from flask import Flask
from flask import Response
from webapp import serializer


app = Flask(__name__)


@app.route('/api/v1/')
def api_root():
    return 'ShipBattles API'


@app.route('/api/v1/account', methods=['POST'])
def account_create():
    account = app.account_service.create_random_account()
    session_token = (app
                     .security_service
                     .generate_auth_token_without_password(account.id))
    response = Response(serializer.account_serialize(account), status=201)
    response.headers['X-AuthToken'] = session_token
    return response
