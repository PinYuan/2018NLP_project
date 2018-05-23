from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether

from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.colors import (
    black,
    purple,
    white,
    yellow
)

import re
from utils.lemmatization import lemmatization

def create_article(title, content, stylesheet, user_level, grade, filename):  
    doc = SimpleDocTemplate(filename, pagesize=letter)
    parts = []
    
    spacer = KeepTogether(Spacer(0, 0.25*inch))
    
    parts.append(Paragraph(title, stylesheet['title']))
    
    para_num = 1
    new_content = []
    for c in content:
        type = c[0]
        text = c[1]
        if type == 'p':
            new_para = ''
            for sent in text:
                words = sent.split()
                for word in words:
                    clean_word = re.sub('^[^a-zA-Z0-9]', '', word) # "word
                    clean_word = re.sub('[^a-zA-Z0-9]$', '', clean_word) # word?
                    if not re.match('\w', clean_word): continue # --
                    lemma_word = lemmatization(clean_word).lower()
                    
                    if lemma_word in grade and grade[lemma_word].startswith(user_level):
                        r = re.search('(?P<f>\W)'+clean_word+'(?P<b>\W)', sent) # cookies
                        if r:
                            f = r.group('f')
                            b = r.group('b')
                            sent = sent.replace(f+clean_word+b, f+'<u><b>'+clean_word+'</b></u>'+b)
                        else: # About ...
                            r = re.match(clean_word, sent)
                            sent = sent.replace(clean_word, '<u><b>'+clean_word+'</b></u>')
                new_para += sent+' '
            c[1] = new_para
            parts.append(Paragraph('<font size=14><b>[' + str(para_num) + ']</b></font> '+c[1], stylesheet['default']))
            para_num += 1
            #parts.append(spacer)
        elif type == 'h2':
            #parts.append(spacer)
            parts.append(Paragraph(text, stylesheet['h2']))
        elif type == 'h3':
            #parts.append(spacer)
            parts.append(Paragraph(text, stylesheet['h3']))
        new_content.append(c)
    doc.build(parts)
    return new_content