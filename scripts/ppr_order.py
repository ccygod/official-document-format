"""Shared WordprocessingML paragraph-property ordering rules."""
from lxml import etree

W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
q=lambda tag:'{'+W+'}'+tag

PPR_ORDER={name:index for index,name in enumerate((
    'pStyle','keepNext','keepLines','pageBreakBefore','framePr','widowControl',
    'numPr','suppressLineNumbers','pBdr','shd','tabs','suppressAutoHyphens',
    'kinsoku','wordWrap','overflowPunct','topLinePunct','autoSpaceDE','autoSpaceDN',
    'bidi','adjustRightInd','snapToGrid','spacing','ind','contextualSpacing',
    'mirrorInd','suppressOverlap','jc','textDirection','textAlignment',
    'textboxTightWrap','outlineLvl','divId','cnfStyle','rPr','sectPr','pPrChange'
))}

def canonicalize_ppr(ppr):
    children=list(ppr)
    for child in children: ppr.remove(child)
    for original_index,child in sorted(enumerate(children), key=lambda item:(PPR_ORDER.get(etree.QName(item[1]).localname,1000),item[0])):
        ppr.append(child)
    return ppr

def ppr_order_failures(roots):
    failures=[]
    for root,label in roots:
        for index,ppr in enumerate(root.xpath('.//w:pPr',namespaces={'w':W})):
            ranks=[PPR_ORDER[etree.QName(child).localname] for child in ppr if etree.QName(child).localname in PPR_ORDER]
            if ranks != sorted(ranks): failures.append(f'{label} paragraph property order {index} is invalid')
    return failures
