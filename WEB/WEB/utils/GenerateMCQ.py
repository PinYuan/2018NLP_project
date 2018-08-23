from collections import defaultdict
import random
import json
from pprint import  pprint
def shuffle_vocab_dict(voc_dict,question_number):
    if(len(voc_dict)<question_number): num = len(voc_dict)
    else: num = question_number
    randict = random.sample(list(voc_dict),num)
    vot = dict()
    for e in randict:
        if (len(e) > 3):
            vot[e] = voc_dict[e]
    return vot
def extractVocList2(vocab_dict,user_level,question_number):
    tmp = defaultdict(lambda:dict())
    for word in vocab_dict:
        lemma,level,pos = vocab_dict[word]
        if(level == user_level and question_number > 0):
            # question_number = question_number -1
            question_number = question_number
            tmp[word]['lemma'] = lemma
            tmp[word]['level'] = level
            tmp[word]['pos'] = pos
    return tmp
def get_spacy_pos(treebank_tag):
    if treebank_tag.startswith('ADJ'):
        return 'j'
    elif treebank_tag.startswith('V'):
        return 'v'
    elif treebank_tag.startswith('N'):
         return 'n'
    elif treebank_tag.startswith('ADV'):
        return 'r'
    elif treebank_tag.startswith('PR'):
        return 'pron'
    elif treebank_tag.startswith('CC'):
        return 'c'
    elif treebank_tag.startswith('ADP'):
        return 'prep'
    elif treebank_tag.startswith('DET'):
        return 'det'
    elif treebank_tag.startswith('PUN'):
        return 'punct'
    else:
        return 'None'
def rebuild_sent(sent, word):
    new_sent = []
    text = sent
    text = text[1:-2]
    temp = text.index(word)
    wordEndIndex = temp + text[temp:].index(' ') - 1
    length = wordEndIndex - temp
    text [temp:wordEndIndex + 1]
    new_sent = text[:temp]+"_____"+text[wordEndIndex+1:]
    # new_sent = text[:temp]+"["+word+"]"+text[wordEndIndex+1:]
    return new_sent
def outLier(wordL, posSet):
    if (len(posSet) == 1 and "n" in posSet):
        if (wordL in posDict):
            outlier = open('outlier.txt', 'a')
            outlier.write("\n" + str(wordL) + "\t" + ("n"))
            outlier.close()
def GDEX(wordL, word_pos):
    CandidateDict = defaultdict(lambda: [])
    ind = 0
    if (excVocList[wordL]['freq'] <= 65000):  # if word is not in database, ignore it.
        for index, sentence in enumerate(coca_sents):  # check sentence by line
            wordInSentence = sentence.split(' ')
            thing_index = indexCheck(wordL, wordInSentence)  # check if target word in sentences
            if (ind <= 100):
                flip = 1
            elif (ind > 100 and ind <= 200):
                flip = index % 2
            else:
                break
            if (thing_index != -1 and flip):
                wordPosInSentence = posCheck(wordL, thing_index, sentence)  #check pos of word in sentence
                if(wordPosInSentence == word_pos):
                    score = returnGDEXScore(wordInSentence, thing_index, sentence)
                    CandidateDict[sentence] = score
                    ind = ind + 1
        if CandidateDict:
            sentcan = max(CandidateDict.items(), key=lambda x: x[1])
            sentcan = sentcan[:-1] # get rid of score
            sent = rebuild_sent(str(sentcan), wordL)    # bracket [answer]
        else:
            pass  # if no sentence, ignore it.
        return sent[1:-1]  # delete bracket
def readDatabase():
    disDB = defaultdict(lambda :dict())
    with open('./utils/data/quiz_sentence.json', 'r') as fp:
        gdexDB = json.load(fp)
    for line in open('./utils/data/distractor_data.txt', 'r'):
        wordL, c1, c2, c3 = line.strip().split()
        disDB[wordL] = c1, c2, c3
    return gdexDB, disDB
