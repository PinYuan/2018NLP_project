import re
import json
from utils.lemmatization import *
from collections import defaultdict, Counter
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import wordnet
import nltk, random
from pprint import pprint

lmtzr = WordNetLemmatizer()
data_pwd = '../../crawler/EVP/data/'
hiFreq_pwd = './utils/data/'

TF = defaultdict(lambda: defaultdict(lambda: 0))
DF = defaultdict(lambda: [])
DL = defaultdict(lambda: 0)

json_data = [json.load(open(data_pwd + chr(letter) + '.json')) for letter in range(ord('A'), ord('Z')+1)]
hifreq = [ word.replace('\n', '') for word in open(hiFreq_pwd + '60000_word_freq.txt') ]

def voc_grading_and_detail(content, user_level):
    voc_grading = {}
    wordlist = list()
    word_exist = []
    
    def cut_word(text):
        text = text.replace(',', ' ,',)
        text = text.replace('\'s', ' \'s')
        text = text.replace('.', ' .')
        text = text.split()
        return text
    
    def get_wordnet_pos(tag): # conveet part-of-speech to wordnet form
        if tag.startswith('adj'): return wordnet.ADJ
        elif tag.startswith('v'): return wordnet.VERB
        elif tag.startswith('n'): return wordnet.NOUN
        elif tag.startswith('adv'): return wordnet.ADV
        return ''

    def words(text): return re.findall(r'\w+', text.lower())

    def isHead(head, word, tag):
        try:
            return lmtzr.lemmatize(word, tag) == head
        except:
            return False

    # ['poses'] -> ['pos'] : pos
    #           -> ['senses'] -> ['dict_examp'] : dict_examp
    #                         -> ['lear_examp'] : lear_examp
    #                         -> ['level'] : level
    #                         -> ['sense'] : sense
    # ['word'] : word
    def trainlesk():
        for start_letter in json_data:
            for word in start_letter:
                head = word['word']
                poses_index = 0
                for poses in word['poses']:
                    senses_index = 0
                    for senses in poses['senses']:
                        wncat = (head, poses_index, senses_index)
                        senseDef = senses['dict_examp'] + senses['lear_examp'] + senses['sense']
                        pos = poses['pos']
                        for word2 in words(senseDef):
                            if word2 != head and not isHead(head, word2, get_wordnet_pos(pos)):
                                TF[word2][wncat] += 1
                                DF[word2] += [] if wncat in DF[word2] else [wncat]
                                DL[wncat] += 1
                        senses_index += 1
                    poses_index += 1
            
    def leskOverlap(word_id, senseDef):
        wnidCount = list()
        for word in senseDef:
            for wncat, tf in TF[word].items():
                if wncat[0] == word_id:
                    wnidCount.append((wncat, tf, word, len(DF[word])+1))
        res = sorted( [ (wnid, tf*int(1000/df)) for wnid, tf, word, df in wnidCount], key = lambda x: -x[1])[:3]
        if not res: return 'Not found'
        counter = Counter()
        for wncat, tfidf in res: counter[wncat] += tfidf/DL[wncat]
        return counter.most_common(1)[0][0]    
    
    def add_word(Lword, paragragh, sentence):
        word = lemmatization(Lword)
        if re.match('[^a-zA-Z]', word) != None: # 's ...
            return
        if Lword in voc_grading: # alreadly exist 
            return
        initial_letter = word[0].upper()
        specific_letter_json_data = json.load(open(data_pwd + initial_letter + '.json'))
        one_word_dict = dict()
        for w in specific_letter_json_data:
            if w['word'] == word:
                t = leskOverlap(word, paragragh)
                if t != 'Not found':
                    wnid = t[0]
                    poses_index = int(t[1])
                    senses_index = int(t[2])
                    voc_grading[Lword] = w['poses'][poses_index]['senses'][senses_index]['level']
                    if voc_grading[Lword].startswith(user_level) == True :
                        one_word_dict.clear()
                        one_word_dict = w['poses'][poses_index]['senses'][senses_index]
                        one_word_dict['part of speech'] = w['poses'][poses_index]['pos']
                        one_word_dict['origin sentence'] = sentence
                        if word not in word_exist:
                            wordlist.append((word, one_word_dict))
                            word_exist.append(word)
                else:
                    voc_grading[Lword] = w['poses'][0]['senses'][0]['level']
                    if voc_grading[Lword].startswith(user_level) == True:
                        one_word_dict.clear()
                        one_word_dict = w['poses'][0]['senses'][0]
                        one_word_dict['part of speech'] = w['poses'][0]['pos']
                        one_word_dict['origin sentence'] = sentence
                        if word not in word_exist:
                            wordlist.append((word, one_word_dict))
                            word_exist.append(word)
    def filter_wordlist_A():
        word_amount_needed = 15
        if len(wordlist) <= word_amount_needed: return wordlist

        lvl_2_wordlist = [ (i, wordlist[i]) for i in range(len(wordlist)) if wordlist[i][1]['level'] == user_level + '2']
    #    lvl_2_wordlist = [ item for item in wordlist if item[1]['level'] == user_level + '2']
        if len(lvl_2_wordlist) == word_amount_needed: return [ item[1] for item in lvl_2_wordlist ]
        elif len(lvl_2_wordlist) < word_amount_needed:
            word_amount_needed -= len(lvl_2_wordlist)
            other_word = [ (i, wordlist[i]) for i in range(len(wordlist)) if wordlist[i][1]['level'] == user_level + '1']
            other_word = sorted(other_word, key = lambda x: len(x[1][0]), reverse = True)[: word_amount_needed]
            return  [item[1] for item in sorted(lvl_2_wordlist+other_word, key = lambda x: x[0])]

        word_hifre = [ (i, lvl_2_wordlist[i][1]) for i in range(len(lvl_2_wordlist)) if lvl_2_wordlist[i][1][0] in hifreq ]

        len_wordlist = len(word_hifre)

        if len_wordlist < word_amount_needed:
            not_hifre_wordlist = [ (i, lvl_2_wordlist[i][1]) for i in range(len(lvl_2_wordlist)) if lvl_2_wordlist[i][1][0] not in hifreq ]
            not_hifre_wordlist = sorted(not_hifre_wordlist, key = lambda x: len(x[1][0]), reverse = True)[: word_amount_needed - len_wordlist]
            return [item[1] for item in sorted(word_hifre+not_hifre_wordlist, key = lambda x: x[0])]

    #    V_ADJ_ADV = sorted(V_ADJ_ADV, key = lenofitem, reverse = True)[: 15]
    #    V_ADJ_ADV = sorted(V_ADJ_ADV, key = index, reverse = True)[: 11]
        _V_ADJ_ADV = [ (i, word_hifre[i][1]) for i in range(len_wordlist) if word_hifre[i][1][1]['part of speech'] not in ['verb', 'adjective', 'adverb']]
        _V_ADJ_ADV = sorted(_V_ADJ_ADV, key = lambda x: len(x[1][0]), reverse = True)[:6]
        _V_ADJ_ADV = sorted(_V_ADJ_ADV, key = lambda x: hifreq.index(x[1][0]), reverse = True)[:3]
        word_amount_needed -= len(_V_ADJ_ADV)
