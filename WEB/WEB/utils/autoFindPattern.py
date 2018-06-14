import sys
from collections import defaultdict
from pprint import pprint
#import numpy
import json
import re 
from utils.senttag import *
#from pgrules import isverbpat

pgPreps = 'around|round|in_favor_of|_|about|after|against|among|as|at|between|behind|by|for|from|in|into|of|on|upon|over|through|to|toward|off|on|across|towarV in favour of    ruled in favour ofV in favour of    ruled in favour ofds|with'.split('|')
otherPreps ='out|down'.split('|')
verbpat = ('V; V n; V ord; V oneself; V adj; V prep; V adv; V -ing; V to v; V to-inf; V n to-inf; V v; V that; V wh; V wh to v; V quote; '+\
              'V so; V not; V as if; V as though; V someway; V together; V as adj; V as to wh; V by amount; '+\
              'V amount; V by -ing; V in favour of n; V in favour of ing; V n in favour of n; V n in favour of ing; V n n; V n adj; V n -ing; V n to v; V n v n; V n that; '+\
              'V n wh; V n wh to v; V n v-ed; V n someway; V n to n; V n with n'+\
              'V n as adj; V n into -ing; V adv; V and v; V ord prep; V n ord prep; '+\
              'V it; V it v-ed; V it n; V it prep;V it adv; V it inf; V prep it; V it as n; V it as adj; '+\
              'V it over n; V it to n; V n for it; V by -ing; V pl-n; V adj among pl-n; V among pl-n; V between pl-n;'+\
              'V to n; V way prep; V way adv').split('; ')
verbpat += ['V %s n' % prep for prep in pgPreps]+['V n %s n' % prep for prep in verbpat]
specialpat = ('V with quote; V n with quote; V pl-n with together; V n with adv').split('; ')
verbpat += specialpat
verbpat += [pat.replace('V ', 'V-ed ') for pat in verbpat] # ???
nounpat = ('N for n to v; N from n that; N from n to v; N from n for n; N in favor of; N in favour of; '+\
            'N of amount; N of n as n; N of n to n; N of n with n; N on n for n; N on n to v'+\
            'N that; N to v; N to n that; N to n to v; N with n for n; N with n that; N with n to v').split('; ')
nounpat += nounpat + ['N %s -ing' % prep for prep in pgPreps ]
nounpat += nounpat + ['ADJ %s n' % prep for prep in pgPreps if prep != 'of']+ ['N %s -ing' % prep for prep in pgPreps]
adjpat = ('ADJ adj; ADJ and adj; ADJ as to wh; '+\
        'ADJ enough; ADJ enough for n; ADJ enough for n to v; ADJ enough n; '+\
        'ADJ enough n for n; ADJ enough n for n to v; ADJ enough n that; ADJ enough to v; '+\
        'ADJ for n to v; ADJ from n to n; ADJ in color; ADJ -ing; '+\
        'ADJ in n as n; ADJ in n from n; ADJ in n to n; ADJ in n with n; ADJ in n as n; ADJ n for n'+\
        'ADJ n to v; ADJ on n for n; ADJ on n to v; ADJ that; ADJ to v; ADJ to n for n; ADJ n for -ing'+\
        'ADJ wh; ADJ on n for n; ADJ on n to v; ADJ that; ADJ to v; ADJ to n for n; ADJ n for -ing').split('; ')
adjpat += [ 'ADJ %s n'%prep for prep in pgPreps ]
pgPatterns = verbpat + adjpat + nounpat

defaultMap = {'NP': 'n', 'VP': 'v', 'JP': 'adj', 'ADJP': 'adj', 'ADVP': 'adv', 'SBAR': 'that' }
selfWords = ['oneself', 'myself', 'ourselves', 'yourself', 'himself', 'herself', 'themselves']
pronOBJ = ['me', 'us', 'you', 'him', 'them']

ordWords = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'nineth', 'tenth']
ordPats = re.compile('[0-9]+st|[0-9]+nd|[0-9]+rd|[0-9]+th')
reservedWords = ['so', 'not', 'though', 'if', 'someway', 'together', 'favor', 'favour', 'as if', 'as though']
whWords = ['who', 'what', 'when', 'where', 'whether', 'how', 'why', 'if']
semiReservedWords = dict([(word, 'prep')for word in pgPreps] + [('it', 'n'), ('way', 'n')])

collinsVerb = defaultdict(lambda: [])
with open('utils/data/autoFindPattern/_collins.pgv.txt', 'r') as verbFile:
    for line in verbFile:
        verb, pat = line.strip('\n').split('\t')
        collinsVerb[verb] += [pat]

def ispat(pat):
    return re.sub('\([a-zA-Z\- ]+\)', '', pat).strip() in pgPatterns 
            
maxDegree = 9

