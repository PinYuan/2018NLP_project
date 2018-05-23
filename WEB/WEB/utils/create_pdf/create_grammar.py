# grammar
from utils.grammar_pattern import *

def create_grammar(title, content, stylesheet, egp, filename):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    parts = []
    
    parts.append(Paragraph(title, stylesheet['title']))
   
    for sentences in content:
        if not (sentences.startswith('[h2]') or sentences.startswith('[h3]')):
            sententces = sentences.replace('? ', '?\t')
            sententces = sentences.replace('! ', '?\t')
            sentences = sentences.replace('...', '')
            sentences = sentences.replace('"', '')
            
            sen_pat = re.compile('\. [A-Z]')
            break_sens = []
            if sen_pat.search(sentences)!= None:
                break_sens = sen_pat.findall(sentences)
                upperWords = []
                for _break in break_sens:
                    upperWord = _break[2]
                    sentences = sentences.replace(_break, '.\t'+upperWord)
                
            sentences = sentences.split('\t')

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
       
