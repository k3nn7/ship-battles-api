from flask import Flask
from flask import request, Response
from webapp import serializer


app = Flask(__name__)


@app.route('/api/v1/')
def api_root():
    return 'ShipBattles API'


@app.route('/api/v1/account', methods=['GET'])
def get_authenticated_account():
    if 'X-AuthToken' in request.headers:
        auth_token = request.headers['X-AuthToken']
        if auth_token == 'foobar':
            response = Response('{"id":"a","nick":"b"}', status=200)
        else:
            response = Response('', status=401)
    else:
        response = Response('', status=401)
    return response


@app.route('/api/v1/account', methods=['POST'])
def account_create():
    account = app.account_service.create_random_account()
    session_token = (app
                     .security_service
                     .generate_auth_token_without_password(account.id))
    response = Response(serializer.account_serialize(account), status=201)
    response.headers['X-AuthToken'] = session_token
    return response
