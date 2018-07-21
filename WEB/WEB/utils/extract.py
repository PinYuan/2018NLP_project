import re
import nltk
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


def remove_a(text):
    text = re.sub('(?is)<a.*?>', '', text)
    text = re.sub('(?is)</a>', '', text)
    return text
    
def clean_content(content, inputType):
    def sentence_tokenize(content):
        sent_text = nltk.sent_tokenize(content) 
        sent_text = [sent for sent in sent_text if '\n' not in sent]
        #sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', content)
        return sent_text
    
    if inputType == 'url':
        content = re.sub('(?is)<div.*?>', '<div>', content)
        content = re.sub('(?is)<p.*?>', '<p>', content)
        content = re.sub('(?is)<a.*?>', '<a>', content)

        content = content[17:-20] # remove html, body, div 
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
    elif inputType == 'youtube':
        v_id = content[0]
        content = content[1].split('\n\n')
        new_content = list()
        for p in content:
            if '-->' in p:
                p = p.split(' --> ', 1)
                time = p[0].strip().split(':')
                time[-1] = time[-1].split('.')[0]
                while len(time) < 3:
                    time.insert(0, 0)
                p[0] = '<a class="youtube-time" href="https://youtu.be/'+v_id+'?t='+time[-3]+'h'+time[-2]+'m'+time[-1]+'s" target="blank_">'+p[0].split('.', 1)[0]+'</a>'
                p[1] = p[1].split('\n', 1)[1].replace('\n', ' ')
                new_content.append(['p', p]) # .split('\n', 1)[-1].replace('\n', ' ')
    else:
        content = content.split('\n')
        new_content = []
        for p in content:
            p = p.strip()
            if p:
                temp = ['p', [p]]
            new_content.append(temp)
    return new_content