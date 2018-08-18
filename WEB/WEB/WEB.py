from flask import Flask, render_template, request, url_for, send_file, jsonify,redirect
from selenium import webdriver
from bs4 import BeautifulSoup

import os
from collections import defaultdict
import json

from utils.extract import *
# from utils.create_pdf import *
import requests
#from readability.readability import Document
from readability import Document

from utils.create_pdf.create_article import *
from utils.GenerateMCQ import *

import youtube_dl
#dictWord = eval(open('utils/data/autoFindPattern/wordPG.txt', 'r',encoding="utf-8").read())
#phraseV = eval(open('utils/data/autoFindPattern/phrase(V).txt', 'r',encoding="utf-8").read())
dictWord = eval(open('utils/data/autoFindPattern/wordPG.txt', 'r').read())
phraseV = eval(open('utils/data/autoFindPattern/phrase(V).txt', 'r').read())
# read translation
#TRANS = eval(open('utils/data/final TRANS.txt', 'r',encoding="utf-8").read()) # tran[pos][word] = [translation...]
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
        response = requests.get(text)
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


def store(*values):
    store.values = values or store.values
    return store.values
# @app.route('/index2', methods=['POST', 'GET'])
# def quiz():
#     return render_template('index2.html')

@app.route('/index2', methods=['POST', 'GET'])
def quiz():
    pure_text,vocab_dict,user_level = store()
    tmpDict = extractVocList2(vocab_dict,user_level,10)  #extract vocabulary list
    o = shuffle_vocab_dict(tmpDict,10)  # randomly pick up n vocabularies
    # o = tmpDict
    questionDict, orderDict, pro_num, category = generateMCQ(o, 0,user_level,pure_text)
    type_ = "text"
    q = merge_two_dicts(questionDict,orderDict)
    vocab = transformFormat(q, type_ == 'youtube', \
                            set(dictWord['V'].keys()), set(dictWord['N'].keys()), set(dictWord['ADJ'].keys()))
#     con = """ 	<ul>
# 		<li>
# 			<form><h4>
# <span>One</span><span>would</span><span data-word="expect" data-level="B" data-pos="V">expect</span><span data-word="such" data-level="A" data-pos="ADJ">such</span><span>a</span><span data-word="consensus" data-level="C" data-pos="N">consensus</span><span>to</span><span data-word="be" data-level="A" data-pos="V">be</span><span data-word="back" data-level="A" data-pos="V">backed</span><span>up</span><span>by</span><span>an</span><span>im_____e</span><span data-word="array" data-level="C" data-pos="N">array</span><span>of</span><span data-word="evidence" data-level="B" data-pos="N">evidence</span><span>.</span>
# 			<br><textarea  rows = "1" cols = "20" align = "left" name = cloze0 id = clozeA0></textarea>
# <span><div data-word="impressive" data-level="B" data-pos="ADJ" id = clozeAns0 class = clozeAns0 name = clozeAns0 style = "display:none;">impressive</div></span><br>
# 			</h4></form>
# 		</li>
# 		<li>
# 			<h4><span>I</span><span data-word="have" data-level="A" data-pos="V">have</span><span data-word="learn" data-level="A" data-pos="V">learned</span><span>a</span><span data-word="great" data-level="A" data-pos="ADJ">great</span><span data-word="deal" data-level="B" data-pos="V">deal</span><span>from</span><span>all</span><span>that</span><span>I</span><span data-word="have" data-level="A" data-pos="V">have</span><span data-word="hear" data-level="A" data-pos="V">heard</span><span>in</span><span>the</span><span>_____</span><span data-word="few" data-level="A" data-pos="ADJ">few</span><span data-word="day" data-level="A" data-pos="N">days</span><span>.</span></h4>
# 			<input type ="radio" name ="question0" id = pickup-1 value="1">
# 			<label for=pickup-1 class = ans0>last</label><br>
# 			<input type ="radio" name ="question0" id = pickup-2 value="2">
# 			<label for=pickup-2 class = ans0 data-word="high" data-level="A" data-pos="ADJ" >high</label><br>
# 			<input type ="radio" name ="question0" id = pickup-3 value="3">
# 			<label for=pickup-3 class = ans0>most</label><br>
# 			<input type ="radio" name ="question0" id = pickup-4 value="4">
# 			<label for=pickup-4 class = ans0 data-word="much" data-level="A" data-pos="ADJ" >much</label><br>
# 		</li>
# 		<li>
# 			<h4><span>And</span><span>it</span><span>certainly</span><span data-word="take" data-level="A" data-pos="V">takes</span><span>an</span><span data-word="expert" data-level="B" data-pos="N">expert</span><span>in</span><span data-word="road" data-level="A" data-pos="N">roads</span><span>to</span><span data-word="deal" data-level="B" data-pos="V">deal</span><span>with</span><span>this</span><span data-word="country" data-level="A" data-pos="N">country</span><span>'s</span><span>_____</span><span data-word="topography" data-level="C" data-pos="N">topography</span><span>and</span><span data-word="climate" data-level="B" data-pos="N">climate</span><span>.</span></h4>
# 			<input type ="radio" name ="question1" id = pickup-5 value="1">
# 			<label for=pickup-5 class = ans1>tricky</label><br>
# 			<input type ="radio" name ="question1" id = pickup-6 value="2">
# 			<label for=pickup-6 class = ans1 data-word="varied" data-level="B" data-pos="ADJ" >varied</label><br>
# 			<input type ="radio" name ="question1" id = pickup-7 value="3">
# 			<label for=pickup-7 class = ans1 data-word="squint" data-level="C" data-pos="N" >squint</label><br>
# 			<input type ="radio" name ="question1" id = pickup-8 value="4">
# 			<label for=pickup-8 class = ans1 data-word="racist" data-level="C" data-pos="N" >racist</label><br>
# 		</li>
# 		<li>
# 			<h4><span>Instead</span><span>it</span><span data-word="be" data-level="A" data-pos="V">was</span><span>the</span><span>Colombians</span><span>that</span><span data-word="double" data-level="A" data-pos="V">doubled</span><span>their</span><span data-word="lead" data-level="B" data-pos="N">lead</span><span>with</span><span>70</span><span data-word="minute" data-level="A" data-pos="N">minutes</span><span>on</span><span>the</span><span>clock,</span></h4>
# 			<input type ="radio" name ="question2" id = pickup-9 value="1">
# 			<label for=pickup-9 class = ans2> Japan has since been nothing if not consistent</label><br>
# 			<input type ="radio" name ="question2" id = pickup-10 value="2">
# 			<label for=pickup-10 class = ans2> Radamel Falcao nonchalantly sliding it past Wojciech Szczęsny to score his first ever World Cup goal.</label><br>
# 			<input type ="radio" name ="question2" id = pickup-11 value="3">
# 			<label for=pickup-11 class = ans2> Poland's journey at the Russia 2018 has already effectively come to an end.</label><br>
# 			<input type ="radio" name ="question2" id = pickup-12 value="4">
# 			<label for=pickup-12 class = ans2> who was carried off on a stretcher and replaced by Mateus Uribe after 32 minutes.</label><br>
# 		</li>
# 	</ul>
# 	<button onclick="returnScore2()">Submit</button>
#     """
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
        else:
            trans['pat'][pos] = []
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
    #app.run(debug=False)
    app.run(host='0.0.0.0', port=int("5487"), debug=False)
