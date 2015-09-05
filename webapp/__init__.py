from flask import Flask
from flask import Response


app = Flask(__name__)


@app.route('/api/v1/')
def api_root():
    return 'ShipBattles API'


@app.route('/api/v1/account', methods=['POST'])
def account_create():
    response = Response('{"nick":"testuser","id":"foo123"}', status=201)
    response.headers['X-AuthToken'] = 'foobar'
    return response