def mcqGDEX(wordL,word_pos,gdexDB):
    if (wordL in gdexDB):  # if word in database, take it.
        if(word_pos in gdexDB[wordL]):
            tmp_sentence = gdexDB[wordL][word_pos][1:-1]  #delete bracket
        else:
            return ""
    else:  # if word is not in database, ignore it
        return ""
    return tmp_sentence
def remove_punc(s):
    indices = [i for i, x in enumerate(s) if x == "\\"]  # replace ' punctuation
    for ind in indices:
        s = s[:ind] + s[ind + 1:]
    # translator = str.maketrans('', '', string.punctuation)
    # s = s.translate(translator)
    if(s[0] == "]"or s[0] == "'"or s[0] == "\""):
        s = s[1:]
    elif(s[1] == "]"or s[1] == "'" or s[1] == "\""):
        s = s[2:]
    if (s[-1] == "]" or s[-1] == "'" or s[-1] == "\""):
        s = s[:-2]
    elif (s[-2] == "]" or s[-2] == "'" or s[-2] == "\""):
        s = s[:-3]

    return s
def generateOrderQ(listOfSentences):
    senPList = []
    orderDict = defaultdict(lambda: dict())
    for sent in listOfSentences:
        tmp = sent.split(",")
        if( len(tmp) > 1 and len(tmp[0]) > 15 and len(tmp[1]) > 15
            and len(tmp[0]) < 100 and len(tmp[1]) < 100):
            senPList.append(tmp)
    random.shuffle(senPList)
    choiceList = [remove_punc(x[1]) for x in senPList if len(x) > 1]
    questionList = [remove_punc(x[0]) for x in senPList if len(x) > 1]
    for q_num in range(1):
        if(len(choiceList) >= 4 and len(questionList) >= 1):
            orderDict[q_num]["sentence"] = questionList[0]
            tmp_list = choiceList[:4]
            random.shuffle(tmp_list)
            orderDict[q_num]["distractor"] = tmp_list
            orderDict[q_num]["answer"] = tmp_list.index(choiceList[0]) + 1
            questionList = questionList[4:]
            choiceList = choiceList[4:]
        else:
            orderDict[q_num]["sentence"] = ""
            orderDict[q_num]["distractor"] = ""
            orderDict[q_num]["answer"] = -1
    return orderDict
def multipleChoiceHtml(questionDict,html,proNum,sliceList,vocab):
    distractorNum = 4
    flag = False
    cut = 0
    if ("cloze" in sliceList):
        flag = True
        cut = sliceList["cloze"]
    if(questionDict):
        for index,key in enumerate(questionDict):
            if(flag and  index < cut): continue
            sent = questionDict[key]['sentence']
            choices = questionDict[key]['distractor']
            if(len(choices) < 4 ):
                proNum = proNum - 1
                pro_num = index + proNum - cut
                continue
            pro_num = index + proNum - cut
            itemNum = pro_num*distractorNum
            indices = [i for i, x in enumerate(sent) if x == "'"]   #replace ' punctuation
            # for ind in indices:
            #     sent = sent[:ind] + "'" + sent[ind+1:]
            html.write("\t\t<li>\n")
            # html.write("\t\t\t<h3>" + sent + "</h3>\n")
            html.write("\t\t\t<h4>")
            for sen in sent.split():
                if(sen in vocab):
                    lemma_word, dataWord,level, pos_tag = vocab[sen]
                    html.write('<span data-lemma="'+lemma_word+'" data-word="' + dataWord + '" data-level="' + level + '" data-pos="' + pos_tag +
                               '">'+sen+"</span>")
                else:
                    html.write('<span>'+sen+"</span>")
            html.write("</h4>\n")

            for i in range(distractorNum):
                pi = "pickup-"+ str(itemNum+i+1)
                html.write("\t\t\t<input type =\"radio\" name =\"question" + str(pro_num) + "\" "
              "id = "+pi+" value=\""+(str(i+1))+"\">\n")
                if(choices[i] in vocab):
                    lemma_word, dataWord,level, pos_tag = vocab[choices[i]]
                    html.write("\t\t\t<label for=" + pi + " class = ans" + str(pro_num) + ""
                    ' data-lemma="'+lemma_word+'" data-word="' + dataWord + '" data-level="' + level +
                    "\" data-pos=\"" + pos_tag + "\" >" + choices[i] + "</label><br>\n")
                else:
                    html.write("\t\t\t<label for="+pi+" class = ans"+str(pro_num)+">"+choices[i]+"</label><br>\n")
            html.write("\t\t</li>\n")
    return pro_num

