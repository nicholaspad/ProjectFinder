from flask import Flask

from CASClient import CASClient

app = Flask(__name__)
app.secret_key = b"insecure-key"


@app.route("/")
def hello():
    netid = CASClient().authenticate()
    return netid
