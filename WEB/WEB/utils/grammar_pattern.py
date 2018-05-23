from collections import defaultdict
from pprint import pprint
import nltk
import re

def load_egp():
    file = open('utils/egp.txt', 'r')
    egp = defaultdict()
    patterns = defaultdict(lambda: [])
    for line in file:
        line = line.split('\t')
        pat, level, cando, examp = line
        egp[pat] = (level, cando, examp)
    file.close()
    
    return egp

def my_tagger(tags):
    new_tags = []
    BE = set(['am', 'is', 'are', 'were', 'was', 'be'])
    BES = set(['am', 'is', 'are'])
    BEP = set(['were', 'was'])
    #BESP = set(['am', 'is', 'are', 'were', 'was', 'be'])
    PP = set(['mine', 'yours', 'his', 'hers', 'ours', 'its', 'theirs'])

    for tag in tags:
        if tag[0] in BEP: new_tag = 'BEP'
        elif tag[0] in BES: new_tag = 'BES'
        elif tag[0] in BE: new_tag = 'BE'
        elif tag[0] in PP: new_tag = 'PP'
        else: new_tag = tag[1]
        new_tags.append(new_tag)
    return new_tags

# todo choose hard one
def isPattern(sentence, egp):
    sen_tokens = nltk.word_tokenize(sentence.lower()); sen_len = len(sen_tokens)
    sen_tags = my_tagger(nltk.pos_tag(sen_tokens))
    
    candidate_word_num = 0
    candidate = []
    for p in egp.keys():
        pat_word_num = len(re.findall('\w+', p))
        
        pat_tokens = p.split(' ')
        pat_len = len(pat_tokens)
        
        if pat_word_num > candidate_word_num:
            
            for sen_index in range(sen_len - pat_len):
                any_word = False # for ...
                any_word_i = 0
                fail = False
                
                for pat_index, t in enumerate(pat_tokens):
                    if fail: break
                    if t == '...':
                        any_word = True
                    else:
                        pattern = re.compile(t)
                        if any_word:
                            while 1:
                                if (t.isupper() and pattern.match(sen_tags[sen_index+pat_index+any_word_i])) or \
                                    (t.islower() and pattern.match(sen_tokens[sen_index+pat_index+any_word_i])): 
                                    any_word = False
                                    break
                                if sen_index+pat_index+any_word_i == sen_len-1:
                                    fail = True 
                                    break
                                any_word_i += 1
                            if fail: break
                        else:
                            if t.isupper():
                                if not pattern.match(sen_tags[sen_index+pat_index+any_word_i]): break
                            else: # lower sign
                                if not pattern.match(sen_tokens[sen_index+pat_index+any_word_i]): break
                    if t is pat_tokens[-1]: 
                        candidate_word_num = pat_word_num
                        candidate = p
    return candidate # random choose
