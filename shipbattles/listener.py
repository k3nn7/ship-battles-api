class BattleDeployFinishedListener:
    def __init__(self, battlefield_service, ship_service):
        self.battlefield_service = battlefield_service
        self.ship_service = ship_service

    def on_event(self, battle):
        self.battlefield_service.create_battlefields_for_battle(battle)
