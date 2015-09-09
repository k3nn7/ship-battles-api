from flask import Flask
from flask import request, Response
from webapp import serializer
from shipbattles import service


app = Flask(__name__)


@app.route('/api/v1/')
def api_root():
    return 'ShipBattles API'


@app.route('/api/v1/account', methods=['GET'])
def get_authenticated_account():
    authenticate_by_hash(request)
    response = Response('{"id":"a","nick":"b"}')
    return response


@app.route('/api/v1/account', methods=['POST'])
def account_create():
    account = app.account_service.create_random_account()
    session_token = (app
                     .security_service
                     .generate_auth_token_without_password(account.id))
    response = Response(serializer.account_serialize(account), status=201)
    response.headers['X-AuthToken'] = session_token.hash
    return response


@app.route('/api/v1/battle', methods=['POST'])
def battle_create():
    session = authenticate_by_hash(request)
    try:
        app.logger.error(session)
        battle = app.battle_service.attack(session.account_id)
    except service.AlreadyInBattleError:
        raise BadRequestError()

    response = Response(serializer.battle_serialize(battle), status=201)
    return response


class ApiError(Exception):
    status_code = 500


class UnauthorizedError(ApiError):
    status_code = 401


class BadRequestError(ApiError):
    status_code = 400


@app.errorhandler(ApiError)
def handle_unauthorized_error(error):
    response = Response('', status=error.status_code)
    return response


def authenticate_by_hash(request):
    if 'X-AuthToken' not in request.headers:
        raise UnauthorizedError()
    try:
        return (app
                .security_service
                .authenticate_by_hash(request.headers['X-AuthToken']))
    except service.InvalidCredentialsError as e:
        raise UnauthorizedError(e)
