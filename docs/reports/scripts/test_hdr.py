import docx
from docx.oxml import parse_xml

doc = docx.Document()
section = doc.sections[0]
header = section.header
p = header.paragraphs[0]
p.text = 'Literature Survey'
pPr = p._p.get_or_add_pPr()
pBdr = parse_xml('<w:pBdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:bottom w:val="single" w:sz="6" w:space="4" w:color="888888"/></w:pBdr>')
pPr.append(pBdr)
doc.save('test_header.docx')
print('Header bottom border added successfully!')
