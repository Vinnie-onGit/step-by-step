import spacy
nlp = spacy.load ("it_core_news_md")
doc = nlp ("Questo è un test.")
print ([token.text for token in doc])