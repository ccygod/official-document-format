"""格式包加载、校验和字号比例计算。"""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROFILE_DIR = ROOT / "config" / "format-profiles"
REQUIRED_ROLES = {"body", "heading_1", "heading_2", "heading_3", "heading_4", "heading_5", "title", "caption"}


class FormatProfileError(ValueError):
    pass


def list_profiles() -> list[dict]:
    result = []
    for path in sorted(PROFILE_DIR.glob("*.json")):
        if path.name == "README.md":
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        result.append(data)
    return result


def load_profile(profile_id: str) -> dict:
    path = PROFILE_DIR / f"{profile_id}.json"
    if not path.exists():
        names = ", ".join(p["id"] for p in list_profiles())
        raise FormatProfileError(f"未识别格式：{profile_id}。可选格式：{names}")
    profile = json.loads(path.read_text(encoding="utf-8"))
    validate_profile(profile)
    return profile


def validate_profile(profile: dict) -> None:
    if not profile.get("id") or not profile.get("display_name"):
        raise FormatProfileError("格式包缺少id或display_name")
    missing = REQUIRED_ROLES - set(profile.get("fonts", {}))
    if missing:
        raise FormatProfileError(f"格式包缺少字体角色：{sorted(missing)}")
    ratios = profile.get("ratios", {})
    for role in REQUIRED_ROLES:
        value = ratios.get(role)
        if not isinstance(value, (int, float)) or not 0.5 <= value <= 3:
            raise FormatProfileError(f"格式包{profile['id']}的{role}比例非法：{value}")
    line = profile.get("line_multiple")
    if not isinstance(line, (int, float)) or not 0.8 <= line <= 3:
        raise FormatProfileError(f"格式包{profile['id']}的行距比例非法：{line}")


def role_half_points(profile: dict, body_half_points: int, role: str) -> int:
    """将正文半磅值按格式包比例计算为偶数半磅值。"""
    key = role.replace('-', '_')
    value = round(body_half_points * float(profile["ratios"].get(key, 1)))
    return max(2, value)


def profile_summary() -> list[dict]:
    return [{"id": p["id"], "display_name": p["display_name"], "description": p["description"]} for p in list_profiles()]
