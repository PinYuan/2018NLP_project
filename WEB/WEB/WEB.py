from flask import Flask, render_template, request, url_for, send_file, jsonify
from selenium import webdriver
from bs4 import BeautifulSoup

import os
import requests
from collections import defaultdict
import json

from utils.extract import *
from utils.create_pdf import *
from readability import Document

from utils.create_pdf.create_article import *

dictWord = eval(open('utils/data/autoFindPattern/wordPG.txt', 'r').read())
phraseV = eval(open('utils/data/autoFindPattern/phrase(V).txt', 'r').read())

# read translation
TRANS = eval(open('utils/data/final TRANS.txt', 'r').read()) # tran[pos][word] = [translation...]

app = Flask(__name__ )
import datetime
# egp = load_egp() # grammar pattern

if not os.path.exists('download'):
    os.makedirs('download')

@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html')
    #return render_template('format.html', title=title, publish_date=publish_date, content=new, user_level=user_level, grade=grade)

@app.route('/handle_data', methods=['POST', 'GET'])
def handle_data():
    user_level = request.form['user_level']
    url = ''
    title = ''
    publish_date = ''
    try:
        url = request.form['url']
        if (url.startswith('http://www.youtube.com') 
            or url.startswith('http://youtube.com') 
            or url.startswith('http://youtu.be') 
            or url.startswith('https://www.youtube.com') 
            or url.startswith('https://youtube.com') 
            or url.startswith('https://youtu.be')):
            v_id = url.split('=')[-1]
            url = "https://www.youtube.com/api/timedtext?name=&fmt=vtt&lang=en&v=%s" % (v_id)
            r = requests.get(url)
            if r.status_code >= 400:content = "There's no English caption."
            else: content = [v_id, r.text]
            type_ = 'youtube'
            url = "https://www.youtube.com/watch?v=%s" % (v_id)
            r = requests.get(url)
            if r.status_code < 400:
                title = BeautifulSoup(r.text, 'html.parser').find('title').text
                publish_date = BeautifulSoup(r.text, 'html.parser').find('meta', itemprop="datePublished")['content']
        else:
            response = requests.get(url)
            doc = Document(response.content)
            title = doc.short_title()
            publish_date = getPublishDate(response.content.decode('UTF-8'))
            content = doc.summary()
            type_ = 'url'
    except:
        text = request.form['text']
        content = text
        type_ = 'text'
        
    content = clean_content(content, type_)
    new = create_article(title, user_level, content, type_=='youtube', \
                         set(dictWord['V'].keys()), set(dictWord['N'].keys()), set(dictWord['ADJ'].keys()))
    
    return render_template('format.html', title=title, publish_date=publish_date, \
                           user_level=user_level, content=new) 

@app.route('/download/<filename>', methods=['GET'])
def return_reformatted(filename):
    try:
        return send_file('download/'+filename)# , as_attachment=True
    except Exception as e:
        return str(e)

@app.route('/ajax', methods = ['POST'])
def ajax_request():
    word = request.form['word'].lower() if request.form['pos'] != 'x' else request.form['word'].split()[0].lower()  
    poses = ['V', 'N', 'ADJ'] if len(request.form['word'].split())==1 else [p.upper() for p in request.form['word'].split()[1:]]
    
    # patternTable[pos] = [(pat, colls, (en, ch, source)), ...] 
    patternTable = defaultdict(lambda: [])
    # phraseTable[pos][phrase] = [pat, (colls, (en, ch, source)), ...] 
    phraseTable = defaultdict(lambda: defaultdict(lambda: []))
    # phraseOrder = [phrase...]
    phraseOrder = []
    # trans[type][pos] = [translation]
    trans = defaultdict(lambda: defaultdict(lambda: list())) 
    
    for pos in poses:
        if word in dictWord[pos].keys():
            # TODO須處理個數，以後可能動態
            for pat, colls, examp in dictWord[pos][word][:5]:
                patternTable[pos] += [(pat, ', '.join(colls[:3]), examp)]

        if pos == 'V' and word in phraseV.keys():
            # 前面以過濾過phrase至多3個, pat已用std過濾
            phraseOrder = sorted(phraseV[word].keys(), key=lambda x: -int(x.rsplit('%', 1)[1]))
            for phrase in phraseOrder:
                for pat, colls, examp in phraseV[word][phrase]:
                    phraseTable[pos][phrase] += [(pat, ', '.join(colls[:3]), examp)]
                    phrase = phrase.split('%')[0]
                    if phrase in TRANS['phrase'][pos].keys():
                        trans['phrase'][phrase] = TRANS['phrase'][pos][phrase]
                    else:
                        trans['phrase'][phrase] = []

        if word in set(TRANS['pat'][pos].keys()):
            trans['pat'][pos] = TRANS['pat'][pos][word]
    return jsonify(patternTable=patternTable, \
                   phraseTable=phraseTable, phraseOrder=phraseOrder, \
                   trans=trans)

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
#     app.run(debug=False)
    app.run(host='0.0.0.0', port=int("5487"), debug=False)