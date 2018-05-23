from flask import Flask, render_template, request, url_for, send_file
from selenium import webdriver
from bs4 import BeautifulSoup

import os
import requests
from utils.extract import *
from utils.voc_grading_and_detail import *
from utils.create_pdf import *
from utils.grammar_pattern import *
from utils.week9 import *
from readability import Document

from utils.create_pdf.create_flashcard import *
from utils.create_pdf.create_article import *
from utils.create_pdf.create_wordlist import *
from utils.create_pdf.create_grammar import *
from utils.create_pdf.stylesheet import *

from pprint import pprint
import json

app = Flask(__name__ )

stylesheet = stylesheet() # pdf stylesheet
egp = load_egp() # grammar pattern

if not os.path.exists('download'):
    os.makedirs('download')
    
week9 = open('utils/week9.txt', 'r')
week9 = week9.readline()
week9 = eval(week9)

@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html')

@app.route('/handle_data', methods=['POST', 'GET'])
def handle_data():
    url = request.form['url']
    user_level = request.form['user_level']
    response = requests.get(url)

    doc = Document(remove_a(response.text))
    title = doc.short_title()
    publish_date = getPublishDate(url)
    content = clean_content(doc.summary())

    grade, wordlist = voc_grading_and_detail(content, user_level)
    pats = find_pattern(content, week9)
    # pprint(json.dumps(pats))
    # create pdf
    new = create_article(title, content, stylesheet, user_level, grade, 'download/'+title+'_article.pdf')
    create_wordlist(wordlist, 'download/'+title+'_wordlist.pdf')
    # create_grammar(title, original, stylesheet, egp, 'download/'+title+'_grammar.pdf')
    
    return render_template('format.html', title=title, publish_date=publish_date, content=new,
                           user_level=user_level, grade=grade)

@app.route('/download/<filename>', methods=['GET'])
def return_reformatted(filename):
    try:
        return send_file('download/'+filename)# , as_attachment=True
    except Exception as e:
        return str(e)

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
    app.run(host='0.0.0.0', port=int("9487"), debug=False)