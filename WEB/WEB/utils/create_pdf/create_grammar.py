# grammar
from utils.grammar_pattern import *
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether

from reportlab.lib.enums import TA_LEFT, TA_CENTER

def create_grammar(title, content, stylesheet, egp, filename):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    parts = []
    
    parts.append(Paragraph(title, stylesheet['title']))
   
    for tag, sentences in content:
        if tag not in ['h2', 'h3']:
            for sentence in sentences:
                if sentence == '': continue
                pat = isPattern(sentence, egp)
                
                level, cando, examps = egp[pat]
                examps = [examp.strip() for examp in examps.split('|||')]
                
                parts.append(Paragraph(pat+' '+level, stylesheet['h3']))
                parts.append(Paragraph(cando, stylesheet['default']))
                for examp in examps:
                    parts.append(Paragraph(examp, stylesheet['default']))
    doc.build(parts)
       

       
