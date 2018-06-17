from flask import Flask, render_template, request, url_for, send_file, jsonify
from selenium import webdriver
from bs4 import BeautifulSoup

import os
import requests
from collections import defaultdict

from utils.extract import *
from utils.voc_grading_and_detail import *
from utils.create_pdf import *
from utils.grammar_pattern import *
from utils.autoFindPattern import *
from readability import Document

from utils.create_pdf.create_flashcard import *
from utils.create_pdf.create_article import *
from utils.create_pdf.create_wordlist import *
from utils.create_pdf.create_grammar import *
from utils.create_pdf.stylesheet import *

from pprint import pprint
import json

# Read statistics file
file = open('utils/data/autoFindPattern/statistics(V).txt', 'r')
dictV =  defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: 0)))) 
for line in file:
    word, subDict = line.split('\t')
    dictV[word] = eval(subDict)
file.close()

file = open('utils/data/autoFindPattern/statistics(N).txt', 'r')
dictN =  defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: 0)))) 
for line in file:
    word, subDict = line.split('\t')
    dictN[word] = eval(subDict)
file.close()

file = open('utils/data/autoFindPattern/statistics(Adj).txt', 'r')
dictAdj =  defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: 0)))) 
for line in file:
    word, subDict = line.split('\t')
    dictAdj[word] = eval(subDict)
file.close()


# read statistic key
file = open('utils/data/autoFindPattern/keys(V).txt', 'r')
verb_set = eval(file.readline())
file.close()

file = open('utils/data/autoFindPattern/keys(N).txt', 'r')
noun_set = eval(file.readline())
file.close()

file = open('utils/data/autoFindPattern/keys(Adj).txt', 'r')
adj_set = eval(file.readline())
file.close()

app = Flask(__name__ )

stylesheet = stylesheet() # pdf stylesheet
# egp = load_egp() # grammar pattern

if not os.path.exists('download'):
    os.makedirs('download')

@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html')
    #return render_template('format.html', title=title, publish_date=publish_date, content=new, user_level=user_level, grade=grade)

@app.route('/handle_data', methods=['POST', 'GET'])
def handle_data():
    url = request.form['url']
    #user_level = request.form['user_level']
    response = requests.get(url)

    doc = Document(remove_a(response.text))
    title = doc.short_title()
    publish_date = getPublishDate(url)
    content = clean_content(doc.summary())
    #grade, wordlist = voc_grading_and_detail(content, user_level)
    #patterns = findGramPat(content)
    # create pdf
    #new = create_article(title, content, stylesheet, grade, 'download/'+title+'_article.pdf')
    #print(content)
    new = create_article(title, content, stylesheet,  'download/'+title+'_article.pdf', verb_set, noun_set, adj_set)
    #create_wordlist(wordlist, patterns, 'download/'+title+'_wordlist.pdf')
    # create_grammar(title, original, stylesheet, egp, 'download/'+title+'_grammar.pdf')
    
    
    
    return render_template('format.html', title=title, publish_date=publish_date, content=new) #, user_level=user_level , grade=grade

@app.route('/download/<filename>', methods=['GET'])
def return_reformatted(filename):
    try:
        return send_file('download/'+filename)# , as_attachment=True
    except Exception as e:
        return str(e)

@app.route('/ajax', methods = ['POST'])
def ajax_request():
    word = request.form['word'].lower() if request.form['pos'] != 'x' else request.form['word'].split()[0].lower()  
    pos = [request.form['pos']] if request.form['pos'] != 'x' else [p.upper() for p in request.form['word'].split()[1:]]
    
    targetList = []
    targetDict = dict()
    if 'V' in pos: targetList.append(dictV)
    if 'N' in pos: targetList.append(dictN)
    if 'ADJ' in pos: targetList.append(dictAdj)
    if not targetList: targetList = [dictV, dictN, dictAdj]
    
    result = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: ''))) # result[pos][pat][obj] = highlight
    patPair = defaultdict(lambda: []) # patPair[pos] = [pat...]
    objs = defaultdict(lambda: defaultdict(lambda: [])) # objs[pos][pat] = [obj...]
        
    for targetDict in targetList:
        if targetDict == dictV: mark = 'V'
        elif targetDict == dictN: mark = 'N'
        else: mark = 'ADJ'
            
        if word in targetDict.keys():
            patPair[mark] = sorted(targetDict[word].keys(), key=lambda x: -(int(x.rsplit('%', 1)[1])))[:5]
            subpatPair = patPair[mark]
            
            sub_objs = defaultdict(lambda: []) # objs[pat] = [obj...]

            for pat in subpatPair:
                objPair = sorted(targetDict[word][pat].keys(), key=lambda x: -(int(x.rsplit('%', 1)[1])))[:3]
                # move '-' to list end
                emptys = [pair for pair in objPair if pair.startswith('-')]
                for empty in emptys:
                    objPair.remove(empty)
                    objPair += [empty]

                sub_objs[pat] += objPair
                for obj in objPair:
                    highlight = sorted(targetDict[word][pat][obj].items(), key=lambda x: -x[1])[0]
                    result[mark][pat][obj] = highlight[0]
                    
            objs[mark] = sub_objs
                      
    return jsonify(table=result, patterns=patPair, objs=objs)

#static url cache buster
@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)   

if __name__ == '__main__':
    app.run(debug=False)
    #app.run(host='0.0.0.0', port=int("9487"), debug=False)