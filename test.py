from flask import Flask
# https://flask.palletsprojects.com/en/2.2.x/installation/#install-flask
# https://flask.palletsprojects.com/en/2.2.x/quickstart/

app = Flask(__name__)

@app.route("/")
def hello_world():
    return '{"text": "Hello, World!"}'