#        pprint(_V_ADJ_ADV)
        V_ADJ_ADV = [ (i, word_hifre[i][1]) for i in range(len_wordlist) if word_hifre[i][1][1]['part of speech'] in ['verb', 'adjective', 'adverb']]
        V_ADJ_ADV = sorted(V_ADJ_ADV, key = lambda x: len(x[1][0]), reverse = True)[: int(1.4*word_amount_needed)]
        V_ADJ_ADV = sorted(V_ADJ_ADV, key = lambda x: hifreq.index(x[1][0]), reverse = True)[: word_amount_needed]
#        pprint('**************' + str(word_amount_needed))
#        pprint(V_ADJ_ADV)
        return [item[1] for item in sorted(V_ADJ_ADV+_V_ADJ_ADV, key = lambda x: x[0])]
    
    def filter_wordlist_B():
        word_amount_needed = 15
        if len(wordlist) <= word_amount_needed: return wordlist

        lvl_2_wordlist = [ (i, wordlist[i]) for i in range(len(wordlist)) if wordlist[i][1]['level'] == user_level + '2']
    #    lvl_2_wordlist = [ item for item in wordlist if item[1]['level'] == user_level + '2']
    ###    if len(lvl_2_wordlist) <= 10: go to 
    ###    elif len(lvl_2_wordlist) < word_amount_needed:
    ###        word_amount_needed -= len(lvl_2_wordlist)
    ###        other_word = [ (i, wordlist[i]) for i in range(len(wordlist)) if wordlist[i][1]['level'] == user_level + '1']
    ###        other_word = sorted(other_word, key = lambda x: len(x[1][0]), reverse = True)[: word_amount_needed]
    ###        return  [item[1] for item in sorted(lvl_2_wordlist+other_word, key = lambda x: x[0])]

        word_hifre = [ (i, lvl_2_wordlist[i][1]) for i in range(len(lvl_2_wordlist)) if lvl_2_wordlist[i][1][0] in hifreq ]

        len_wordlist = len(word_hifre)

        if len_wordlist < word_amount_needed:
            not_hifre_wordlist = [ (i, lvl_2_wordlist[i][1]) for i in range(len(lvl_2_wordlist)) if lvl_2_wordlist[i][1][0] not in hifreq ]
            not_hifre_wordlist = sorted(not_hifre_wordlist, key = lambda x: len(x[1][0]), reverse = True)[: word_amount_needed - len_wordlist]
            return [item[1] for item in sorted(word_hifre+not_hifre_wordlist, key = lambda x: x[0])]

    #    V_ADJ_ADV = sorted(V_ADJ_ADV, key = lenofitem, reverse = True)[: 15]
    #    V_ADJ_ADV = sorted(V_ADJ_ADV, key = index, reverse = True)[: 11]
        _V_ADJ_ADV = [ (i, word_hifre[i][1]) for i in range(len_wordlist) if word_hifre[i][1][1]['part of speech'] not in ['verb', 'adjective', 'adverb']]
    #    _V_ADJ_ADV = sorted(_V_ADJ_ADV, key = lambda x: len(x[1][0]), reverse = True)[:6]
        _V_ADJ_ADV = sorted(_V_ADJ_ADV, key = lambda x: hifreq.index(x[1][0]), reverse = True)[:2]

        word_amount_needed -= len(_V_ADJ_ADV)
