# word list
from reportlab.pdfgen import canvas
import textwrap
import ast
import codecs
import re

def create_wordlist(wordlist, patterns, filename):
    from reportlab.lib.units import inch
    max_length = 90
    max_y = 800
    def long_length(string,offset):
        wrap_text = textwrap.wrap(string, width=max_length)
        c.setFont('Helvetica-Bold', 10)
        c.drawRightString(125, max_y - offset, state+": ")
        c.setFont('Helvetica', 10)
        c.drawString(50 + 80, max_y - offset, wrap_text[0])
        offset = offset + 10
        c.drawString(130, max_y - offset, wrap_text[1])
        return offset
    
    c = canvas.Canvas(filename)
    offset = 50
    c.setFont('Helvetica-Bold', 25)
    c.drawString(50, 780, 'volcabulary List')

    for key in wordlist:
        if offset>=730:
            c.showPage()
            offset = 0
        # print(key+'\n')
        c.setFillColorRGB(1,0.64,0.09) #choose fill colour
        c.rect(45, max_y-5-offset, 7*inch, 18, stroke=0, fill=1) #draw rectangle
        
        c.setFillColorRGB(1,1,1) #choose your font colour
        c.setFont('Helvetica-Bold', 10)
        c.drawString(55, max_y-offset, key[0])
        c.drawRightString(40+7*inch, max_y-offset, ' ▎  ' + key[1]['part of speech'] + '   ▎  ' + key[1]['level'])
        c.setFillColorRGB(0,0,0)
        offset = offset + 5
        for state in key[1]:
            if state == 'part of speech' or state == 'level': continue
            offset = offset+15
            # print(state+": "+wordlist[key][state]+'\n')
            if len(key[1][state]) > max_length:
                offset = long_length(key[1][state], offset)
            else:
                c.setFont('Helvetica-Bold', 10)
                c.drawRightString(125, max_y - offset, state+": ")
                c.setFont('Helvetica', 10)
                c.drawString(50 + 80, max_y - offset, key[1][state])
        offset = offset+30
    
    c.showPage()
    offset = 0
    
    c.setFont('Helvetica-Bold', 25)
    c.drawString(50, max_y - offset, 'Pattern')
    c.setFont('Helvetica-Bold', 10)
    offset = offset+15
    for word, pat, sent, highlight in patterns:
        if offset>=730:
            c.showPage()
            offset = 0
        offset = offset+15
        c.drawString(50, max_y - offset, word+'    '+pat)
        
        r = re.search('(?P<f>\W)'+highlight+'(?P<b>\W)', sent) # cookies
        if r:
            f = r.group('f')
            b = r.group('b')
            sent = sent.replace(f+highlight+b, f+'<b>'+highlight+'</b>'+b)
        else: # About ...
            r = re.match(highlight, sent)
            sent = sent.replace(highlight, '<b>'+highlight+'</b>')
        offset = offset+10
        c.drawString(50, max_y - offset, sent)
    c.save()