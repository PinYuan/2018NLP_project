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
from nltk.corpus import wordnet # To get words in dictionary with their parts of speech
from nltk.stem import WordNetLemmatizer # lemmatizes word based on it's parts of speech
from utils.senttag import parse_sent
from pprint import pprint

data_pwd = './utils/data/levelWord/'
A_word = set()
B_word = set()
C_word = set()

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

def get_level_set():
    f = open(data_pwd + 'A_level_word.txt', 'r')
    words = f.readlines()[0].split()
    for word in words:
        A_word.add(word)
    f.close()
    
    f = open(data_pwd + 'B_level_word.txt', 'r')
    words = f.readlines()[0].split()
    for word in words:
        B_word.add(word)
    f.close()
    
    f = open(data_pwd + 'C_level_word.txt', 'r')
    words = f.readlines()[0].split()
    for word in words:
        C_word.add(word)
    f.close()
    
def create_article(title, user_level, content, stylesheet, filename, verb, noun, adj):
    get_level_set()
    level_set = set()
    _level_set = set()
    if user_level == 'A': 
        level_set = A_word
        _level_set = B_word | C_word
    elif user_level == 'B': 
        level_set = B_word
        _level_set = A_word | C_word
    else:
        level_set = C_word
        _level_set = A_word | B_word
        
    #file = open('_all.txt', 'w')
    
    doc = SimpleDocTemplate(filename, pagesize=letter)
    parts = []
    
    spacer = KeepTogether(Spacer(0, 0.25*inch))
    
    parts.append(Paragraph(title, stylesheet['title']))
    
    para_num = 1
    new_content = []
    word_list = set(['word', 'span', 'data', 'pos', 'u', 'datum'])
    for c in content:
        _type = c[0]
        text = c[1]
        if _type == 'p':
            new_para = ''
            _tag_para = ''
            for sent in text:
                _sent = sent
                parse = parse_sent(sent)
                pos_parse = [y for x in parse[2] for y in x.split()]
                words = [y for x in parse[0] for y in x.split()]
                lemma_words = [y for x in parse[1] for y in x.split()]
                pos_num = 0
                word_set = set()
                for word in words:
                    no_underline = 0
                    lemma_word = lemma_words[pos_num]
                    if lemma_word in word_set:
                        pos_num += 1
                        #no_underline = 1
                        continue
                    word_set.add(lemma_word)
                    pos = pos_parse[pos_num]
                    clean_word = re.sub('^[^a-zA-Z0-9]', '', word) # "word
                    clean_word = re.sub('[^a-zA-Z0-9]$', '', clean_word) # word?
                    if not re.match('\w', clean_word):
                        pos_num += 1
                        continue # --
                    pos_tag = ''
                    if pos.startswith('VB') and lemma_word in verb: pos_tag = 'V'
                    elif pos.startswith('NN') and lemma_word in noun: pos_tag = 'N'
                    elif pos.startswith('J') and lemma_word in adj: pos_tag = 'ADJ'
                    if lemma_word not in level_set:
                        if user_level != 'C' or lemma_word in _level_set:
                            #pos_num += 1
                            no_underline = 1
                            #continue
                    
                    if lemma_word == 'quit': print(pos, pos_tag, no_underline, lemma_word not in word_list, sent)
                    if pos_tag:
                        if lemma_word not in word_list:
                            #file.write(lemma_word + '\t' + pos_tag + '\n')
                            word_list.add(lemma_word)
                            bf_tag = ""
                            bb_tag = ""
                        else:
                            no_underline = 1
                            bf_tag = ""
                            bb_tag = ""
                            #pos_num += 1
                            #continue
                        r = re.findall('(?P<f>\W)'+clean_word+'(?P<b>\W)', sent) # cookies
                        for f, b in r:
                            if f != r[0][0] or no_underline:
                                if lemma_word == 'quit': print( f, r[0][0],'f != r[0][0] or no_underline')
                                sent = sent.replace(f+clean_word+b, f+'<span data-word="'+lemma_word+'" data-pos="'+pos_tag+'">'+bf_tag+clean_word+bb_tag+'</span>'+b)
                                #continue
                            else: 
                                sent = sent.replace(f+clean_word+b, f+'<u><span data-word="'+lemma_word+'" data-pos="'+pos_tag+'">'+bf_tag+clean_word+bb_tag+'</span></u>'+b)
                                _sent = _sent.replace(f+clean_word+b, f+'<span><u>'+bf_tag+clean_word+bb_tag+'</u></span>'+b)
                        if not r: # About ...
                            r = re.match(clean_word, sent)
                            sent = sent.replace(clean_word, '<u><span data-word="'+lemma_word+'" data-pos="'+pos_tag+'">'+bf_tag+clean_word+bb_tag+'</span></u>')
                            _sent = _sent.replace(clean_word, '<span><u>'+bf_tag+clean_word+bb_tag+'</u></span>')
                    pos_num += 1
                new_para += sent+' '
                _tag_para += _sent+' '
            c[1] = _tag_para
            parts.append(Paragraph('<font size=14><b>[' + str(para_num) + ']</b></font> '+c[1], stylesheet['default']))
            para_num += 1
            new_content.append(['p', new_para])
            
        elif _type == 'h2':
            parts.append(Paragraph(text, stylesheet['h2']))
            new_content.append(['h2', text])
        elif _type == 'h3':
            parts.append(Paragraph(text, stylesheet['h3']))
            new_content.append(['h3', text])
        
    doc.build(parts)
    #file.close()
    return new_content