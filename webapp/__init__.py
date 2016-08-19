from flask import Flask
from flask import request, Response
from webapp import serializer
from webapp.serializer import collection, j
from shipbattles import service, entity
import json


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
    response = Response(
        j(serializer.account_serialize(account)),
        status=201
    )
    response.headers['X-AuthToken'] = session_token.hash
    return response


@app.route('/api/v1/account/password', methods=['PUT'])
def account_update_password_authenticated_account():
    session = authenticate_by_hash(request)
    request_body = json.loads(request.data.decode('utf-8'))
    current_password = None
    new_password = None
    if 'new_password' in request_body:
        new_password = request_body['new_password']
    if 'current_password' in request_body:
        current_password = request_body['current_password']
    try:
        app.account_service.update_password(
            session.account_id,
            current_password,
            new_password
        )
    except service.ValidationError:
        raise BadRequestError
    return Response(None, status=204)


@app.route('/api/v1/account/nickname', methods=['PUT'])
def account_update_nickname_authenticated_account():
    session = authenticate_by_hash(request)
    request_body = json.loads(request.data.decode('utf-8'))
    nickname = None
    if 'nickname' in request_body:
        nickname = request_body['nickname']
    try:
        app.account_service.update_nickname(
            session.account_id,
            nickname
        )
    except service.ValidationError:
        raise BadRequestError
    return Response(None, status=204)


@app.route('/api/v1/battle', methods=['POST'])
def battle_create():
    session = authenticate_by_hash(request)
    try:
        battle = app.battle_service.attack(session.account_id)
    except service.AlreadyInBattleError:
        raise BadRequestError()

    response = Response(
        j(serializer.battle_serialize(battle)),
        status=201
    )
    return response


@app.route('/api/v1/battles', methods=['GET'])
def battle_get_current():
    session = authenticate_by_hash(request)
    current_battle = app.battle_service.get_current_battle(session.account_id)
    if current_battle is None:
        return Response(None, status=404)

    try:
        my_battlefield = serializer.my_battlefield_serialize(
            app.battlefield_service.get_my_battlefield(
                current_battle, session.account_id)
        )
    except service.EntityNotFoundError:
        my_battlefield = None

    try:
        opponent_battlefield = serializer.opponent_battlefield_serialize(
            app.battlefield_service.get_opponent_battlefield(
                current_battle, session.account_id)
        )
    except service.EntityNotFoundError:
        opponent_battlefield = None

    response_body = serializer.battle_serialize(current_battle)
    response_body['my_battlefield'] = my_battlefield
    response_body['opponent_battlefield'] = opponent_battlefield

    return Response(
        j(response_body),
        status=200
    )


@app.route('/api/v1/battle/my-battlefield', methods=['PUT'])
def deploy_ship():
    session = authenticate_by_hash(request)
    request_body = json.loads(request.data.decode('utf-8'))

    current_battle = app.battle_service.get_current_battle(session.account_id)
    my_battlefield = app.battlefield_service.get_my_battlefield(
        current_battle, session.account_id)

    for ship_data in request_body['ships']:
        try:
            ship_class = app.ship_class_repository.find_by_id(ship_data['id'])
            ship = entity.Ship(ship_data['id'], entity.Coordinates(
                ship_data['x'], ship_data['y']), ship_class.size,
                entity.Orientation(ship_data['orientation']))
            app.battle_service.deploy_ship_for_battle(
                current_battle.id, session.account_id, ship)
        except service.EntityNotFoundError:
            pass
        except service.InvalidShipClassError:
            pass

    my_battlefield = app.battlefield_service.get_my_battlefield(
        current_battle, session.account_id)

    return Response(
        j(serializer.my_battlefield_serialize(my_battlefield)),
        status=200
    )


@app.route('/api/v1/battle/ready', methods=['PUT'])
def ready_for_battle():
    session = authenticate_by_hash(request)
    current_battle = app.battle_service.get_current_battle(session.account_id)
    try:
        app.battle_service.ready_for_battle(
            session.account_id, current_battle.id)
    except service.NotAllShipsDeployedError:
        return Response(
            None,
            status=400
        )

    return Response(
        None,
        status=204
    )


@app.route('/api/v1/battle/shots', methods=['PUT'])
def fire():
    session = authenticate_by_hash(request)
    request_body = json.loads(request.data.decode('utf-8'))
    current_battle = app.battle_service.get_current_battle(session.account_id)
    coordinates = entity.Coordinates(
        request_body['x'],
        request_body['y'])
    try:
        result = app.battle_service.fire(
            current_battle.id,
            session.account_id,
            coordinates
        )
        return Response(
            j({'fire_result': result.value}),
            status=200
        )
    except service.InvalidBattleStateError:
        return Response(
            None,
            status=400
        )


@app.route('/api/v1/ship_classes', methods=['GET'])
def ship_classes_get():
    ship_classes = app.ship_class_service.get_all()
    return Response(
        j(collection(ship_classes, serializer.ship_class_serialize)),
        status=200
    )


@app.route('/api/v1/battle/my-battlefield/inventory')
def inventory_get():
    session = authenticate_by_hash(request)
    current_battle = app.battle_service.get_current_battle(session.account_id)
    my_battlefield = app.battlefield_service.get_my_battlefield(
        current_battle, session.account_id)
    inventory = app.ship_repository.find_by_battlefield_id(
        my_battlefield.id)
    return Response(
        j(collection(inventory, serializer.ship_serialize)),
        status=200
        )


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
