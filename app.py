from flask import Flask, request, g
from flask_cors import CORS, cross_origin
from processing.recommender import recommender_class
from processing.classifier import classifier_class
import mysql.connector
import db
import datetime
import logging

# https://flask.palletsprojects.com/en/2.2.x/installation/#install-flask
# https://flask.palletsprojects.com/en/2.2.x/quickstart/
#  venv\Scripts\activate
# https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/
#  python -m flask run 

app = Flask(__name__)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'whichjournal'

date = datetime.datetime.now()
logname = str(date.day) + "-" +str(date.month) + "-" + str(date.year) + "__" + date.strftime("%X").replace(":", "-")

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("processing/logs/" + logname + '.log')
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

rm = recommender_class(logger)
cs = classifier_class(logger)

@app.route("/")
@cross_origin()
def hello_world():
    return '{"text": "Hello, World!"}'

@app.before_request
def before_request():
    g.db = db.get_db()

@app.after_request
def after_request(response):
    g.db.close()
    return response

@app.route("/get_results", methods = ['POST'])
def get_results():
    

    data = request.form
    print(data)
    journals = get_journals_test()
    conf = get_conferences_test()
    st = journals.removesuffix(']') + ',' + conf.removeprefix('[')



    title = "Digital Economy and Sustainable Development"
    desc = "This is the description of the text"
    keywords = "This may be empty or not, but it is very important"
    isJournals = False
    isConferences = True
    _top = 20
    json_journals = ""
    json_conferences = ""

    if isJournals:
        rm_journals = rm.recommend(title, desc, keywords, table = "journals", top = _top)
        cs_journals = cs.classify_predators(rm_journals)
        json_journals = get_journals_json(cs_journals)
    if isConferences:
        rm_conferences = rm.recommend(title, desc, keywords, table = "conferences", top = _top)
        json_conferences = get_conferences_json(rm_conferences)
    
    if isJournals and isConferences:
        result = json_journals.removesuffix(']') + ',' + json_conferences.removeprefix('[')
    elif isJournals:
        result = json_journals
    elif isConferences:
        result = json_conferences
    else:
        result = ""

    return st

def get_journals_json(journals_dict):
    
    print(journals_dict)

def get_conferences_json(conferences_dict):
    print(conferences_dict)

def get_journals_test():
    json = '['
    for i in range(0,5):
        json += '{"imagePath" : "",'
        json += '"title" : "Journal of' + str(i) + '",'
        json += '"ssn" : "1255-1236' + str(i) + '",'
        json += '"releaseYear" : "2001' + str(i) + '",'
        json += '"type" : "Online' + str(i) + '",'
        json += '"price" : "2000€' + str(i) + '",'
        json += '"impactFactor" : "3.1254' + str(i) + '",'
        json += '"quartil" : "Q1' + str(i) + '",'
        json += '"otherMetrics" : "5.4 (Citescore)' + str(i) + '",'
        json += '"acceptanceRate" : "20%' + str(i) + '",'
        json += '"timeDecision" : "3 weeks' + str(i) + '",'
        json += '"timePublication" : "3 weeks' + str(i) + '"},'
    # json += '{"imagePath" : "",'

    # json += '"timePublication" : "Mitiempopublicacion' + str(i) + '"},'
    json = json.removesuffix(",")
    json += ']'
    return json

def get_conferences_test():
    json = '['
    for i in range(0,5):
        json += '{"titulo" : "International conference on computational physics' + str(i) + '",'
        json += '"fecha" : "March 08-09, 2023' + str(i) + '",'
        json += '"pais" : "Thailand' + str(i) + '",'
        json += '"ciudad" : "Bangkok' + str(i) + '",'
        json += '"fechaInscripcion" : "March 08, 2023' + str(i) + '",'
        json += '"organizacion" : "Organizacion' + str(i) + '",'
        json += '"tipo" : "Online' + str(i) + '",'
        json += '"tags" : " geophysics physics applied physics' + str(i) + '",'
        json += '"precio" : "€ 450' + str(i) + '"},'
    json = json.removesuffix(",")
    json += ']'
    return json