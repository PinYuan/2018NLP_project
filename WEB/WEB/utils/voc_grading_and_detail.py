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

TF = defaultdict(lambda: defaultdict(lambda: 0))
DF = defaultdict(lambda: [])
DL = defaultdict(lambda: 0)

json_data = [json.load(open(data_pwd + chr(letter) + '.json')) for letter in range(ord('A'), ord('B')+1)][0]

def voc_grading_and_detail(content, user_level):
    voc_grading = {}
    wordlist = []
    
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
        for word in json_data:
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
                    if voc_grading[Lword].startswith(user_level) == True:
                        one_word_dict.clear()
                        one_word_dict = w['poses'][poses_index]['senses'][senses_index]
                        one_word_dict['part of speech'] = w['poses'][poses_index]['pos']
                        one_word_dict['origin sentence'] = sentence
                        wordlist.append((word, one_word_dict))
                else:
                    voc_grading[Lword] = w['poses'][0]['senses'][0]['level']
                    if voc_grading[Lword].startswith(user_level) == True:
                        one_word_dict.clear()
                        one_word_dict = w['poses'][0]['senses'][0]
                        one_word_dict['part of speech'] = w['poses'][0]['pos']
                        one_word_dict['origin sentence'] = sentence
                        wordlist.append((word, one_word_dict))
    

    trainlesk()
    for c in content:
        paragragh = [word for sentence in c[1] for word in cut_word(sentence) ]
        for sentence in c[1]:
            sentence_list = cut_word(sentence)
            for word in sentence_list:
                add_word(word, paragragh, sentence)
            
    return voc_grading, wordlist