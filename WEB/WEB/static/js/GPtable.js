function genTrans(trans) {
    var translate = ''
    for (tranIdx in trans) {
        translate += (tranIdx != 0) ? '/' : '<br>'
        translate += trans[tranIdx]
    }

    return translate
}

function genTable(word, patterns) {
    var table = '</h2><table class="table"> <thead><tr><th>pattern</th><th style="text-align: center;">percent</th><th>col.</th></tr></thead><tbody>'

    var noreplace = new Set('under|without|around|round|about|after|against|among|as|at|between|behind|by|for|from|in|into|of|on|upon|over|through|to|toward|off|on|across|towards|with|out|N|V|ADJ|and|that|ord|pron-refl|if|so|someway|together|it|way|amount|be|V-ed|out|off|down|up|across'.split('|'))
    var NER = new Set(['&lt;GPE&gt;', '&lt;NORP&gt;', '&lt;TIME&gt;', '&lt;MONEY&gt;'])

    for (patIndex in patterns) {
        var tuple = patterns[patIndex];
        var pat, percent, colls, en, ch, source;
        pat = tuple[0].split("%")[0]
        percent = tuple[0].split("%")[1]
        colls = tuple[1].split(", ")
        en = tuple[2][0]
        ch = tuple[2][1]
        source = tuple[2][2]

        /* 重新整理collation呈現，含NER*/
        patList = pat.split(" ")
        var newcolls = []
        for (let coll of colls) {
            coll = coll.split('_')

            newcoll = []
            for (let p of patList) {
                if (noreplace.has(p))
                    newcoll.push(p)
                else {
                    if (NER.has(coll[0])) {
                        if (coll[0] == '&lt;GPE&gt;') newcoll.push('<span class="NER" title="EX. US, UK, Scotland, Chicago">GPE</span>')
                        else if (coll[0] == '&lt;NORP&gt;') newcoll.push('<span class="NER" title="EX. Americans, Asians, Canadians, Italian">NORP</span>')
                        else if (coll[0] == '&lt;TIME&gt;') newcoll.push('<span class="NER" title="EX. year, month, date, minute">TIME</span>')
                        else if (coll[0] == '&lt;MONEY&gt;') newcoll.push('<span class="NER" title="EX. billion, million, dollar, cent">MONEY</span>')
                    } else newcoll.push(coll[0])
                    coll.shift()
                }
            }
            newcoll = newcoll.join(' ')
            newcolls.push(newcoll)
        }
        newcolls = newcolls.join(', ')

        table += '<tr><td style="color: indianred;">' + pat + '</td><td style="text-align: center;">' + percent + "%</td><td>" + newcolls + "</td></tr>"
        if (en != "") table += '<tr><td style="background: #f2f2f2; " colspan=3>' + en
        if (ch != "") table += "<br>" + ch + ' '
        if (source == "cam") table += "<a href='https://dictionary.cambridge.org/zht/搜索/english-chinese-traditional/direct/?q=" + word.toLowerCase() + "' target='blank_'><span class='glyphicon glyphicon-book'></span></a>"
        else if (source != 'coca') table += "<a href='https://dictionary.cambridge.org/zht/搜索/english-chinese-traditional/direct/?q=" + source + "' target='blank_'><span class='glyphicon glyphicon-book'></span></a>"
        table += "</tr>"
        
    }
    table += "</tbody></table>"
    if (!patterns || !word) {
        table = '</h2><table class="table" style="display:none;"> <thead><tr><th>pattern</th><th style="text-align: center;">percent</th><th>col.</th></tr></thead><tbody></tbody></table>'
    }
    return table
}