def sentence_to_ngram(words, lemmas, tags, chunks): #start from 1 
    return [ (k, k+degree) for k in range(0, len(words)) for degree in range(2, min(maxDegree, len(words)-k+1)) ]
    #                 if chunks[k][-1] in ['H-VP', 'H-NP', 'H-ADJP'] 
    #                 and chunks[k+degree-1][-1] in ['H-VP', 'H-NP', 'H-ADJP', 'H-ADVP'] ]

mapHead = dict( [('H-NP', 'N'), ('H-VP', 'V'), ('H-ADJP', 'ADJ'), ('H-ADVP', 'ADV'), ('H-VB', 'V')] )
#mapRest = dict( [('H-NP', 'n'), ('H-VP', 'v'), ('H-TO', 'to'), ('H-ADJ', 'adj'), ('H-ADV', 'adv')] )
mapRest = dict( [('VBG', '-ing'), ('VBD', 'v-ed'), ('VBN', 'v-ed'), ('VB', 'v'), ('NN', 'n'), ('NNS', 'n'), ('JJ', 'adj'), ('RB', 'adv')] )
#mapRW = dict( [ pair.split() for pair in reservedWords ] )

def hasTwoObjs(tag, chunk):
    if chunk[-1] != 'H-NP': return False
    return (len(tag) > 1 and tag[0] in pronOBJ) or (len(tag) > 1 and 'DT' in tag[1:] and tag[0] != 'PRP$') # his every(DT) word

def hasVInf(tag, chunk): # V inf in onegram
    if chunk[-1] not in ['H-VP', 'H-VB']: return False
    _len = len(tag)
    for i in range(0, _len-1):
        if tag[i:i+2] in [['VB', 'VB'], ['VBP', 'VB'], ['VBZ', 'VB']]: return True
    return False

def isPlural(word, tag):
    if tag[-1] == 'NNS' or tag[-1] == 'NNPS': return True
    if tag[-1] == 'PRP' and word[-1] in ['we', 'they', 'us', 'you', 'them']: return True
    if tag.count('NN') > 1 or tag.count('PRP') > 1: return True
    return False

def chunk_to_element(words, lemmas, tags, chunks, i, isHead):
    #print ('***', i, words[i], lemmas[i], tags[i], chunks[i], isHead, tags[i][-1] == 'RP' and tags[i-1][-1][:2] == 'VB')
    if isHead:                                                    #   return [mapHead[chunks[i][-1]]] if chunks[i][-1] in mapHead else '*'
        if tags[i][-1] in ['VBN'] and chunks[i][-1] in ['H-VP', 'H-VB']: # control passive 應該不要有V的可能 
            if lemmas[i][0] == 'have' and lemmas[i][1] != 'been': return [mapHead[chunks[i][-1]]] if chunks[i][-1] in mapHead else '*'
                
            if words[i][0] in ['are', 'were']: return ['pl-n be V-ed'] 
            elif words[i][0] in ['is', 'was']: return ['n be V-ed'] 
            else: return ['n be V-ed'] # n covered with
        return [mapHead[chunks[i][-1]]] if chunks[i][-1] in mapHead else '*'

    #print(words, lemmas, tags, chunks)
    if lemmas[i][0] == 'favour' and words[i-1][-1]=='in' and\
       words[i+1][0]=='of':                                          return ['favour']
    if tags[i][-1] == 'RP' and tags[i-1][-1][:2] == 'VB':            return ['_']
   
    if lemmas[i][0] in whWords:                                     return ['wh'] # tags[i][0][0]=='W' and 
    if lemmas[i][0] in reservedWords:                                return [lemmas[i][0]]
    if lemmas[i][-1] in selfWords:                                   return ['oneself']
    if chunks[i][0] == 'H-ADJP' and \
       (lemmas[i][0] in ordWords or re.match(ordPats, lemmas[i][0])):return ['ord']

    if tags[i][0] == 'CD' or \
        re.match('[0-9]*\.*[0-9]+', lemmas[i][-1]):                  return ['amount', 'n']#return ['amount', 'pl-n', 'n'] if tags[i][-1] == 'NNS' else ['amount', 'n']# 1 point
    
    if hasTwoObjs(tags[i], chunks[i]):                               return ['n n', 'n']
    
    if '"' in lemmas[i]:                                             return ['quote']
    if isPlural(words[i], tags[i]):                                  return ['pl-n', 'n']
    
    if lemmas[i][-1] in semiReservedWords.keys():                    return [lemmas[i][-1], semiReservedWords[lemmas[i][-1]]]
    
    if tags[i][-1] in mapRest:                                       return [mapRest[tags[i][-1]]]
    if tags[i][-1][:2] in mapRest:                                   return [mapRest[tags[i][-1][:2]]]
    
    if chunks[i][-1] in mapHead:                                     return [mapHead[chunks[i][-1]].lower()]
    if lemmas[i][-1] in pgPreps:                                     return [lemmas[i][-1]] # won't enter

    return [lemmas[i][-1]]

