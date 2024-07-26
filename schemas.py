from flask_marshmallow import Marshmallow
from marshmallow import fields
from marshmallow_sqlalchemy.fields import Nested
from models import (Player, Match, MatchesData, Team, MatchAction, Stadium, Staff, Division, LeagueMatches,
                    TimerDisplayMode)

ma = Marshmallow()

class PlayerSchema(ma.Schema):
    class Meta:
        model = Player
        fields = ('id', 'full_name', 'team', 'position',
                  'matches', 'goals', 'assists',
                  'yellow_cards', 'red_cards', 'own_goals',
                  'best_five', 'best_players',
                  'first_name', 'last_name', 'default_nr',
                  'squad', 'is_active', 'captain', 'link')


player_schema = PlayerSchema()
players_schema = PlayerSchema(many=True)


class TeamSchema(ma.Schema):
    class Meta:
        model = Team
        fields = ('id', 'full_name', 'competitions', 'link', 'short_name',
                  'home_tricot_color_number', 'home_color_1', 'home_color_2', 'home_color_3', 'color_for_ui',
                  'away_color_1', 'away_color_2', 'away_color_3', 'selected_tricot', 'bibs_color',
                  'away_tricot_color_number', 'logo_file', 'penalty_points', 'players', 'name_16')

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
        fields = ('id', 'seconds', 'added_seconds', 'current_period_time_limit', 'match_id', 'action_id', 'player_id',
                  'team_id', 'record_time', 'actual', 'player', 'action', 'team', 'is_hided', 'replay_file')
    player = Nested(player_schema)
    action = Nested(match_action_schema)
    team = Nested(team_schema)


match_data_schema = MatchesDataSchema()
match_datas_schema = MatchesDataSchema(many=True)


class StaffSchema(ma.Schema):
    class Meta:
        model = Staff
        fields = ('id', 'first_name', 'last_name')

staff_schema = StaffSchema(many=True)


class DivisionSchema(ma.Schema):
    class Meta:
        model = Division
        fields = ('id', 'name', 'is_cup')

division_schema = DivisionSchema()


class MatchesSchema(ma.Schema):
    class Meta:
        model = Match
        fields = ('id', 'team_a', 'team_b', 'actual', 'periods', 'period_length', 'is_added_time_allowed',
                  'extra_time_periods', 'extra_time_period_length', 'max_fouls',
                  'panel_timer_display_mode', 'seconds', 'added_seconds', 'is_timer_active', 'panel_timer_display_mode',
                  'is_panel_timer_ascending', 'stream_timer_display_mode', 'is_stream_timer_ascending', 'stadium',
                  'date', 'commentator', 'cameraman', 'referee', 'division', 'competitions', 'is_scoreboard_reversed')

    # team_a = Nested(team_schema)
    # team_b = Nested(team_schema)
    commentator = Nested(staff_schema, many=True)
    cameraman = Nested(staff_schema, many=True)
    referee = Nested(staff_schema, many=True)
    division = Nested(division_schema)


match_schema = MatchesSchema()
matches_schema = MatchesSchema(many=True)


class StadiumSchema(ma.Schema):
    class Meta:
        model = Stadium
        fields = ('id', 'name', 'address')


stadium_schema = StadiumSchema()


class LeagueMatchesSchema(ma.Schema):
    class Meta:
        model = LeagueMatches
        fields = ('id', 'team1', 'team2', 'score1', 'score2',
                  'competitions', 'division', 'date', 'event_id',
                  'is_actual', 'team1_penalty_points', 'team2_penalty_points')

    team1 = fields.Nested(team_schema)
    team2 = fields.Nested(team_schema)
    division = fields.Nested(division_schema)

league_match_schema = LeagueMatchesSchema()
league_matches_schema = LeagueMatchesSchema(many=True)


class TimerDisplayModeSchema(ma.Schema):
    class Meta:
        model = TimerDisplayMode
        fields = ('id', 'format')


timer_display_mode_schema = TimerDisplayModeSchema()









