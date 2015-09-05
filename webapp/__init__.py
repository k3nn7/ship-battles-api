from flask import Flask
from flask import Response
from webapp import serializer


app = Flask(__name__)


@app.route('/api/v1/')
def api_root():
    return 'ShipBattles API'


@app.route('/api/v1/account', methods=['POST'])
def account_create():
    new_account = app.account_service.create_random_account()
    response = Response(serializer.account_serialize(new_account), status=201)
    response.headers['X-AuthToken'] = 'foobar'
    return response
