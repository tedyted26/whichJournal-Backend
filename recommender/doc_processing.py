import spacy
from collections import Counter
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer

def tokenizer(text):
    nlp = spacy.load("en_core_web_sm")
    text_doc = nlp(text.translate({ord(i): " " for i in "0123456789ºª!·$%&/()=|@#~€¬'?¡¿`+^*[]´¨}{,.-;:_<>\n \""}))

    text_lemma = [token.lemma_.lower().strip() for token in text_doc if not token.is_stop and not token.is_punct and not len(token)<2]

    return text_lemma


