from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.colors import (
    black,
    purple,
    white,
    yellow
)

def stylesheet():
    styles= {
        'default': ParagraphStyle(
            'default',
            fontName='Times-Roman',
            fontSize=10,
            leading=24, # double space 
            leftIndent=0,
            rightIndent=0,
            firstLineIndent= 0, # -12, firstindent make layout error
            alignment=TA_LEFT,
            spaceBefore=20,
            spaceAfter=20,
            bulletFontName='Times-Roman',
            bulletFontSize=10,
            bulletIndent=0,
            textColor= black,
            backColor=None,
            wordWrap=None,
            borderWidth= 0,
            borderPadding= 0,
            borderColor= None,
            borderRadius= None,
            allowWidows= 1,
            allowOrphans= 0,
            textTransform=None,  # 'uppercase' | 'lowercase' | None
            endDots=None,         
            splitLongWords=1,
        ),
    }
    styles['title'] = ParagraphStyle(
        'title',
        parent=styles['default'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=42,
        alignment=TA_CENTER,
        textColor=purple,
    )
    styles['h2'] = ParagraphStyle(
        'h2',
        parent=styles['default'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=42,
        alignment=TA_CENTER,
        textColor=purple,
    )
    styles['h3'] = ParagraphStyle(
        'h3',
        parent=styles['default'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=42,
        alignment=TA_CENTER,
        textColor=purple,
    )
    styles['alert'] = ParagraphStyle(
        'alert',
        parent=styles['default'],
        leading=14,
        backColor=yellow,
        borderColor=black,
        borderWidth=1,
        borderPadding=5,
        borderRadius=2,
        spaceBefore=10,
        spaceAfter=10,
    )
    return styles