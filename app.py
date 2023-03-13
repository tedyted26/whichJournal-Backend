from flask import Flask, request
from flask_cors import CORS, cross_origin
# https://flask.palletsprojects.com/en/2.2.x/installation/#install-flask
# https://flask.palletsprojects.com/en/2.2.x/quickstart/
#  venv\Scripts\activate
# https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/
#  python -m flask run 
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/")
@cross_origin()
def hello_world():
    return '{"text": "Hello, World!"}'

@app.route("/get_results", methods = ['POST'])
def get_results():
    data = request.form
    print(data)
    journals = get_journals()
    conf = get_conferences()
    st = journals.removesuffix(']') + ',' + conf.removeprefix('[')
    return st

def get_journals():
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

def get_conferences():
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

