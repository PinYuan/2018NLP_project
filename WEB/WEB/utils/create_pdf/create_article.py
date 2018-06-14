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
from collections import defaultdict, Counter
import re
from nltk.corpus import wordnet # To get words in dictionary with their parts of speech
from nltk.stem import WordNetLemmatizer # lemmatizes word based on it's parts of speech

def get_pos(word):
    w_synsets = wordnet.synsets(word)

    pos_counts = Counter()
    pos_counts["n"] = len(  [ item for item in w_synsets if item.pos()=="n"]  )
    pos_counts["v"] = len(  [ item for item in w_synsets if item.pos()=="v"]  )
    pos_counts["a"] = len(  [ item for item in w_synsets if item.pos()=="a"]  )
    pos_counts["r"] = len(  [ item for item in w_synsets if item.pos()=="r"]  )
    
    most_common_pos_list = pos_counts.most_common(3)
    # first indexer for getting the top POS from list, second indexer for getting POS from tuple( POS: count )
    #print(most_common_pos_list[0])
    if most_common_pos_list[0][1] == 0:
        return None
    return most_common_pos_list[0][0] 

# Read statistics file
#myDict = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: 0))) 
def isVerb():
    verb = set()
    file = open('utils/data/statistics.txt', 'r')
    for line in file:
        word, subDict = line.split('\t')
        #myDict[word] = eval(subDict)
        #verb.add(word)
        if get_pos(word) == 'v':
            verb.add(word)
    file.close()
    return verb


def create_article(title, content, stylesheet, filename):  
    verb = isVerb()
    doc = SimpleDocTemplate(filename, pagesize=letter)
    parts = []
    
    spacer = KeepTogether(Spacer(0, 0.25*inch))
    
    parts.append(Paragraph(title, stylesheet['title']))
    
    para_num = 1
    new_content = []
    for c in content:
        _type = c[0]
        text = c[1]
        if _type == 'p':
            new_para = ''
            for sent in text:
                words = sent.split()
                for word in words:
                    clean_word = re.sub('^[^a-zA-Z0-9]', '', word) # "word
                    clean_word = re.sub('[^a-zA-Z0-9]$', '', clean_word) # word?
                    if not re.match('\w', clean_word): continue # --
                    lemma_word = lemmatization(clean_word).lower()
                    
                    if lemma_word in verb:
                        r = re.search('(?P<f>\W)'+clean_word+'(?P<b>\W)', sent) # cookies
                        if r:
                            f = r.group('f')
                            b = r.group('b')
                            sent = sent.replace(f+clean_word+b, f+'<span><u><b>'+clean_word+'</b></u></span>'+b)
                        else: # About ...
                            r = re.match(clean_word, sent)
                            sent = sent.replace(clean_word, '<span><u><b>'+clean_word+'</b></u></span>')
                new_para += sent+' '
            c[1] = new_para
            parts.append(Paragraph('<font size=14><b>[' + str(para_num) + ']</b></font> '+c[1], stylesheet['default']))
            para_num += 1
            
        elif _type == 'h2':
            parts.append(Paragraph(text, stylesheet['h2']))
        elif _type == 'h3':
            parts.append(Paragraph(text, stylesheet['h3']))
        new_content.append(c)
        
    doc.build(parts)
    return new_content