function whatClicked(evt) {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(xmlhttp.responseText)
            var word = evt.target.getAttribute("data-word").toUpperCase()
            var patTable = ''
            var phrTable = ''

            if (word != null) {
                var pos = evt.target.getAttribute("data-pos")
                
                // pattern

                if (response.change) {
                    patTable += '<p>Since there is no information about "' + evt.target.getAttribute("data-lemma") + '", we show a synonym for this word.</p>';
                }
                patTable += '<h2>' + word + '<span data-pos="' + pos + '"></span>'
                patTable += genTrans(response.trans['pat'][pos])
                patTable += genTable(word.toLowerCase(), response.patternTable[pos])
                document.getElementById("patTable").innerHTML = patTable;
                document.getElementById("patTable").style.height = "auto";

                // phrase
                
                if (response.change) {
                    phrTable += '<p>Since there is no information about "' + evt.target.getAttribute("data-lemma") + '", we show a synonym for this word.</p>';
                }
                if (response.phraseOrder.length > 0) {
                    for (phraseIndex in response.phraseOrder) {
                        var phrase = response.phraseOrder[phraseIndex]
                        phrTable += '<h2>' + phrase.split('%')[0] /*+ '<span data-pos="' + pos + '"></span>'*/
                        phrTable += genTrans(response.trans['phrase'][phrase.split('%')[0]])
                        phrTable += genTable(word.toLowerCase(), response.phraseTable['V'][phrase])
                    }
                    document.getElementById("phrTable").innerHTML = phrTable;
                    document.getElementById("phrTable").style.height = "auto";
                } else {
                    phrTable += '<table class="table" style="display:none;"> <thead><tr><th>pattern</th><th style="text-align: center;">percent</th><th>col.</th></tr></thead><tbody></tbody></table>'
                    document.getElementById("phrTable").innerHTML = phrTable;
                }
            }
        }
    };
    xmlhttp.open('POST', '/ajax')
    xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
    //alert(evt.target.parentElement.parentElement.getAttribute("data-word"))
    var postVars = 'word=' + evt.target.getAttribute("data-word") + '&lemma=' + evt.target.getAttribute("data-lemma") + '&pos=' + evt.target.getAttribute("data-pos")
    //var postVars = 'word='+evt.target.firstChild.nodeValue+'&pos=V'

    xmlhttp.send(postVars);

}

function search() {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(xmlhttp.responseText)
            var word = response.finalWord.toUpperCase()
            var patTable = ''
            var phrTable = ''

            if (word != null) {
                // pattern

                for (let pos of ['V', 'N', 'ADJ']) {
                    if (pos in response.patternTable === false) continue
                    if (response.change) {
                        patTable += '<p>Since there is no information about "' + document.getElementById("search_word").value + '", we show a synonym for this word.</p>';
                    }
                    patTable += '<h2>' + word + '<span data-pos="' + pos + '"></span>'
                    patTable += genTrans(response.trans['pat'][pos])
                    patTable += genTable(word.toLowerCase(), response.patternTable[pos])
                }
                if (patTable == '') {
                    patTable += '<h2>' + word + '</h2><h3>Not found</h3><table class="table"><thead><tr><th>pattern</th><th style="text-align: center;">percent</th><th>col.</th><th>example</th> </tr></thead><tbody></tbody></table>'
                }
                document.getElementById("patTable").innerHTML = patTable;
                document.getElementById("patTable").style.height = "auto";

                // phrase
                
                if (response.phraseOrder.length > 0) {
                    for (phraseIndex in response.phraseOrder) {
                        var phrase = response.phraseOrder[phraseIndex]
                        if (response.change) {
                            phrTable += '<p>Since there is no information about "' + document.getElementById("search_word").value + '", we show a synonym for this word.</p>';
                        }
                        phrTable += '<h2>' + phrase.split('%')[0] /*+ '<span data-pos="' + pos + '"></span>'*/
                        phrTable += genTrans(response.trans['phrase'][phrase.split('%')[0]])
                        phrTable += genTable(word.toLowerCase(), response.phraseTable['V'][phrase])
                    }
                    document.getElementById("phrTable").innerHTML = phrTable;
                    document.getElementById("phrTable").style.height = "auto";
                } else {
                    phrTable += '<table class="table" style="display:none;"> <thead><tr><th>pattern</th><th style="text-align: center;">percent</th><th>col.</th></tr></thead><tbody></tbody></table>'
                    document.getElementById("phrTable").innerHTML = phrTable;
                }
            }
        }
    };
    xmlhttp.open('POST', '/ajax')
    xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
    var postVars = 'word=' + document.getElementById("search_word").value + '&lemma=x&pos=x'

    xmlhttp.send(postVars);

}