def clozeHtml(questionDict,html,proNum,sliceList,vocab,pure_text):
    if(questionDict):
        num = sliceList["cloze"]
        html.write("\t\t<li>\n")
        html.write("\t\t\t<form>\n")
        for index,key in enumerate(questionDict):
            if(index == num): break
            sent = questionDict[key]['sentence']
            # pro_num = index + proNum
            indices = [i for i, x in enumerate(sent) if x == "'"]   #replace ' punctuation
            for ind in indices:
                sent = sent[:ind] + "\'" + sent[ind+1:]
            sent = rebuildSent(sent,key)
            if(sent == ""): continue
            html.write("<h4>")
            for sen in sent.split():
                if (sen in vocab):
                    lemma_word, dataWord,level, pos_tag = vocab[sen]
                    html.write('<span data-lemma="'+lemma_word+'" data-word="' + dataWord
                               + '" data-level="' + level + '" data-pos="' + pos_tag +
                               '">' + sen + "</span>")
                else:
                    html.write('<span>' + sen + "</span>")
            html.write("</h4>\n")
            # html.write("\t\t\t"+sent +"<br>\n")
            html.write("\n\t\t\t<br><textarea  rows = \"1\" cols = \"20\" align = \"left\" "
                       "name = cloze" + str(index) + " id = clozeA" + str(index) + "></textarea>\n")
            if (key in vocab):
                lemma_word, dataWord, level, pos_tag = vocab[key]
                html.write(
                    '<span><div data-lemma="'+lemma_word+'" data-word="' + dataWord +
                    '" data-level="' + level + '" data-pos="' + pos_tag
                    + '" id = clozeAns'+ str(index) + " class = clozeAns" + str(index) + " name = clozeAns" + str(
                        index) + " style = \"display:none;\">" + str(key) + "</div></span><br>\n")
            else:
                html.write(
                    "<div id = clozeAns" + str(index) + " class = clozeAns" + str(index) + " name = clozeAns" + str(
                        index) +
                    " style = \"display:none;\">" + str(key) + "</div><br>\n")
        html.write("\t\t\t</form>\n")
        html.write("\t\t</li>\n")

    return

def rebuildSent(sent,key):
    if("_" in sent and "_ " in sent):
        indStart = sent.index("_")
        indEnd = sent.index("_ ")
        sent = sent[:indStart] + key[:2] + "_____" +key[-1] + sent[indEnd+1:]
    return sent
def multipleChoiceJs(questionDict,js,cat,cloze):
    L = len(questionDict)
    for index,item in enumerate(questionDict):
        if(index == L-1 and cat == 0): break
        if(index < cloze): continue
        if(questionDict[item]["answer"] == -1): continue
        if(len(questionDict[item]["distractor"]) < 4): continue
        if(index > 0  and questionDict[item]['sentence'] != "" and index>cloze):
            js.write(",")
        js.write("\""+str(questionDict[item]["answer"])+"\"")
    if(cat == 0 and questionDict[item]["answer"]!=-1):
        js.write(",\"" + str(questionDict[item]["answer"]) + "\"],\n")
    elif(cat == 0 and questionDict[item]["answer"]==-1):
        js.write("],\n")

    return cat
def generateHtml(questionDict,orderDict,proNum,sliceList,vocab,pure_text):
    distractorNum = 4
    html = open("./templates/index2.html", "w", encoding='utf-8')
