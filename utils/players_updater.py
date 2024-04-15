from models import Player
from database import db


class NALFplayersUpdater:
    # def __init__(self, app):
    #     with app.app_context():
    #         self.nalffutsal_players = []
    #         self.local_db_team_id =local_db_team_id
    #         self.local_db_players = Player.query.filter_by(team=self.local_db_team_id).all()

    def update_players(self, nalffutsal_players, local_db_team_id):
        # with app.app_context():
        start_list = Player.query.filter_by(team=local_db_team_id).all()
        updated_list = []
        for player in nalffutsal_players:
            # print('1', player)
            db_player = Player.query.filter_by(full_name=player['full_name']).first()
            # print('2', db_player)
            if db_player:
                db_player.team = local_db_team_id
                db_player.first_name = db_player.full_name.split()[-1]
                db_player.last_name = " ".join(db_player.full_name.split()[0:-1])
                db_player.position = player['is_goalkeeper']
                db_player.matches = player['matches']
                db_player.goals = player['goals']
                db_player.assists = player['assists']
                db_player.yellow_cards = player['yellow_cards']
                db_player.red_cards = player['red_cards']
                db_player.own_goals = player['own_goals']
                db_player.best_five = player['best_five']
                db_player.best_player = player['best_player']
                db_player.link = player['link']
                updated_list.append(db_player)
                self._remove_player(start_list, db_player)
                db.session.add(db_player)
                db.session.commit()
            else:
                db_player = Player(
                    full_name=player['full_name'],
                    team=local_db_team_id,
                    position=player['is_goalkeeper'],
                    matches=player['matches'],
                    goals=player['goals'],
                    assists=player['assists'],
                    yellow_cards=player['yellow_cards'],
                    red_cards=player['red_cards'],
                    own_goals=player['own_goals'],
                    best_five=player['best_five'],
                    best_player=player['best_player'],
                    first_name=player['full_name'].split()[1],
                    last_name=player['full_name'].split()[0],
                    default_nr=0,
                    squad=0,
                    is_active=0,
                    captain=0,
                    link=player['link'],
                )
                updated_list.append(db_player)
                db.session.add(db_player)
                db.session.commit()
        for player in start_list:
            _player = Player.query.filter_by(id=player.id).first()
            _player.team = None
            db.session.add(_player)
            db.session.commit()
        return {'players': updated_list, 'to_delete': start_list}

    def _remove_player(self, start_list, db_player):
        for player in start_list:
            if player.full_name == db_player.full_name:
                start_list.remove(player)

# app = create_app()
# scraper = NALFteamScraper('drug-ony')
# nalffutsal_players = scraper.scrape_team_players()
# player_comp = NALFplayersUpdater(app)
# result = player_comp.compare_players(app, nalffutsal_players, 3)