#        pprint('**************' + str(len(_V_ADJ_ADV)))
#        pprint(_V_ADJ_ADV)
        V_ADJ_ADV = [ (i, word_hifre[i][1]) for i in range(len_wordlist) if word_hifre[i][1][1]['part of speech'] in ['verb', 'adjective', 'adverb']]
    #    V_ADJ_ADV = sorted(V_ADJ_ADV, key = lambda x: len(x[1][0]), reverse = True)[: int(1.4*word_amount_needed)]
        V_ADJ_ADV = sorted(V_ADJ_ADV, key = lambda x: hifreq.index(x[1][0]), reverse = True)[: word_amount_needed-3]
#        pprint('**************' + str(len(V_ADJ_ADV)))
#        pprint(V_ADJ_ADV)

        longest_word = [ (i, wordlist[i]) for i in range(len(wordlist)) if wordlist[i] not in V_ADJ_ADV + _V_ADJ_ADV]
        _long_V_ADJ_ADV = [ (i, longest_word[i][1]) for i in range(len(longest_word)) if longest_word[i][1][1]['part of speech'] not in ['verb', 'adjective', 'adverb']]
        _long_V_ADJ_ADV = sorted(_long_V_ADJ_ADV, key = lambda x: len(x[1][0]), reverse = True)[:1]
#        pprint('**************' + str(len(_long_V_ADJ_ADV)))
#        pprint(_long_V_ADJ_ADV)

        long_V_ADJ_ADV = [ (i, longest_word[i][1]) for i in range(len(longest_word)) if longest_word[i][1][1]['part of speech'] in ['verb', 'adjective', 'adverb']]
        long_V_ADJ_ADV = sorted(long_V_ADJ_ADV, key = lambda x: len(x[1][0]), reverse = True)[:2]