#     html.write("""<!DOCTYPE html>
# <html>
# <head>
# <link rel="stylesheet" type="text/css" href="./static/css/index2.css">
# <script type="text/javascript" src="./static/js/index2.js" ></script>
# </head>
# <body>\n""")
    html.write("\t<ul>\n")
    if(questionDict):
        sliceL =  sliceList
        if(sliceL["cloze"] > 0):
            clozeHtml(questionDict,html,proNum,sliceList,vocab,pure_text)
        pro_num = multipleChoiceHtml(questionDict,html,proNum,sliceL,vocab)
    if(orderDict):
        sliceL = {"none": 2}
        multipleChoiceHtml(orderDict,html,pro_num+1,sliceL,vocab)
    html.write("\t</ul>\n"
               "\t<button onclick=\"returnScore2()\">Submit</button>\n"
               # "\t<a href=\"www.mypage.com\" onclick=\"window.history.go(-1); return false;\"> Link </a>\n"
               "<button onclick=\"window.history.go(-1); return false;\">"
               "Return</button>\n")
#     html.write("""
# </body>
# </html>""")
    html.close()
    return
def generateJs3(questionDict,orderDict,cat,sliceList):
    text = """tot = answers.length;
    var valList = [];
function getCheckedValue( radioName ){
    var radios = document.getElementsByName( radioName ); // Get radio group by-name
    checkedValue = -1;
    for(var y=0; y<radios.length; y++){
      radios[y].disabled = true;
      if(radios[y].checked){
        checkedValue = radios[y].value; // return the checked value
       }
    }
    return checkedValue; // return the checked value
}
function getTypedValue( textName ){
    var text = document.getElementsByName( textName ); 
    for(var y=0; y<text.length; y++){
      enterText = text[y].value; 
    }
    return enterText; 
}
function Clear(){
  var radios;
    for (var i=0; i<tot; i++){
      radioName = "question"+i;  
       radios = document.getElementsByName(radioName); 
    for(var y=0; y<radios.length; y++){
      radios[y].disabled = false;
    }
   }
}
function getScore(){
  var score = 0;
  for (var i=0; i<tot; i++){
      Checkedval = getCheckedValue("question"+i);
    if(Checkedval===answers[i]){   
       score += 1; // increment only 
       valList[i] = Checkedval;
    }
    else{
        valList[i] = Checkedval;     
    }
  }
  return score;
}
function getClozeScore(){
  var score = 0;
  for (var i=0; i<clozeTot; i++){
      enterText = getTypedValue("cloze"+i);
    if(enterText === clozeAnswers[i]){   
       score += 1; // increment only 
       clozeValList[i] = 1;
    }
    else{
        clozeValList[i] = 0;     
    }
  }
  return score;
}
function returnScore2(){
  score = getClozeScore();
   // document.getElementById("demo").innerHTML = score;
  // alert("Your score is "+ score +"/"+ tot);
    var i;
    for (i = 0; i < clozeTot; i++) {
         var nam = document.getElementById('clozeA'+i)
         // var nam = document.querySelectorAll("clozeA"+i);
        if(clozeValList[i] == 1){
        nam.style.backgroundColor= "#0C0";
        nam.style.color= "white";
        }
      else{
         var blockName = document.getElementById('clozeAns'+i)
        blockName.style.display = "block";
        blockName.style.fontWeight = "bold";
        nam.style.backgroundColor= "red";
        nam.style.color= "white";
      }      
    }
        var colr = document.getElementsByClassName("tab-content");
      colr[0].style.opacity =  1;
      // document.getElementById("demo").innerHTML = score;
      score1 = returnScore();
     alert("Your score is "+ (score + score1) +"/"+ (tot+clozeTot));
     // document.getElementById("demo").innerHTML = score;
}
function returnScore(){
  score1 = getScore();
  // alert("Your score is "+ score +"/"+ tot);
    var i;
    for (i = 0; i < tot; i++) {
          var y = document.querySelectorAll(".ans"+i);
         //document.getElementById("demo").innerHTML = valList[0];
         //document.getElementById("testing").innerHTML = answers[0];
        if(valList[i] !== answers[i] && valList[i]!=-1){
           y[valList[i]-1].style.backgroundColor = "red"; 
           y[answers[i]-1].style.backgroundColor = "#0C0";
           y[answers[i]-1].style.color = "white"; 
        }
      else{
          y[answers[i]-1].style.backgroundColor = "#0C0";         
      }      
    } 
  return score1
}
    """
    L = sliceList["cloze"]
    # js = open("./static/js/index2.js", "w", encoding='utf-8')
    js = open("./templates/index2.html", "a", encoding='utf-8')
    ans = [item for item in questionDict]
    # print("var clozeAnswers = " + str(ans[:L]))
    js.write("<script>\n")
    if(len(ans)>=L):
        js.write("var clozeAnswers = "+str(ans[:L])+",\n")
    else:
        js.write("var clozeAnswers =[\"\"]" +",\n")
    js.write("""clozeTot = clozeAnswers.length;
var clozeValList = [];\n""")
    js.write("var answers = [")
    if(questionDict):
        cat = cat - 1
        if(len(orderDict) == 0): cat = cat - 1
        multipleChoiceJs(questionDict, js,cat,L)
    if(orderDict):
        cat = cat - 1 # print different thing for  last category
        multipleChoiceJs(orderDict, js,cat,0)
    js.write(text)
    js.write("</script>\n")
    js.close()
    return
