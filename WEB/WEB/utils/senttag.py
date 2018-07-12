#!/usr/bin/env python 
# -*- coding: utf-8 -*-

from itertools import groupby, product
import re, sys
import geniatagger
import glob
from pprint import pprint

tagger = geniatagger.GeniaTagger('utils/geniatagger-3.0.2/geniatagger')

def parseV_to_H(info):
    def bio_to_iho(BIO):
        res, oldPhrase = [], '***'
        for iToken, token in enumerate(BIO):
            phrase = token[(token.index('-')+1) if '-' in token else 0:]
            res = (['O'] if phrase=='O' else ['H-'+phrase if phrase != oldPhrase else 'I-'+phrase])+res
            oldPhrase = phrase
        return res

    origin = list()
    lemma = list()
    POS = list()
    BIO = list()
    for e in info:
        o,l,P,B,_ = e
        origin.append(o); lemma.append(l); POS.append(P); BIO.append(B)
    HIO = bio_to_iho(BIO[::-1])
    return '%s\t%s\t%s\t%s' % (' '.join(origin),' '.join(lemma),' '.join(POS),' '.join(HIO))

def IHO_to_phrases(line):
    words, lemmas, tags, chunks = line.strip().split('\t')
    words, lemmas, tags, chunks = \
        words.split(), ( (lemmas[0] if lemmas[:2] == 'I ' else lemmas[0].lower())+lemmas[1:] ).split(), tags.split(), chunks.split()
    res, ix = [], 0
    SEP = ' '
    
    for iy in range(len(words)-1):
        if lemmas[iy+1] == 'to' and chunks[iy] == 'I-VP':   # v of v to-inf
            chunks[iy] = 'H-VB'                             
        elif lemmas[iy] == 'to' and chunks[iy] == 'I-VP':   # to of to-inf
            chunks[iy] = 'H-TO'; tags[iy] = 'TO'
        elif chunks[iy] and chunks[iy][0] in ['H','O']: # or tags[iy] in ['TO'] or tags[iy+1] in ['WDT']:
            pass
        else:
            continue
        
        res += [ ( SEP.join(words[ix:iy+1]), SEP.join(lemmas[ix:iy+1]), SEP.join(tags[ix:iy+1]), SEP.join(chunks[ix:iy+1]) ) ]
        ix = iy+1

    res += [ (words[-1], lemmas[-1], tags[-1], chunks[-1]) ]
    return res
    
def parse_sent(sent):
    sent = sent.replace(' — ', ' ')
    parse = tagger.parse(sent)
    parse = parseV_to_H(parse)
    parse = IHO_to_phrases(parse)

    words, lemmas, tags, chunks = zip(*parse)
    return [words, lemmas, tags, chunks]


