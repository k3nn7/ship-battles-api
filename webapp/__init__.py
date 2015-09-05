from flask import Flask


app = Flask(__name__)


@app.route('/api/v1/')
def api_root():
    return 'ShipBattles API'