def generateJs(questionDict,orderDict,cat,sliceList):
    text = """tot = answers.length;
    var valList = [];
function getCheckedValue( radioName ){
    var radios = document.getElementsByName( radioName ); // Get radio group by-name
    checkedValue = -1;
    for(var y=0; y<radios.length; y++){
      radios[y].disabled = true;
      if(radios[y].checked){
        checkedValue = radios[y].value; // return the checked value
       }
    }
    return checkedValue; // return the checked value
}
function getTypedValue( textName ){
    var text = document.getElementsByName( textName ); 
    for(var y=0; y<text.length; y++){
      enterText = text[y].value; 
    }
    return enterText; 
}
function Clear(){
  var radios;
    for (var i=0; i<tot; i++){
      radioName = "question"+i;  
       radios = document.getElementsByName(radioName); 
    for(var y=0; y<radios.length; y++){
      radios[y].disabled = false;
    }
   }
}
function getScore(){
  var score = 0;
  for (var i=0; i<tot; i++){
      Checkedval = getCheckedValue("question"+i);
    if(Checkedval===answers[i]){   
       score += 1; // increment only 
       valList[i] = Checkedval;
    }
    else{
        valList[i] = Checkedval;     
    }
  }
  return score;
}
function getClozeScore(){
  var score = 0;
  for (var i=0; i<clozeTot; i++){
      enterText = getTypedValue("cloze"+i);
    if(enterText === clozeAnswers[i]){   
       score += 1; // increment only 
       clozeValList[i] = 1;
    }
    else{
        clozeValList[i] = 0;     
    }
  }
  return score;
}
function returnScore2(){
  score = getClozeScore();
   // document.getElementById("demo").innerHTML = score;
  // alert("Your score is "+ score +"/"+ tot);
    var i;
    for (i = 0; i < clozeTot; i++) {
         var nam = document.getElementById('clozeA'+i)
         // var nam = document.querySelectorAll("clozeA"+i);
        if(clozeValList[i] == 1){
        nam.style.backgroundColor= "#0C0";
        nam.style.color= "white";
        }
      else{
         var blockName = document.getElementById('clozeAns'+i)
        blockName.style.display = "block";
        blockName.style.fontWeight = "bold";
        nam.style.backgroundColor= "red";
        nam.style.color= "white";
      }      
    }
    var colr = document.getElementsByClassName("tab-content");
    colr[0].style.opacity =  1;
    // document.getElementById("demo").innerHTML = score;
    score1 = returnScore();
    alert("Your score is "+ (score + score1) +"/"+ (tot+clozeTot));
    // document.getElementById("demo").innerHTML = score;
}
function returnScore(){
  score1 = getScore();
  // alert("Your score is "+ score +"/"+ tot);
    var i;
    for (i = 0; i < tot; i++) {
          var y = document.querySelectorAll(".ans"+i);
         //document.getElementById("demo").innerHTML = valList[0];
         //document.getElementById("testing").innerHTML = answers[0];
        if(valList[i] !== answers[i] && valList[i]!=-1){
           y[valList[i]-1].style.backgroundColor = "red"; 
           y[answers[i]-1].style.backgroundColor = "#0C0";
           y[answers[i]-1].style.color = "white"; 
        }
      else{
          y[answers[i]-1].style.backgroundColor = "#0C0";         
      }      
    } 
  return score1
}
    """
    L = sliceList["cloze"]
    js = open("./templates/index2.html", "a", encoding='utf-8')
    ans = [item for item in questionDict]
    js.write("<script>\n")
    if(len(ans)>=L):
        js.write("var clozeAnswers = "+str(ans[:L])+",\n")
    else:
        js.write("var clozeAnswers =[\"\"]" +",\n")
    js.write("""clozeTot = clozeAnswers.length;\nvar clozeValList = [];\n""")
    if(questionDict):
        mcq_ans = [str(questionDict[item]["answer"]) for item in questionDict]
        if(len(orderDict) > 0):
            order_ans = [str(orderDict[item]["answer"]) for item in orderDict]
            js.write("var answers = " + str(mcq_ans[L:])[:-1]+", "+str(order_ans)[1:]+",\n")
        else:
            js.write("var answers = " + str(mcq_ans[L:])+",\n")
    js.write(text)
    js.write("\n</script>\n")
    js.close()
    return
