import re
try: 
    from urllib.request import urlopen, Request
except:
    import urllib
    
def getPublishDate(url):
         # 1 year; 3 month; 5 date; 6 time  (?is)(\d{4}|\d{2})(\-|\/)(\d{1,2})(\-|\/)(\d{1,2})\s?(\d{2}:\d{2}?)
        try:
            response = urlopen(Request(url, headers={'User-Agent': 'Mozilla'}))
        except:
            response = urllib.urlopen(url)
            
        html = response.read().decode('UTF-8')
        
        publishDate = ""
        search_result = re.search("(?is)(\d{4}|\d{2})(\-|\/)(\d{1,2})(\-|\/)(\d{1,2})", html)
        if search_result != None:
            publishDate = search_result.group(1) + '-' + search_result.group(3) + '-' + search_result.group(5)
        return publishDate

# def cut_word(text):
#     text = text.replace(',', ' ,',)
#     text = text.replace('\'s', ' \'s')
#     text = text.replace('.', ' .')
#     text = text.split()
#     return text

# def has_space(text): # s -> has space n -> no space
#     space = []
#     for word in text:
#         if re.match(',|\.|\'s', word) != None:
#             space.append('n')
#         else:
#             space.append('s')
#     return space

def remove_a(text):
    text = re.sub('(?is)<a.*?>', '', text)
    text = re.sub('(?is)</a>', '', text)
    return text
    
def clean_content(content):
    def sentence_tokenize(content):
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', content)
        return sentences
    
    content = re.sub('(?is)<div.*?>', '<div>', content)
    content = re.sub('(?is)<p.*?>', '<p>', content)
    content = re.sub('(?is)<a.*?>', '<a>', content)
    
    content = content[17:-20] # remove html, body, div 
#    matches = re.findall('(?is)<div>.*?</div>', content)
#     for match in matches:
#         sub = '<p>' + re.sub('<div>|<p>|</div>|</p>', '', match) + '</p>'
#         content = re.sub('(?is)<div>.*?</div>', sub, content, count=1) # because sometimes use match fail 
    content = re.sub('<p>', '[p]', content)
    content = re.sub('<h2>', '[h2]', content)
    content = re.sub('<h3>', '[h3]', content)
    content = re.sub('<.*?>', '', content)

    content = re.split('\[p\]', content)
    
    new_content = []
    for p in content[1:]:
        p = p.strip()
        if p.startswith('[h2]'):
            p = p.replace('[h2]', '')
            temp = ['h2', p]
        elif p.startswith('[h3]'):
            p = p.replace('[h3]', '')
            temp = ['h3', p]
        else:
            temp = ['p', list(filter(None, sentence_tokenize(p)))]
            
        new_content.append(temp)
    return new_content