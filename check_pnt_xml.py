import docx
from lxml import etree

doc = docx.Document(r"D:\Professional Training I template-1 (1).docx")

sec0 = doc.sections[0]
pnt = sec0._sectPr.find(docx.oxml.ns.qn('w:pgNumType'))
print("Sec 0 pgNumType XML:", etree.tostring(pnt, encoding='utf-8').decode('utf-8'))
