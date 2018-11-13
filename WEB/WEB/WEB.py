from flask import Flask, render_template, request, url_for, send_file, jsonify
from bs4 import BeautifulSoup

import os
import requests
from collections import defaultdict
import json

from utils.extract import *
from utils.create_pdf import *
from readability import Document

from utils.create_pdf.create_article import *
from utils.GenerateMCQ import *        # import quiz generation

import youtube_dl

dictWord = eval(open('utils/data/autoFindPattern/GPs.txt', 'r').read())
phraseV = eval(open('utils/data/autoFindPattern/phrase.txt', 'r').read())

# read translation
TRANS = eval(open('utils/data/final TRANS.txt', 'r').read()) # tran[pos][word] = [translation...]

app = Flask(__name__ )
import datetime

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

if not os.path.exists('download'):
    os.makedirs('download')

@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html')
    #return render_template('format.html', title=title, publish_date=publish_date, content=new, user_level=user_level, grade=grade)

def store(*values):  # store value from handle_data() and pass to quiz() 
    store.values = values or store.values
    return store.values    
   
@app.route('/handle_data', methods=['POST', 'GET'])
def handle_data():
    def cleancap(raw_cap):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_cap)
        tmp = cleantext.split('\n')
        cap = list()
        pre = ''
        for line in tmp:
            if line.replace(' ', '') and line != pre:
                if '-->' in line: cap.append('')
                else: pre = line
                cap.append(line)
        tmp = set()
        for idx in range(len(cap)):
            if '-->' in cap[idx] and (idx >= len(cap)-2 or '-->' in cap[idx+2]):
                tmp.add(idx)
                tmp.add(idx+1)
        final = list()
        for idx in range(len(cap)):
            if idx not in tmp: final.append(cap[idx])
        return '\n'.join(final)
    
    user_level = request.form['user_level']
    title = ''
    publish_date = ''
    text = request.form['text']
    if (text.startswith('http://www.youtube.com')
        or text.startswith('http://youtube.com') 
        or text.startswith('http://youtu.be') 
        or text.startswith('https://www.youtube.com') 
        or text.startswith('https://youtube.com') 
        or text.startswith('https://youtu.be')):
        ydl_opts = {
            'writesubtitles': True,
            'writeautomaticsub': True,
            'skip_download': True, # We just want to extract the info
            'outtmpl': 'download/target' # file_path/target
        }
        file = ''
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([text])
            dirPath = "download"
            fileList = os.listdir(dirPath)
            if 'target.en.vtt' in fileList:
                file = cleancap(open('download/target.en.vtt').read())
            else:
                file = 'There is no english substitle in this video!'
            for fileName in fileList:
                if os.path.isfile(os.path.join(dirPath, fileName)): os.remove(os.path.join(dirPath, fileName))
        v_id = text.split('=')[-1]
        content = [v_id, file]
        type_ = 'youtube'
        r = requests.get(text)
        if r.status_code < 400:
            title = BeautifulSoup(r.text, 'html.parser').find('title').text
            publish_date = BeautifulSoup(r.text, 'html.parser').find('meta', itemprop="datePublished")['content']
    elif text.startswith('http://') or text.startswith('https://'):
        response = requests.get(text, headers=headers)
        doc = Document(remove_sometag(response.text))
        title = doc.short_title()
        publish_date = getPublishDate(response.content.decode('UTF-8'))
        content = doc.summary()
        type_ = 'url'
    else:
        content = text
        type_ = 'text'
            
    content = clean_content(content, type_)
    new,pure_text,vocab_dict = create_article(title, user_level, content, type_=='youtube', \
                         set(dictWord['V'].keys()), set(dictWord['N'].keys()), set(dictWord['ADJ'].keys()))
    store(pure_text,vocab_dict,user_level)
    return render_template('format.html', title=title, publish_date=publish_date, \
                           user_level=user_level, content=new) 

