from collections import Counter 
import re
from nltk.corpus import wordnet # To get words in dictionary with their parts of speech
from nltk.stem import WordNetLemmatizer # lemmatizes word based on it's parts of speech
from collections import defaultdict, Counter
from pprint import pprint
# index(1st_letter_of_word) - word : lemmetized_word
noun_plus = defaultdict(lambda: defaultdict(lambda: ''))
verb_plus = defaultdict(lambda: defaultdict(lambda: ''))
data_pwd = '../../crawler/EVP/data/'

def build_noun_plus_dict():
    for line in open(data_pwd + 'gec.pattern.noun.txt'):
        lem_word, word_list = line.split('\t', 1)
        word_list = word_list.split()
        for word in word_list:
            noun_plus[word[0]][word] = lem_word
        noun_plus[lem_word[0]][lem_word] = lem_word

def build_verb_plus_dict():
    for line in open(data_pwd + 'gec.pattern.verb.txt'):
        lem_word, word_list = line.split('\t', 1)
        word_list = word_list.split()
        for word in word_list:
            verb_plus[word[0]][word] = lem_word
        verb_plus[lem_word[0]][lem_word] = lem_word

build_noun_plus_dict()
build_verb_plus_dict()

def get_pos(word):
    w_synsets = wordnet.synsets(word)

    pos_counts = Counter()
    pos_counts["n"] = len(  [ item for item in w_synsets if item.pos()=="n"]  )
    if noun_plus[word[0]].get(word) :pos_counts["n"] += 1
    pos_counts["v"] = len(  [ item for item in w_synsets if item.pos()=="v"]  )
    if verb_plus[word[0]].get(word) :pos_counts["v"] += 1
    pos_counts["a"] = len(  [ item for item in w_synsets if item.pos()=="a"]  )
    pos_counts["r"] = len(  [ item for item in w_synsets if item.pos()=="r"]  )
    
    most_common_pos_list = pos_counts.most_common(3)
    # first indexer for getting the top POS from list, second indexer for getting POS from tuple( POS: count )
    return most_common_pos_list[0][0] 

wnl = WordNetLemmatizer()

def lemmatization(word):
    pos = get_pos(word)
    ans = wnl.lemmatize(word, pos)
    if pos == 'n' and noun_plus[word[0]].get(word):
        ans = noun_plus[word[0]][word]
    elif pos == 'v' and verb_plus[word[0]].get(word):
        ans = verb_plus[word[0]][word]
    return ans