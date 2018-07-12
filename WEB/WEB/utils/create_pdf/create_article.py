import re
from collections import defaultdict, Counter
from utils.senttag import parse_sent

# build level word list
data_pwd = './utils/data/levelWord/'
A_word = set(open(data_pwd + 'A_level_word.txt', 'r').readlines()[0].split())
B_word = set(open(data_pwd + 'B_level_word.txt', 'r').readlines()[0].split())
C_word = set(open(data_pwd + 'C_level_word.txt', 'r').readlines()[0].split())
    
def create_article(title, user_level, content, filename, verb, noun, adj):
    new_content = []
    word_list = set(['word', 'span', 'data', 'pos', 'u', 'datum']) # prevent replace loop
    for c in content:
        _type, text = c[0], c[1]
        if _type == 'p':
            new_para = ''
            for sent in text:
                parse = parse_sent(sent)
                words = [y for x in parse[0] for y in x.split()]
                lemma_words = [y for x in parse[1] for y in x.split()]
                pos_parse = [y for x in parse[2] for y in x.split()]
                pos_num = 0
                word_set = set()
                for word in words:
                    level = 'C'
                    lemma_word = lemma_words[pos_num]
                    if lemma_word in word_set:
                        pos_num += 1
                        continue
                    word_set.add(lemma_word)
                    pos = pos_parse[pos_num]
                    clean_word = re.sub('[^a-zA-Z0-9]$', '', re.sub('^[^a-zA-Z0-9]', '', word)) # "word, word?
                    if not re.match('\w', clean_word):
                        pos_num += 1
                        continue # --
                    pos_tag = ''
                    if pos.startswith('VB') and lemma_word in verb: pos_tag = 'V'
                    elif pos.startswith('NN') and lemma_word in noun: pos_tag = 'N'
                    elif pos.startswith('J') and lemma_word in adj: pos_tag = 'ADJ'
                    
                    if lemma_word in A_word: level = 'A'
                    elif lemma_word in B_word: level = 'B'
                    
                    if pos_tag:
                        word_list.add(lemma_word)
                        bf_tag = bb_tag = ""
                        r = re.findall('(?P<f>\W)'+clean_word+'(?P<b>\W)', sent) # cookies
                        for f, b in r:
                            sent = sent.replace(f+clean_word+b, f+'<span data-word="'+lemma_word+'" data-level="'+level+'" data-pos="'+pos_tag+'">'+bf_tag+clean_word+bb_tag+'</span>'+b)
                        if not r: # About ...
                            r = re.match(clean_word, sent)
                            sent = sent.replace(clean_word, '<span data-word="'+lemma_word+'" data-level="'+level+'" data-pos="'+pos_tag+'">'+bf_tag+clean_word+bb_tag+'</span>')
                    pos_num += 1
                new_para += sent+' '
            new_content.append(['p', new_para])
        elif _type == 'h2': new_content.append(['h2', text])
        elif _type == 'h3': new_content.append(['h3', text])

    return new_content