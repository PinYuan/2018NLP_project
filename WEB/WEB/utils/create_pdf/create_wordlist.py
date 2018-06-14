# word list
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
import textwrap
import ast
import codecs

def create_wordlist(wordlist, pattern, filename):
    from reportlab.lib.units import inch
    
    def long_length(string,offset):
        wrap_text = textwrap.wrap(string, width=max_length)
        c.setFont('Helvetica-Bold', 10)
        c.drawRightString(125, max_y - offset, state+": ")
        c.setFont('Helvetica', 10)
        c.drawString(50 + 80, max_y - offset, wrap_text[0])
        offset = offset + 10
        c.drawString(130, max_y - offset, wrap_text[1])
        return offset
    
    def showPage(offset):
        if offset>=700:
            c.showPage()
            offset = 0
        return offset
    
    max_width = 90
    max_length = 790
    min_y = 30
    BSL = 15 # word block space length
    LSL = 15 # item space length
    
    TBC = 55 # text begin coordinate x
    RBC = TBC-10 # rectangle
    LLBC = 125 # left line 
    RLBC = LLBC+5 # right line
    
    title_size = 25
    T_size = 10 # text size
    
    offset = title_size    
    c = canvas.Canvas(filename)
    c.setFont('Helvetica-Bold', title_size)
    c.drawString(RBC, max_length-offset, 'Volcabulary List')
    offset += T_size
    
    for key in wordlist:
        offset = showPage(offset)
        
        # print word, POS, level
        offset += BSL
        c.setFillColorRGB(1,0.64,0.09)
        c.rect(RBC, max_length-5-offset, 7*inch, 18, stroke=0, fill=1) #draw rectangle
        c.setFillColorRGB(1,1,1) # white
        c.setFont('Helvetica-Bold', T_size)
        c.drawString(TBC, max_length-offset, key[0])
        c.drawRightString(RBC-5+7*inch, max_length-offset, ' ▎  ' + key[1]['part of speech'] + '   ▎  ' + key[1]['level'])
        
        c.setFillColorRGB(0,0,0) # black
        offset += 20
        
        # print sense
        c.setFont('Helvetica-Bold', T_size)
        c.drawRightString(LLBC, max_length - offset, "sense:")
        wrap_text = textwrap.wrap(key[1]['sense'], width=max_width)
        c.setFont('Helvetica', T_size)
        for line in wrap_text:
            c.drawString(RLBC, max_length - offset, line)
            if line != wrap_text[-1]:
                offset += T_size
        offset += LSL
        
        # print original sentence
        c.setFont('Helvetica-Bold', T_size)
        c.drawRightString(LLBC, max_length - offset, "origin sentence:")
        wrap_text = textwrap.wrap(key[1]['origin sentence'], width=max_width)
        c.setFont('Helvetica', T_size)
        for line in wrap_text:
            c.drawString(RLBC, max_length - offset, line)
            if line != wrap_text[-1]:
                offset += T_size
        offset += LSL
                
        # print example
        c.setFont('Helvetica-Bold', T_size)
        c.drawRightString(LLBC, max_length - offset, "example:")
        wrap_text = textwrap.wrap(key[1]['dict_examp'], width=max_width)
        c.setFont('Helvetica', T_size)
        for line in wrap_text:
            c.drawString(RLBC, max_length - offset, line)
            if line != wrap_text[-1]:
                offset += T_size
        offset += LSL
        
        # print example 2
        if key[1]['lear_examp']:
            c.setFont('Helvetica-Bold', T_size)
            c.drawRightString(LLBC, max_length - offset, "example:")
            wrap_text = textwrap.wrap(key[1]['lear_examp'], width=max_width)
            c.setFont('Helvetica', T_size)
            for line in wrap_text:
                c.drawString(RLBC, max_length - offset, line)
                if line != wrap_text[-1]:
                    offset += T_size
        
        offset += BSL

    c.save()