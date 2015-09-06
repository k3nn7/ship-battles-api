# from pymongo import MongoClient
#
#
# print("connecting...")
#
# client = MongoClient("mongodb://mongodb:27017")
# db = client.shipbattles
#
# result = db.users.insert_one({
#     "nick": "k3nn7",
#     "email": "lukasz.lalik@gmail.com"
# })
#
# print(result)
import webapp
from shipbattles import service
from repository import memory


def main():
    account_repository = memory.CrudRepository()
    session_token_repository = memory.SessionTokenRepository()
    webapp.app.debug = True
    webapp.app.account_service = service.AccountService(
        account_repository
    )
    webapp.app.security_service = service.SecurityService(
        account_repository,
        session_token_repository
    )
    webapp.app.run(host='0.0.0.0', port=8080)

if __name__ == '__main__':
    main()
