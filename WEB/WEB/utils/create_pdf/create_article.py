import re
from collections import defaultdict, Counter
from utils.senttag import parse_sent
from nltk.corpus import wordnet as wn
# build level word list
data_pwd = './utils/data/levelWord/'
A_word = set(open(data_pwd + 'A_level_word.txt', 'r').readlines()[0].split())
B_word = set(open(data_pwd + 'B_level_word.txt', 'r').readlines()[0].split())
C_word = set(open(data_pwd + 'C_level_word.txt', 'r').readlines()[0].split())
def wordnet(word_, pos, posSet):
    target = set()
    if pos == 'V': syn = wn.synsets(word_, pos=wn.VERB)
    elif pos == 'N': syn = wn.synsets(word_, pos=wn.NOUN)
    else: syn = wn.synsets(word_, pos=wn.ADJ)
    for item in syn:
        for word in item.lemma_names():
            if not (word == word_ or not bool(re.match('^[a-zA-Z]+$', word)) or word in target): 
                if word in posSet: return word
                target.add(word)
    return ''

def create_article(title, user_level, content, youtube, verb, noun, adj):
    new_content = []
    dangerous_word = set(['word', 'span', 'data', 'pos', 'datum', 'level', 'lemma']) # prevent replace loop
    for c in content:
        _type, text = c[0], c[1]
        if _type == 'p':
            new_para = ''
            for sent in text:
                if youtube and not text.index(sent):
                    new_para += sent+' '
                    continue
                parse = parse_sent(sent)
                words = [ x[0] for x in parse ]
                lemma_words = [ x[1] for x in parse ]
                pos_parse = [ x[2] for x in parse ]
                pos_num = 0
                word_set = set()
                for word in words:
                    level = 'C'
                    lemma_word = lemma_words[pos_num]
                    if lemma_word in word_set | dangerous_word:
                        pos_num += 1
                        continue
                    word_set.add(lemma_word)
                    pos = pos_parse[pos_num]
                    clean_word = re.sub('[^a-zA-Z0-9]$', '', re.sub('^[^a-zA-Z0-9]', '', word)) # "word, word?
                    if not re.match('\w', clean_word):
                        pos_num += 1
                        continue # --
                    pos_tag = ''
                    dataWord = ''
                    if pos.startswith('VB'):
                        pos_tag = 'V'
                        if lemma_word in verb: dataWord = lemma_word
                        else: dataWord = wordnet(lemma_word, pos_tag, verb)
                    elif pos.startswith('NN'):
                        pos_tag = 'N'
                        if lemma_word in noun: dataWord = lemma_word
                        else: dataWord = wordnet(lemma_word, pos_tag, noun)
                    elif pos.startswith('J'):
                        pos_tag = 'ADJ'
                        if lemma_word in adj: dataWord = lemma_word
                        else: dataWord = wordnet(lemma_word, pos_tag, adj)
                    
                    if lemma_word in A_word: level = 'A'
                    elif lemma_word in B_word: level = 'B'
                    
                    if dataWord:
                        bf_tag = bb_tag = ""
                        r = re.findall('(?P<f>\W)'+clean_word+'(?P<b>\W)', sent) # cookies
                        for f, b in r:
                            sent = sent.replace(f+clean_word+b, f+'<span data-lemma="'+lemma_word+'" data-word="'+dataWord+'" data-level="'+level+'" data-pos="'+pos_tag+'">'+bf_tag+clean_word+bb_tag+'</span>'+b)
                        if not r: # About ...
                            r = re.match(clean_word, sent)
                            sent = sent.replace(clean_word, '<span data-lemma="'+lemma_word+'" data-word="'+dataWord+'" data-level="'+level+'" data-pos="'+pos_tag+'">'+bf_tag+clean_word+bb_tag+'</span>')
                    pos_num += 1
                new_para += sent+' '
            new_content.append(['p', new_para])
        elif _type == 'h2': new_content.append(['h2', ' '.join(text)])
        elif _type == 'h3': new_content.append(['h3', ' '.join(text)])
    return new_content