@app.route('/index2', methods=['POST', 'GET'])
def quiz():
    pure_text,vocab_dict,user_level = store() 
    if(len(pure_text) == 0):
        con = "\nplease paste link or text"
        return render_template('format2.html', title="quiz", publish_date="2018.8.11", \
                           user_level="B", content=con)    
    tmpDict = extractVocList2(vocab_dict,user_level,10)  #extract vocabulary list 
    o = shuffle_vocab_dict(tmpDict,10)  # randomly pick up n vocabularies
    questionDict, orderDict, pro_num, category = generateMCQ(o, 0, user_level,pure_text)
    type_ = "text"
    q = merge_two_dicts(questionDict,orderDict)
    vocab = transformFormat(q, type_ == 'youtube', \
                            set(dictWord['V'].keys()), set(dictWord['N'].keys()), set(dictWord['ADJ'].keys()))
    generateWeb(questionDict,orderDict,pro_num,category,vocab,pure_text)  # generate web file(html+js)
    file = open("./templates/index2.html", "r", encoding="utf-8")  
    con = file.read() # read html and js file and write into format2.html
    return render_template('format2.html', title="quiz", publish_date="2018.8.11", \
                           user_level="B", content=con)                        
                           
@app.route('/download/<filename>', methods=['GET'])
def return_reformatted(filename):
    try:
        return send_file('download/'+filename)# , as_attachment=True
    except Exception as e:
        return str(e)

@app.route('/ajax', methods = ['POST'])
def ajax_request():
    word = request.form['word'].lower() if request.form['pos'] != 'x' else request.form['word'].split()[0].lower()  
    
    if request.form['pos'] != 'x': # click
        poses = [request.form['pos']]
    elif len(request.form['word'].split()) == 1: # search
        poses = ['V', 'N', 'ADJ']
    else:
        poses = [p.upper() for p in request.form['word'].split()[1:]]
    
    finalWord = word
    # patternTable[pos] = [(pat, colls, (en, ch, source)), ...] 
    patternTable = defaultdict(lambda: [])
    # phraseTable[pos][phrase] = [pat, (colls, (en, ch, source)), ...] 
    phraseTable = defaultdict(lambda: defaultdict(lambda: []))
    # phraseOrder = [phrase...]
    phraseOrder = []
    # trans[type][pos] = [translation]
    trans = defaultdict(lambda: defaultdict(lambda: list())) 
    
    for pos in poses:
        if pos == 'null': continue
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
        if finalWord in set(TRANS['pat'][pos].keys()):
            trans['pat'][pos] = TRANS['pat'][pos][finalWord]
        else:
            trans['pat'][pos] = []
    
    if not patternTable.keys():
        for pos in poses:
            if pos == 'null': continue
            if finalWord == word or not finalWord: finalWord = wordnet(word, pos, set(dictWord[pos].keys()))
            if finalWord and finalWord != word:
                if finalWord in dictWord[pos].keys():
                    for pat, colls, examp in dictWord[pos][finalWord][:5]:
                        patternTable[pos] += [(pat, ', '.join(colls[:3]), examp)]
                        
                if pos == 'V' and finalWord in phraseV.keys():
                    # 前面以過濾過phrase至多3個, pat已用std過濾
                    phraseOrder = sorted(phraseV[finalWord].keys(), key=lambda x: -int(x.rsplit('%', 1)[1]))
                    for phrase in phraseOrder:
                        for pat, colls, examp in phraseV[finalWord][phrase]:
                            phraseTable[pos][phrase] += [(pat, ', '.join(colls[:3]), examp)]
                            phrase = phrase.split('%')[0]
                            if phrase in TRANS['phrase'][pos].keys():
                                trans['phrase'][phrase] = TRANS['phrase'][pos][phrase]
                            else:
                                trans['phrase'][phrase] = []
                if finalWord in set(TRANS['pat'][pos].keys()):
                    trans['pat'][pos] = TRANS['pat'][pos][finalWord]
                else:
                    trans['pat'][pos] = []
                        
                        
                        
    return jsonify(finalWord=finalWord, \
                   change=(finalWord!=word), \
                   patternTable=patternTable, \
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