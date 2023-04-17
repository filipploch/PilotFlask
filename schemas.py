from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy.fields import Nested
from models import Player, Match, MatchesData, Team, MatchAction, Stadium, Referee, Cameraman, Commentator

ma = Marshmallow()

class PlayerSchema(ma.Schema):
    class Meta:
        model = Player
        fields = ('id', 'full_name', 'team', 'position',
                  'first_name', 'last_name', 'default_nr',
                  'squad', 'is_active', 'captain')


player_schema = PlayerSchema()
players_schema = PlayerSchema(many=True)


class TeamSchema(ma.Schema):
    class Meta:
        model = Team
        fields = ('id', 'full_name', 'competitions', 'link', 'short_name',
                  'home_tricot_color_number', 'home_color_one', 'home_color_two', 'home_color_three', 'color_for_ui',
                  'away_color_one', 'away_color_two', 'away_color_three', 'selected_tricot', 'bibs_color',
                  'away_tricot_color_number', 'logo_file', 'players')

    players = Nested(players_schema)


team_schema = TeamSchema()
teams_schema = TeamSchema(many=True)


class MatchActionSchema(ma.Schema):
    class Meta:
        model = MatchAction
        fields = ('id', 'desc_polish', 'action_icon')

match_action_schema = MatchActionSchema()


class MatchesDataSchema(ma.Schema):
    class Meta:
        model = MatchesData
        fields = ('id', 'time', 'match_id', 'action_id', 'player_id', 'team_id', 'actual', 'player', 'action', 'team')
    player = Nested(player_schema)
    action = Nested(match_action_schema)
    team = Nested(team_schema)


match_data_schema = MatchesDataSchema()
match_datas_schema = MatchesDataSchema(many=True)


class MatchesSchema(ma.Schema):
    class Meta:
        model = Match
        fields = ('id', 'team_a', 'team_b', 'actual', 'match_length', 'max_fouls', 'actual', 'is_timer_countdown', 'stadium', 'date')
    team_a = Nested(team_schema)
    team_b = Nested(team_schema)


match_schema = MatchesSchema()
matches_schema = MatchesSchema(many=True)


class StadiumSchema(ma.Schema):
    class Meta:
        model = Stadium
        fields = ('id', 'name', 'address')

stadium_schema = StadiumSchema()


class RefereeSchema(ma.Schema):
    class Meta:
        model = Referee
        fields = ('id', 'first_name', 'last_name')

referee_schema = RefereeSchema()


class CameramanSchema(ma.Schema):
    class Meta:
        model = Cameraman
        fields = ('id', 'first_name', 'last_name')

cameraman_schema = CameramanSchema()


class CommentatorSchema(ma.Schema):
    class Meta:
        model = Commentator
        fields = ('id', 'first_name', 'last_name')

commentator_schema = CommentatorSchema()
