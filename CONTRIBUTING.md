# Contributing

Thanks for helping improve artifact-template-wps. Start with a concrete failure: the request, a minimal synthetic input, expected behavior, and what actually happened. Keep private documents out of issues.

Use Python 3.10+ and install `requirements.txt`. Run `python3 -m unittest discover -s scripts -p 'test_*.py' -v`. Add a regression that checks behavior before changing a script. For instruction changes, include a realistic example and say what you reviewed; a structural PASS does not establish writing quality or rendering.

Small, focused pull requests are easiest to review. Preserve explicit user constraints and existing template structures. Cite external ideas and never bundle proprietary fonts or customer material.