def mcqDistractor(wordL,disDB):
    if (wordL in disDB):  # if word in database, take it.
        distracotrCand = []
        distracotrCand.append(wordL)
        for value in disDB[wordL]:
            distracotrCand.append(value)
        if(len(distracotrCand) < 4):
            return "",-1
    else:  # if word is not in database, ignore it or search it right now
        return "",-1
    random.shuffle(distracotrCand)
    ans = distracotrCand.index(wordL) + 1
    return  distracotrCand,ans
def generateMCQ(vocList,pro_num,level,pure_text):
    questionDict = defaultdict(lambda: defaultdict(lambda :dict))
    gdexDB, disDB = readDatabase()   #  read GDEX and choices database
    for word in vocList:
        wordL = vocList[word]["lemma"]
        word_pos =  get_spacy_pos(vocList[word]['pos'])
        tmp_sentence = mcqGDEX(wordL, word_pos, gdexDB) #generate GDEX
        tmp_distractor,tmp_ans = mcqDistractor(wordL, disDB) # generate distractor
        if(tmp_sentence!="" and len(tmp_distractor) == 4 and tmp_ans!=-1):
            questionDict[wordL]["sentence"] = tmp_sentence
            questionDict[wordL]["distractor"] = tmp_distractor
            questionDict[wordL]["answer"] = tmp_ans
        else:
            continue

    orderDict = generateOrderQ(pure_text)  #generate order question
    category = 2
    return questionDict,orderDict,pro_num,category  #return question and choices
def generateWeb(questionDict,orderDict,pro_num,category,vocab,pure_text):
    sliceList = {"cloze": 2}
    generateHtml(questionDict,orderDict,pro_num,sliceList,vocab,pure_text)  #generate html code
    generateJs(questionDict,orderDict,category,sliceList)   #generate javascript code
    # generateJs2(questionDict,orderDict,category,sliceList)   #generate javascript code
    return
def merge_two_dicts(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z