def simplifyPat(pat):
    pat_split = pat.split()
    if pat in ['V ,', 'V .']: return 'V'
    if len(pat_split) == 3 and pat_split[0] == 'V' and pat_split[1] in pgPreps and pat_split[1] != 'by' and\
        pat_split[2] == 'ing': # V prep n->(-ing) / V by -ing 
        return ' '.join(pat_split[0:2]+['n'])
    if 'to v' in pat: return pat.replace('to v', 'to-inf') # to v -> to-inf
    # if pat == 'V v': return 'V inf'
    return pat.replace(' _', '').replace('_', ' ').replace('  ', ' ')
    # return 'V' if pat == 'V ,' or pat == 'V .' else pat.replace(' _', '').replace('_', ' ').replace('  ', ' ')

def modifySpecial(pat):
    if 'quote' in pat:
        if pat == ['quote', 'n', 'V', 'n'] or pat == ['V', 'n', 'quote']: return ['V', 'n', 'with', 'quote']
        elif pat == ['quote', 'V'] or pat == ['V', 'quote']: return ['V', 'with', 'quote']
        else: return pat
    else:
        for p in specialpat[2:]:
            p = p.replace('with', '').split()
            if pat == ' '.join(p): return ' '.join()
            elif pat == ' '.join([p[0], p[2], p[1]]): return ' '.join([p[0], p[2], p[1]]) 
            
        return pat
    
def passive2active(pat): # is done
    passives = [('pl-n be V-ed', ['V', 'pl-n']), ('n be V-ed', ['V', 'n'])]
    pat_len = len(pat)
    
    for passive in passives:
        if passive[0] in pat:
            if pat_len == 1: return passive[1] 
            elif pat_len == 2:
                may_prep = pat[1] # was taught to!! 
                if may_prep in pgPreps: pat.remove(may_prep) # is comprised of -> comprise
                else: return None # correct misclassify passive
                pat.remove(passive[0])
                if may_prep == 'to':
                    return passive[1] + pat
                else:
                    return passive[1] + pat + [' (be V-ed %s)' % (may_prep)] if may_prep != 'by' else passive[1] + pat
            else: return pat
    return pat
    
def genPat_choose(pat):
    # generate semi[[V], [it, n], [as, prep]] -> [[V, it, as], [V, it, prep], ...] and passive to actice
    pats = [[]]
    for p in pat: # gen combination
        pats = [ _list + [word] for word in p for _list in pats ]
    #print(pats)
    pats = [modifySpecial(pat) for pat in pats]
    pats = [passive2active(pat) for pat in pats]
    pats = [simplifyPat(' '.join(pat)) for pat in pats if pat != None]
    
    pats = [_pat for _pat in pats if ispat(_pat)]
    
    return pats if pats else '' # pats[0]
    
def ngram_to_pat(words, lemmas, tags, chunks, start, end):
    pat, doneHead = [], False
    for i in range(start, end):
        isHead = tags[i][-1][0] in ['V', 'N', 'J'] and not doneHead
        pat.append( chunk_to_element(words, lemmas, tags, chunks, i, isHead) ) # list for combination
        if isHead: doneHead = True

    pat = genPat_choose(pat)
   
    return pat

def ngram_to_head(words, lemmas, tags, chunks, start, end):
    for i in range(start, end):
        if tags[i][-1][0] in 'V' and tags[i+1][-1]=='RP':  return lemmas[i][-1].upper()+ ('_'+lemmas[i+1][-1].upper())
        if tags[i][-1][0] in ['V', 'J', 'N']:  return lemmas[i][-1].upper()
    
def oneGram(words, lemmas, tags, chunks):
    _len = len(words)
    for i in range(0, _len):
        if hasVInf(tags[i], chunks[i]): 
            #print('\t', 'V inf', [' '.join(words[i])])
            result.append('V inf')
        if tags[i][-1] in ['VBN'] and chunks[i][-1] in ['H-VP', 'H-VB'] and words[i+1] in [',', '.', '!']:
            #print('\t', 'V n', [' '.join(words[i])])
            result.append('V n')

def findGramPat(content):
    result = [] # (word, pat(V n), article sent, word to hightlight)
    for tag, sentences in content:
        if tag == 'p':
            for sent in sentences:
                parse = parse_sent(sent)
                parse = [ [y.split() for y in x]  for x in parse ]

                for start, end in sentence_to_ngram(*parse):
                    key = parse[1][start][0]
                    pats = ngram_to_pat(*parse, start, end)
                    for pat in pats:
                        if pat and pat in collinsVerb[key]:
                            highlight = ' '.join([' '.join(x) for x in parse[0][start:end]])
                            #result[ngram_to_head(*parse, start, end)+'-'+head][pat].append(' '.join([' '.join(x) for x in parse[0][start:end] ]))
                            #print('\t', pat, [' '.join([' '.join(x) for x in parse[0][start:end] ])])
                            result.append((key, pat, sent, highlight))
    return result