#        pprint('**************' + str(len(long_V_ADJ_ADV)))
#        pprint(long_V_ADJ_ADV)

        return [item[1] for item in sorted(V_ADJ_ADV+_V_ADJ_ADV, key = lambda x: x[0])]
    
    def filter_wordlist_C():
        word_amount_needed = 15
        if len(wordlist) <= word_amount_needed: return wordlist

        lvl_2_wordlist = [ (i, wordlist[i]) for i in range(len(wordlist)) if wordlist[i][1]['level'] == user_level + '2']
    #    lvl_2_wordlist = [ item for item in wordlist if item[1]['level'] == user_level + '2']
        '''
        if len(lvl_2_wordlist) == word_amount_needed: return [ item[1] for item in lvl_2_wordlist ]
        elif len(lvl_2_wordlist) < word_amount_needed:
            word_amount_needed -= len(lvl_2_wordlist)
            other_word = [ (i, wordlist[i]) for i in range(len(wordlist)) if wordlist[i][1]['level'] == user_level + '1']
            other_word = sorted(other_word, key = lambda x: len(x[1][0]), reverse = True)[: word_amount_needed]
            return  [item[1] for item in sorted(lvl_2_wordlist+other_word, key = lambda x: x[0])]
        '''

        word_hifre = [ (i, lvl_2_wordlist[i][1]) for i in range(len(lvl_2_wordlist)) if lvl_2_wordlist[i][1][0] in hifreq ]

        len_wordlist = len(word_hifre)

        '''
        if len_wordlist < word_amount_needed:
            not_hifre_wordlist = [ (i, lvl_2_wordlist[i][1]) for i in range(len(lvl_2_wordlist)) if lvl_2_wordlist[i][1][0] not in hifreq ]
            not_hifre_wordlist = sorted(not_hifre_wordlist, key = lambda x: len(x[1][0]), reverse = True)[: word_amount_needed - len_wordlist]
            return [item[1] for item in sorted(word_hifre+not_hifre_wordlist, key = lambda x: x[0])]
        '''

    #    V_ADJ_ADV = sorted(V_ADJ_ADV, key = lenofitem, reverse = True)[: 15]
    #    V_ADJ_ADV = sorted(V_ADJ_ADV, key = index, reverse = True)[: 11]
        _V_ADJ_ADV = [ (i, word_hifre[i][1]) for i in range(len_wordlist) if word_hifre[i][1][1]['part of speech'] not in ['verb', 'adjective', 'adverb']]
    #    _V_ADJ_ADV = sorted(_V_ADJ_ADV, key = lambda x: len(x[1][0]), reverse = True)[:6]
        _V_ADJ_ADV = sorted(_V_ADJ_ADV, key = lambda x: hifreq.index(x[1][0]), reverse = True)[:2]

        word_amount_needed -= len(_V_ADJ_ADV)
#        pprint('**************' + str(len(_V_ADJ_ADV)))
#        pprint(_V_ADJ_ADV)
        V_ADJ_ADV = [ (i, word_hifre[i][1]) for i in range(len_wordlist) if word_hifre[i][1][1]['part of speech'] in ['verb', 'adjective', 'adverb']]
    #    V_ADJ_ADV = sorted(V_ADJ_ADV, key = lambda x: len(x[1][0]), reverse = True)[: int(1.4*word_amount_needed)]
        V_ADJ_ADV = sorted(V_ADJ_ADV, key = lambda x: hifreq.index(x[1][0]), reverse = True)[: word_amount_needed-3]
#        pprint('**************' + str(len(V_ADJ_ADV)))
#        pprint(V_ADJ_ADV)

        longest_word = [ (i, wordlist[i]) for i in range(len(wordlist)) if wordlist[i] not in V_ADJ_ADV + _V_ADJ_ADV]
        _long_V_ADJ_ADV = [ (i, longest_word[i][1]) for i in range(len(longest_word)) if longest_word[i][1][1]['part of speech'] not in ['verb', 'adjective', 'adverb']]
        _long_V_ADJ_ADV = sorted(_long_V_ADJ_ADV, key = lambda x: len(x[1][0]), reverse = True)[:1]
#        pprint('**************' + str(len(_long_V_ADJ_ADV)))
#        pprint(_long_V_ADJ_ADV)

        long_V_ADJ_ADV = [ (i, longest_word[i][1]) for i in range(len(longest_word)) if longest_word[i][1][1]['part of speech'] in ['verb', 'adjective', 'adverb']]
        long_V_ADJ_ADV = sorted(long_V_ADJ_ADV, key = lambda x: len(x[1][0]), reverse = True)[:2]
#        pprint('**************' + str(len(long_V_ADJ_ADV)))
#        pprint(long_V_ADJ_ADV)

        return [item[1] for item in sorted(V_ADJ_ADV+_V_ADJ_ADV, key = lambda x: x[0])]

    def filter_wordlist():
        if user_level == 'A': return filter_wordlist_A()
        elif user_level == 'B': return filter_wordlist_B()
        elif user_level == 'C': return filter_wordlist_C()
        else: 
            print('************************wrong user_level:' + 'user_level')
            return []
            
        
    trainlesk()
    for c in content:
        paragragh = [word for sentence in c[1] for word in cut_word(sentence) ]
        for sentence in c[1]:
            sentence_list = cut_word(sentence)
            for word in sentence_list:
                add_word(word, sentence, sentence)
    #print(wordlist)
    return_wordlist = filter_wordlist()
    voc_grading = [ item[0] for item in return_wordlist ]
    return voc_grading, return_wordlist