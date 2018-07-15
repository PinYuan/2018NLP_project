import spacy
nlp = spacy.load('en_core_web_sm', disable=['parser', 'entity'])
def parse_sent(sent):
    parse = []
    doc = nlp(sent)
    for token in doc:
        parse += [(token.text, token.lemma_, token.tag_)]
    return parse