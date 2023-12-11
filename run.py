import json
from utils.createeditmatch import CEM
from utils.table_generator import TableGenerator
from flask import Flask, render_template, jsonify, current_app, Blueprint, request, redirect, url_for, send_file
from flask_cors import CORS
from wtforms import BooleanField, StringField
from datetime import datetime, timedelta
import pyautogui
from models import Team, Match, Player, MatchesData, Stadium, Staff, MatchCommentator, MatchCameraman, MatchReferee, \
    MatchAction, Division
from database import db
from schemas import ma, player_schema, players_schema, match_datas_schema, team_schema, teams_schema, match_data_schema, \
    stadium_schema, matches_schema, staff_schema, match_schema, division_schema
import re
from timer import Timer
from obswebsocketpy import OBSWebsocket
# from variables import MATCH_ID, TEAM_A_ID, TEAM_B_ID
from flask_apscheduler import APScheduler
from collections import OrderedDict
from forms import MatchForm, EditTeamForm
import os

monitor_blueprint = Blueprint('monitor', __name__)
controller_blueprint = Blueprint('controller', __name__)
timer_blueprint = Blueprint('timer', __name__)
settings_blueprint = Blueprint('settings', __name__)
obswebsocketpy_blueprint = Blueprint('obswebsocketpy', __name__)

apscheduler = APScheduler()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hardsecretkey'

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:''@localhost/futsal'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.register_blueprint(monitor_blueprint)
    app.register_blueprint(controller_blueprint)
    app.register_blueprint(timer_blueprint)
    app.register_blueprint(settings_blueprint)
    app.register_blueprint(obswebsocketpy_blueprint)
    db.init_app(app)
    ma.init_app(app)
    apscheduler.init_app(app)
    apscheduler.start()
    timer = Timer(app)
    obs_ws = OBSWebsocket(app)
    app.config['obs_ws'] = obs_ws
    apscheduler.add_job(func=timer.control_timer, args=[app], id='timer')
    apscheduler.add_job(func=obs_ws.connect_websocket, args=[app], id='obswebsocketpy')
    CORS(app)
    return app


@monitor_blueprint.route('/')
def index():
    _actual_match = Match.query.filter_by(actual=1).first()
    _teams_names = {'teama': Team.query.filter_by(id=_actual_match.team_a).first().full_name,
                    'teamb': Team.query.filter_by(id=_actual_match.team_b).first().full_name}
    return render_template('index.html', actualMatch=_actual_match, teamsNames=_teams_names)


@timer_blueprint.route('/control-timer/<control_variable>')
def control_timer(control_variable):
    Match.query.filter_by(actual=1).first().is_timer_active = int(control_variable)
    db.session.commit()
    return jsonify({'is_timer_active': Match.query.filter_by(actual=1).first().is_timer_active})


@monitor_blueprint.route('/start')
def start():
    _match = matchdata().get_json()
    _match_details = _match['match']
    _match_details['date'] = decode_date(_match_details['date'])[1:3]
    _logos = {'logo_a': _match['teama']['logo_file'],
              'logo_b': _match['teamb']['logo_file']}
    _teams = {'team_a': Team.query.filter_by(id=_match['teama']['id']).first(),
              'team_b': Team.query.filter_by(id=_match['teamb']['id']).first()
              }
    return render_template('start.html', logos=_logos, teams=_teams, match=_match_details)


@monitor_blueprint.route('/match-preview')
def match_preview():
    _match = matchdata().get_json()
    _match_details = _match['match']
    _match_details['date'] = decode_date(_match_details['date'])[1:3]
    _logos = {'logo_a': _match['teama']['logo_file'],
              'logo_b': _match['teamb']['logo_file']}
    _teams = {'team_a': Team.query.filter_by(id=_match['teama']['id']).first(),
              'team_b': Team.query.filter_by(id=_match['teamb']['id']).first()
              }
    return render_template('match-preview.html', logos=_logos, teams=_teams, match=_match_details)


@monitor_blueprint.route('/match-preview-x26')
def match_preview_x26():
    _match = matchdata().get_json()
    _match_details = _match['match']
    _match_details['date'] = decode_date(_match_details['date'])[1:3]
    _logos = {'logo_a': _match['teama']['logo_file'],
              'logo_b': _match['teamb']['logo_file']}
    _teams = {'team_a': Team.query.filter_by(id=_match['teama']['id']).first(),
              'team_b': Team.query.filter_by(id=_match['teamb']['id']).first()
              }
    return render_template('match-preview-x26.html', logos=_logos, teams=_teams, match=_match_details)


def decode_date(date_to_decode):
    re_pattern = '^(\d{4}-\d{2}-\d{2}) (\d{1,2}:\d{2})$'
    return re.split(re_pattern, date_to_decode)


@monitor_blueprint.route('/match')
def match():
    return render_template('match.html')


@monitor_blueprint.route('/action')
def action():
    _action = MatchesData.query.filter_by(actual=1).first()
    if _action:
        _time = int(int(_action.time) / 60 + 1)

        return render_template('action.html', action=match_data_schema.dump(_action), time_minutes=_time)
    return redirect(url_for('monitor.match'))


@monitor_blueprint.route('/teams')
def teams():
    _match = matchdata().get_json()
    _goals = {'goals_a': MatchesData.query.filter_by(match_id=_match['match']['id']
                                                     , team_id=_match['teama']['id']
                                                     , action_id=1
                                                     ).all(),
              'goals_b': MatchesData.query.filter_by(match_id=_match['match']['id']
                                                     , team_id=_match['teamb']['id']
                                                     , action_id=1
                                                     ).all(),
              'own_goals_a': MatchesData.query.filter_by(match_id=_match['match']['id']
                                                         , team_id=_match['teamb']['id']
                                                         , action_id=4
                                                         ).all(),
              'own_goals_b': MatchesData.query.filter_by(match_id=_match['match']['id']
                                                         , team_id=_match['teama']['id']
                                                         , action_id=4
                                                         ).all()
              }

    _strikers = {'strikers_a': get_strikers(_goals['goals_a'] + _goals['own_goals_a']),
                 'strikers_b': get_strikers(_goals['goals_b'] + _goals['own_goals_b'])}
    return render_template('teams.html', matchdata=_match, strikers=_strikers)


def get_strikers(events):
    strikers = OrderedDict()
    for event in events:
        striker_id = event.player_id
        goal_minute = int(int(event.time) / 60 + 1)
        action = ''
        if event.action_id == 4:
            action = '(S)'

        if striker_id not in strikers:
            strikers.update({striker_id: [[goal_minute], action]})
        else:
            strikers[striker_id][0].append(goal_minute)
    _strikers = sorted(strikers.items(), key=lambda x: x[1][0])
    return get_players_by_id(_strikers)


def get_players_by_id(data):
    new_data = []
    for item in data:
        item[1][0] = sorted(item[1][0])
        new_data.append(
            [Player.query.filter_by(id=item[0]).first(), item[1][1], ', '.join((str(x) + "'") for x in item[1][0])])
    return new_data


@monitor_blueprint.route('/lineup/<team>')
def lineup(team):
    _team_id = matchdata().get_json()[team]['id']
    _team = Team.query.filter_by(id=_team_id).first()
    _lineup = [player for player in _team.players if player.squad]
    _logo = _team.logo_file
    return render_template('lineup.html', _lineup=_lineup, _logo=_logo)


@monitor_blueprint.route('/controller-lineup/<team>')
def controller_lineup(team):
    _team_id = matchdata().get_json()[team]['id']
    _team = Team.query.filter_by(id=_team_id).first()
    _lineup = [{'id': player.id,
                'first-name': player.first_name,
                'last-name': player.last_name,
                'nr': player.default_nr,
                'is-gk': player.position,
                'is-captain': player.captain,
                'team-id': _team.id,
                'team-full-name': _team.full_name,
                'team-short-name': _team.short_name,
                } for player in _team.players if player.squad]
    return jsonify(_lineup)


@monitor_blueprint.route('/controller-lineup-edit/<team>')
def controller_lineup_edit(team):
    _team_id = matchdata().get_json()[team]['id']
    _team = Team.query.filter_by(id=_team_id).first()
    _lineup = [{'id': player.id,
                'squad': player.squad,
                'first-name': player.first_name,
                'last-name': player.last_name,
                'nr': player.default_nr,
                'is-gk': player.position,
                'is-captain': player.captain,
                'team-id': _team.id,
                'team-full-name': _team.full_name,
                'team-short-name': _team.short_name,
                } for player in _team.players]
    return jsonify(_lineup)


@monitor_blueprint.route('/end-screen')
def end_screen():
    _actual_match = Match.query.filter_by(actual=1).first()
    _match_schema = match_schema.dump(_actual_match)
    _staff = {
        'commentator': _match_schema['commentator'],
        'cameraman': _match_schema['cameraman'],
        'producer': [{'id': 0, 'last_name': 'Płoch', 'first_name': 'Filip'}],
        'music': [{'id': 0, 'last_name': 'Plošicek', 'first_name': 'Petr'}]
    }
    return render_template('endscreen.html', staff=_staff)


@monitor_blueprint.route('/virtualtable/<division>')
def virtualtable(division):
    _division = division
    json_file_base_table_path = os.path.join(settings_blueprint.root_path, 'static', 'json', f'base-table-{division}.json')
    json_file_virtual_table_path = os.path.join(settings_blueprint.root_path, 'static', 'json', f'virtual-table-{division}.json')

    # Odczytaj dane z pliku JSON
    with open(json_file_base_table_path, 'r') as json_file:
        data_b = json.load(json_file)

    # Odczytaj dane z pliku JSON
    with open(json_file_virtual_table_path, 'r') as json_file:
        data_v = json.load(json_file)

    short_names = skroty = {'Brotherm': 'BRO',
                            'MK Team': 'MKT',
                            'Legion': 'LEG',
                            'IGLOMEN&RodzinneRestauracje': 'IGL',
                            'Boanerges': 'BOA',
                            'eNHa': 'ENH',
                            'DRUG-ony': 'DRU',
                            'Drink Team': 'DRI',
                            'Trivium Słomniki Warriors': 'SŁO',
                            'WKS Futsal Team': 'WKS',
                            'Złote Chłopaki': 'ZŁO',
                            'Żarłacze': 'ŻAR',
                            'Galactik Futsal': 'GAL',
                            'Nowy Ład': 'NŁD',
                            'Laga Bonito': 'LAG',
                            'Hattrick': 'HAT',
                            'eNHa II': 'EN2',
                            'Popalone Styki': 'STY',
                            'Nowohucki Klub Sportowy': 'NKS'
                            }
    _base_table = data_b
    _base_table = [[short_names[nazwa], wartosc, actual] for nazwa, wartosc, actual in _base_table]
    _virtual_table = data_v
    _virtual_table = [[short_names[nazwa], wartosc, actual] for nazwa, wartosc, actual in _virtual_table]
    return render_template('virtualtable.html', division=division, base_table=_base_table, virtual_table=_virtual_table)


@controller_blueprint.route('/panel')
def panel():
    _matchdata = matchdata().get_json()
    return render_template('panel.html', matchdata=_matchdata)


@controller_blueprint.route('/matchdata')
def matchdata():
    match = Match.query.filter_by(actual=1).first()
    team_a = Team.query.filter_by(id=match.team_a).first()
    team_b = Team.query.filter_by(id=match.team_b).first()
    players_a = Player.query.filter_by(team=team_a.id).all()
    players_b = Player.query.filter_by(team=team_b.id).all()
    stadium = Stadium.query.filter_by(id=match.stadium).first()
    division = Division.query.filter_by(id=match.division).first()
    return jsonify({'teama': {'id': team_a.id,
                              'full_name': team_a.full_name,
                              'short_name': team_a.short_name,
                              'tricot': get_tricot(team_a),
                              'color_for_ui': team_a.color_for_ui,
                              'players': players_schema.dump(players_a),
                              'scores': match.score_a,
                              'fouls': match.fouls_a,
                              'logo_file': team_a.logo_file,
                              'selected_tricot': team_b.selected_tricot

                              },
                    'teamb': {'id': team_b.id,
                              'full_name': team_b.full_name,
                              'short_name': team_b.short_name,
                              'tricot': get_tricot(team_b),
                              'color_for_ui': team_b.color_for_ui,
                              'players': players_schema.dump(players_b),
                              'scores': match.score_b,
                              'fouls': match.fouls_b,
                              'logo_file': team_b.logo_file,
                              'selected_tricot': team_b.selected_tricot
                              },

                    'match': {'id': match.id,
                              'match_length': match.match_length,
                              'seconds': match.seconds,
                              'is_timer_countdown': match.is_timer_countdown,
                              'stadium': stadium_schema.dump(stadium),
                              'date': match.date,
                              'referee': staff_schema.dump(match.referee),
                              'cameraman': staff_schema.dump(match.cameraman),
                              'commentator': staff_schema.dump(match.commentator),
                              'division': division_schema.dump(division)
                              }
                    })


@controller_blueprint.route('/update-value', methods=['POST'])
def update_value():
    if request.method == 'POST':
        value = request.get_json()['value']
        divId = request.get_json()['divId']
        if divId == 'display-fouls-a':
            Match.query.filter_by(actual=1).first().fouls_a = int(value)
        elif divId == 'display-score-a':
            Match.query.filter_by(actual=1).first().score_a = int(value)
        elif divId == 'display-score-b':
            Match.query.filter_by(actual=1).first().score_b = int(value)
        elif divId == 'display-fouls-b':
            Match.query.filter_by(actual=1).first().fouls_b = int(value)
        db.session.commit()
        return jsonify({'value': value})


@controller_blueprint.route('/get-seconds')
def get_seconds():
    seconds = Match.query.filter_by(actual=1).first().seconds
    return jsonify(seconds)


@controller_blueprint.route('/get-actual-match')
def get_actual_match_id():
    actual_match_id = Match.query.filter_by(actual=1).first().id
    return jsonify(actual_match_id)


@controller_blueprint.route('/set-timer-countdown', methods=['GET', 'POST'])
def set_timer_countdown():
    if request.method == 'POST':
        value = request.get_json()['is_timer_countdown']
        Match.query.filter_by(actual=1).first().is_timer_countdown = int(value)
        db.session.commit()
        return jsonify(Match.query.filter_by(actual=1).first().seconds)


@controller_blueprint.route('/get-match-actions/<team_id>')
def get_match_actions(team_id):
    actual_match = matchdata().get_json()['match']
    actual_match_id = actual_match['id']
    match_actions = MatchesData.query.filter_by(match_id=actual_match_id, team_id=team_id).all()
    return match_datas_schema.dump(match_actions)


@controller_blueprint.route('/set-match-actions-non-actual', methods=['POST'])
def set_match_actions_non_actual():
    if request.method == 'POST':
        actual_match_id = matchdata().get_json()['match']['id']
        match_actions = MatchesData.query.filter_by(match_id=actual_match_id).all()
        for action in match_actions:
            action.actual = 0
            db.session.commit()
        return ''


@controller_blueprint.route('/update-match-actions', methods=['POST'])
def update_match_actions():
    if request.method == 'POST':
        response = request.get_json()
        match_data = MatchesData.query.filter_by(id=response['id']).first()
        match_data.time = response['time']
        match_data.player_id = response['player_id']
        match_data.action_id = response['action_id']
        db.session.add(match_data)
        db.session.commit()
        return 'match actions updated'


@controller_blueprint.route('/add-match-action', methods=['POST'])
def add_match_action():
    if request.method == 'POST':
        response = request.get_json()
        actual_match = Match.query.filter_by(actual=1).first()
        seconds = actual_match.seconds
        match_data = MatchesData(
            action_id=response['action_id'],
            player_id=response['player_id'],
            team_id=get_team_id_by_description(response['team'], actual_match),
            time=seconds,
            match_id=actual_match.id,
            actual=1
        )
        db.session.add(match_data)
        db.session.commit()
        return 'match action added'


@controller_blueprint.route('/insert-match-action', methods=['POST'])
def insert_match_action():
    if request.method == 'POST':
        response = request.get_json()
        actual_match = Match.query.filter_by(actual=1).first()
        all_match_data = MatchesData.query.all()
        for data in all_match_data:
            data.actual = 0
        match_data = MatchesData(
            action_id=response['action_id'],
            player_id=response['player_id'],
            team_id=response['team_id'],
            time=response['seconds'],
            match_id=actual_match.id,
            actual=1
        )
        db.session.add(match_data)
        db.session.commit()
        return 'match action added'


def get_team_id_by_description(description, actual_match):
    if description == 'teama':
        return actual_match.team_a
    else:
        return actual_match.team_b


@controller_blueprint.route('/delete-match-action', methods=['POST'])
def delete_match_action():
    action_id = request.get_json()['action_id']
    action = MatchesData.query.filter_by(id=action_id).first()
    db.session.delete(action)
    db.session.commit()
    return ''


@controller_blueprint.route('/get-player/<player_id>')
def get_player(player_id):
    player = Player.query.filter_by(id=player_id).first()
    return player_schema.dump(player)


@timer_blueprint.route('/increment-seconds', methods=['GET', 'POST'])
def increment_seconds():
    if request.method == 'POST':
        value = request.get_json()['value']
        Match.query.filter_by(actual=1).first().seconds += int(value)
        db.session.commit()
        return jsonify(Match.query.filter_by(actual=1).first().seconds)


@controller_blueprint.route('/change-score-a', methods=['POST'])
def change_score_a():
    if request.method == 'POST':
        value = request.get_json()['value']
        Match.query.filter_by(actual=1).first().score_a += int(value)
        db.session.commit()
        return jsonify(Match.query.filter_by(actual=1).first().score_a)


@controller_blueprint.route('/change-score-b', methods=['POST'])
def change_score_b():
    if request.method == 'POST':
        value = request.get_json()['value']
        Match.query.filter_by(actual=1).first().score_b += int(value)
        db.session.commit()
        return jsonify(Match.query.filter_by(actual=1).first().score_b)


@controller_blueprint.route('/change-fouls-a', methods=['POST'])
def change_fouls_a():
    if request.method == 'POST':
        value = request.get_json()['value']
        Match.query.filter_by(actual=1).first().fouls_a += int(value)
        db.session.commit()
        return jsonify(Match.query.filter_by(actual=1).first().fouls_a)


@controller_blueprint.route('/change-fouls-b', methods=['POST'])
def change_fouls_b():
    if request.method == 'POST':
        value = request.get_json()['value']
        Match.query.filter_by(actual=1).first().fouls_b += int(value)
        db.session.commit()
        return jsonify(Match.query.filter_by(actual=1).first().fouls_b)


@controller_blueprint.route('/get-all-teams/<competition_id>')
def get_all_teams(competition_id):
    teams = Team.query.filter_by(competitions=competition_id).order_by(Team.full_name).all()
    return teams_schema.dump(teams)


@controller_blueprint.route('/get-team/<team_id>')
def get_team(team_id):
    team = Team.query.filter_by(id=team_id).first()
    return team_schema.dump((team))


@controller_blueprint.route('/update-lineup', methods=['POST'])
def update_lineup():
    _player = request.get_json()
    player = Player.query.filter_by(id=_player['id']).first()
    player.squad = _player['squad']
    player.default_nr = _player['default_nr']
    player.first_name = _player['first_name']
    player.last_name = _player['last_name']
    player.position = set_position(_player['position'])
    player.captain = _player['captain']
    db.session.commit()
    return jsonify(Player.query.filter_by(id=_player['id']).first())


def set_position(position):
    if position:
        return 'Bramkarz'
    else:
        return ''


@controller_blueprint.route('/update-tricots', methods=['POST'])
def update_tricots():
    if request.method == 'POST':
        _team = request.get_json()
        team = Team.query.filter_by(id=_team['id']).first()
        team.home_color_one = _team['home_color_one']
        team.home_color_two = _team['home_color_two']
        team.home_color_three = _team['home_color_three']
        team.home_tricot_color_number = _team['home_tricot_color_number']
        team.away_color_one = _team['away_color_one']
        team.away_color_two = _team['away_color_two']
        team.away_color_three = _team['away_color_three']
        team.away_tricot_color_number = _team['away_tricot_color_number']
        team.bibs_color = _team['bibs_color']
        team.color_for_ui = _team['color_for_ui']
        team.selected_tricot = _team['selected_tricot']
        db.session.commit()
        return jsonify(Team.query.filter_by(id=_team['id']).first())


def get_tricot(team):
    if team.selected_tricot == 1:
        tricot = [team.home_color_one, team.home_color_two, team.home_color_three][:team.home_tricot_color_number]
    elif team.selected_tricot == 2:
        tricot = [team.away_color_one, team.away_color_two, team.away_color_three][:team.away_tricot_color_number]
    else:
        tricot = [team.bibs_color]
    return tricot


@controller_blueprint.route('/update-time', methods=['POST'])
def update_time():
    if request.method == 'POST':
        seconds = request.get_json()['seconds']
        Match.query.filter_by(actual=1).first().seconds = int(seconds)
        db.session.commit()
        return jsonify(Match.query.filter_by(actual=1).first().seconds)


@controller_blueprint.route('/get_files')
def get_files():
    directory = 'static/video/replays'
    files = [file for file in os.listdir(directory) if file.endswith('.mp4')]
    return {'files': files}


@controller_blueprint.route('/process_file/<filename>')
def process_file(filename):
    replay_name = 'replay.mp4'
    source_path = os.path.join('static/video/replays', filename)
    target_path = os.path.join('static/video/processed', replay_name)

    with open(source_path, 'rb') as source_file, open(target_path, 'wb') as target_file:
        target_file.write(source_file.read())

    return send_file(target_path, as_attachment=True)


@controller_blueprint.route('/actual-match-data/<team>', methods=['GET', 'POST'])
def actual_match_data(team):
    _team_id = matchdata().get_json()[team]['id']
    _team_name = Team.query.filter_by(id=_team_id).first().full_name
    _match_id = get_actual_match_id().get_json()
    _match_data = MatchesData.query.filter_by(match_id=_match_id).filter_by(team_id=_team_id).all()
    match_data = []
    match_data.append(_team_name)
    event_data = []
    for _data in _match_data:
        _player = Player.query.filter_by(id=_data.player_id).first()
        event_data.append({
            'data_id': _data.id,
            'time': sec_to_secmin(_data.time),
            'action_type': set_action_type(_data.action_id),
            'player_id': _player.id,
            'player_first_name': _player.first_name,
            'player_last_name': _player.last_name,
        })
    match_data.append(event_data)

    return jsonify(match_data)


def sec_to_secmin(sec):
    _div = divmod(int(sec), 60)
    secmin = {'minutes': '{:02}'.format(_div[0]), 'seconds': '{:02}'.format(_div[1])}
    return secmin


def set_action_type(action_id):
    _actions = {1: 'G', 2: 'Ż', 3: 'C', 4: 'S', 5: 'T'}
    return _actions[action_id]


@controller_blueprint.route('/prepare-data-to-edit/<int:dataId>')
def prepare_data_to_edit(dataId):
    _match_data = MatchesData.query.filter_by(id=dataId).first()
    data = {}
    _data = {
        'data_id': _match_data.id,
        'time': sec_to_secmin(_match_data.time),
        'action_id': _match_data.action_id,
        'player_id': _match_data.player_id,
        'team_id': _match_data.team_id,
        'match_id': _match_data.match_id
    }
    data.update({'event': _data})
    _match = Match.query.filter_by(id=data['event']['match_id']).first()
    _teams_ids = {'normal': _match_data.team_id}
    if int(_match_data.team_id) == int(_match.team_a):
        _teams_ids.update({'og': _match.team_b})
    else:
        _teams_ids.update({'og': _match.team_a})
    data.update({'teams_ids': _teams_ids})
    _actions_types = MatchAction.query.all()
    _actions = {}
    for _action in _actions_types:
        _actions.update({_action.id: _action.desc_polish})
    data.update({'actions': _actions})
    _players = {'normal': players_schema.dump(Player.query.filter_by(team=_teams_ids['normal']).all()),
                'og': players_schema.dump(Player.query.filter_by(team=_teams_ids['og']).all())
                }
    data.update({'players': _players})
    return jsonify(data)


@controller_blueprint.route('/update-data/<int:data_id>', methods=['PUT'])
def update_data(data_id):
    try:
        # Pobierz dane z żądania
        data = request.get_json()

        # Pobierz obiekt z bazy danych
        obj_to_update = MatchesData.query.get(data_id)

        # Zaktualizuj pola obiektu
        obj_to_update.time = data['time']
        obj_to_update.action_id = data['action']
        obj_to_update.player_id = data['player']

        # Przekonwertuj czas z minut i sekund na sekundy
        time_in_seconds = data['time']
        obj_to_update.time = time_in_seconds

        # Zapisz zmiany w bazie danych
        db.session.commit()

        return jsonify({'message': 'Dane zaktualizowane pomyślnie'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@settings_blueprint.route('/matches-settings', methods=['GET'])
def matches_settings():
    matches = Match.query.all()
    _matches = matches_schema.dump(matches)
    for _match in _matches:
        _team_a = Team.query.filter_by(id=_match['team_a']).first()
        _team_b = Team.query.filter_by(id=_match['team_b']).first()
        try:
            _match.update({'team_a': _team_a})
            _match.update({'team_b': _team_b})
        except:
            print('falseeee', flush=True)
    return render_template('matches-settings.html', matches=matches_schema.dump(_matches))


@settings_blueprint.route('/creatematch', methods=['GET', 'POST'])
def creatematch():
    form = MatchForm(request.form)
    form.competitions.default = 1
    form.process()

    form_content = CEM.form_content

    # if request.method == 'POST' and form.validate():
    if request.method == 'POST':
        team_a = request.form.get('team_a')
        team_b = request.form.get('team_b')
        match_length = request.form.get('match_length')
        is_actual = request.form.get('is_actual')
        cameramen = request.form.get('cameramen')
        commentators = request.form.get('commentators')
        referees = request.form.get('referees')
        stadium = request.form.get('stadium')
        date_time = request.form.get('date_time')
        competitions = request.form.get('competitions')
        division = request.form.get('division')

        # Utwórz nowy mecz
        new_match = Match(team_a=team_a
                          , team_b=team_b
                          , match_length=match_length
                          , stadium=stadium
                          , date=date_time
                          , competitions=competitions
                          , division=division)
        if is_actual:
            db.session.query(Match).update({Match.actual: 0})
            new_match.actual = 1
        db.session.add(new_match)
        db.session.flush()

        # # Dodaj cameramen do meczu
        for cameraman_id in cameramen:
            cameraman = Staff.query.get(cameraman_id)
            if cameraman:
                new_match.cameraman.append(cameraman)

        for commentator_id in commentators:
            commentator = Staff.query.get(commentator_id)
            if commentator:
                new_match.commentator.append(commentator)

        for referee_id in referees:
            referee = Staff.query.get(referee_id)
            if referee:
                new_match.referee.append(referee)

        # Zapisz zmiany w bazie danych
        db.session.commit()

        return redirect(url_for('monitor.index'))

    return render_template('creatematch.html', form=form, form_content=form_content)


@settings_blueprint.route('/edit-match/<int:match_id>', methods=['GET', 'POST'])
def edit_match(match_id):
    if match_id == 0:
        match_id = Match.query.filter_by(actual=1).first().id
    match = Match.query.get(match_id)

    if not match:
        return 'Mecz o podanym identyfikatorze nie istnieje'

    cameramen = MatchCameraman.query.filter_by(match_id=match_id).all()
    referees = MatchReferee.query.filter_by(match_id=match_id).all()
    commentators = MatchCommentator.query.filter_by(match_id=match_id).all()
    selected_cameramen = [cameraman.staff_id for cameraman in cameramen]
    selected_referees = [referee.staff_id for referee in referees]
    selected_commentators = [commentator.staff_id for commentator in commentators]
    date_time = Match.query.filter_by(id=match_id).first().date

    form = MatchForm(obj=match)
    form.date_time = MatchForm(date_time=date_time)

    form_content = CEM.form_content

    if request.method == 'POST':
        team_a = form.team_a.data
        team_b = form.team_b.data
        match_length = form.match_length.data
        is_actual = form.is_actual.data
        cameramen = form.cameramen.data
        commentators = form.commentators.data
        referees = form.referees.data
        stadium = form.stadium.data
        date_time = form.date_time.data

        # Utwórz nowy mecz
        # match = Match(team_a=team_a, team_b=team_b, match_length=match_length, stadium=stadium, date=date_time)
        if is_actual:
            db.session.query(Match).update({Match.actual: 0})
            match.actual = 1
        # db.session.flush()
        match.cameraman.clear()
        match.commentator.clear()
        match.referee.clear()

        # # Dodaj cameramen do meczu
        for cameraman_id in cameramen:
            cameraman = Staff.query.get(cameraman_id)
            if cameraman:
                match.cameraman.append(cameraman)

        for commentator_id in commentators:
            commentator = Staff.query.get(commentator_id)
            if commentator:
                match.commentator.append(commentator)

        for referee_id in referees:
            referee = Staff.query.get(referee_id)
            if referee:
                match.referee.append(referee)

        # Aktualizacja danych meczu
        # form.populate_obj(match)

        # Zapisanie zmian w bazie danych
        db.session.add(match)
        db.session.commit()

        return redirect(url_for('monitor.index'))

    return render_template('edit_match.html', form=form, match=match, selected_commentators=selected_commentators,
                           selected_cameramen=selected_cameramen, selected_referees=selected_referees,
                           form_content=form_content)


@settings_blueprint.route('/matches')
def matches():
    matches = Match.query.all()
    _matches = []
    for match in matches:
        _match = match_schema.dump(match)
        if is_future(_match['date']):
            team_a = Team.query.filter_by(id=_match['team_a']).first()
            team_b = Team.query.filter_by(id=_match['team_b']).first()
            _match.update({'team_a': team_schema.dump(team_a), 'team_b': team_schema.dump(team_b)})
            _matches.append(_match)
    return render_template('matches.html', matches=_matches)


def is_future(date_time):
    _date_time = datetime.strptime(date_time, "%Y-%m-%d %H:%M")
    if _date_time > datetime.now():
        return True
    else:
        return False


@settings_blueprint.route('/competition-teams')
def competition_teams():
    _competition_teams = Team.query.filter_by(competitions=1).order_by('full_name')
    return render_template('competition-teams.html', teams=_competition_teams)


@settings_blueprint.route('/edit-team/<int:team_id>', methods=['GET', 'POST'])
def edit_team(team_id):
    if request.method == 'POST':
        player_data = request.form.to_dict()
        save_data_to_database(player_data)
        return redirect(url_for('settings.edit_team', team_id=team_id))
    team = Team.query.filter_by(id=team_id).first()
    players = Player.query.filter_by(team=team_id)  # Pobierz graczy z bazy danych
    return render_template('edit_team.html', team_id=team_id, team=team, players=players)


def save_data_to_database(player_data):
    players_ids = []
    players_data = {}

    for key, value in player_data.items():
        # Sprawdź, czy pole zawiera dane gracza
        if '[' in key and ']' in key:
            player_id = key.split('[')[0].split('_')[1]
            players_ids.append(player_id)
    players_ids = set(players_ids)

    for plyr_id in players_ids:
        _plyr_data = {}

        for key, value in player_data.items():
            if f'player_{plyr_id}' in key:
                key = key.split('[')[1][:-1]
                _plyr_data.update({key: value})
        players_data.update({plyr_id: _plyr_data})

    # # Zapisz dane do bazy danych
    for key in players_data:
        player = Player.query.filter_by(id=key).first()

        if player:
            # Aktualizuj dane istniejącego gracza
            player.squad = players_data[key].get('squad', '0')
            player.default_nr = players_data[key].get('default_nr', 0)
            player.first_name = players_data[key].get('first_name', 'Imię')
            player.last_name = players_data[key].get('last_name', 'Nazwisko')
            player.position = players_data[key].get('position', 0)
            player.captain = players_data[key].get('captain', 0)

        db.session.commit()

@settings_blueprint.route('/set-actual-match', methods=['POST'])
def set_actual_match():
    try:
        # Pobierz dane z żądania
        data = request.get_json()
        match_id = data['matchId']
        # Pobierz obiekt z bazy danych
        _all_matches = Match.query.all()
        for _match in _all_matches:
            _match.actual = 0
        _actual_match = Match.query.filter_by(id=match_id).first()
        _actual_match.actual = 1

        # Zapisz zmiany w bazie danych
        db.session.commit()

        return jsonify({'message': 'Dane zaktualizowane pomyślnie'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@settings_blueprint.route('/show_empty_result/<division>', methods=['GET'])
def show_empty_result(division):
    # Skonstruuj pełną ścieżkę do pliku JSON
    json_file_path = os.path.join(settings_blueprint.root_path, 'static', 'json', 'matches.json')

    try:
        # Odczytaj dane z pliku JSON
        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)

        # Wybierz tylko te wpisy, gdzie 'result' jest pusty
        empty_result_data = [entry for entry in data if entry['result'] == '']

        # Renderuj szablon HTML z danymi
        return render_template('update_results.html', data=empty_result_data, division=division)

    except FileNotFoundError:
        return "Error: File 'matches.json' not found."

@settings_blueprint.route('/show-matches-by-date/<division>', methods=['GET'])
def show_matches_by_date(division):
    print(division, flush=True)
    # Pobieramy parametr 'days' z zapytania lub używamy domyślnej wartości +1/-1 dni
    days = int(request.args.get('days', 14))

    # Obliczamy daty
    today = datetime.now()
    start_date = today - timedelta(days=days)
    end_date = today + timedelta(days=days)

    # Pobieramy dane z pliku matches.json
    with open(f'static/json/matches-{division}.json', 'r') as json_file:
        data = json.load(json_file)

    # Filtrujemy dane, aby pokazać tylko te w określonym przedziale dat
    filtered_data = [entry for entry in data if start_date <= datetime.strptime(entry['date'], '%Y-%m-%d %H:%M:%S') <= end_date]

    return render_template('update_results.html', data=filtered_data, division=division)

@settings_blueprint.route('/save-result/<division>', methods=['POST'])
def save_result(division):
    # Pobierz dane JSON przesłane z przeglądarki
    match_data = request.json
    print(match_data, flush=True)

    # Aktualizuj plik JSON
    with open(f'static/json/matches-{division}.json', 'r') as json_file:
        data = json.load(json_file)
    for entry in data:
        if entry['id'] == int(match_data['id']):
            # Aktualizuj wartości 'result' w zależności od przesłanych danych
            if match_data['result_home'] == '' or match_data['result_away'] == '':
                entry['result'] = ''
                entry['actual'] = match_data['actual']
            else:
                entry['result'] = [match_data['result_home'], match_data['result_away']]
                entry['actual'] = match_data['actual']

    # Zapisz zaktualizowane dane z powrotem do pliku JSON
    with open(f'static/json/matches-{division}.json', 'w') as json_file:
        json.dump(data, json_file, indent=2)

    return redirect(url_for('settings.show_matches_by_date', division=division))

@settings_blueprint.route('/generate_base_table/<division>', methods=['GET', 'POST'])
def generate_base_table(division):
    if request.method == 'POST':
        _actual_played_teams = request.get_json()
        if division == 'b':
            table_generator = TableGenerator(division=division)

            virtual_table = table_generator.generate_table(_actual=True, _divided=True)
            _virtual_tbl = [[x['team_name'], x['points'], x['actual']] for x in virtual_table]
            # for item in _virtual_tbl:
            #     print('v_tab:', item, flush=True)
            for item in _virtual_tbl:
                if item[0] in _actual_played_teams:
                    item[2] = True
            with open(f'static/json/virtual-table-{division}.json', 'w') as json_file:
                json.dump(_virtual_tbl, json_file, indent=2)

            base_table = table_generator.generate_table(_divided=True)
            _base_tbl = [[x['team_name'], x['points'], x['actual']] for x in base_table]
            # for item in _base_tbl:
                # print('b_tab:', item, flush=True)
            for item in _base_tbl:
                if item[0] in _actual_played_teams:
                    item[2] = True

            with open(f'static/json/base-table-{division}.json', 'w') as json_file:
                json.dump(_base_tbl, json_file, indent=2)
        else:

            table_generator = TableGenerator(division=division)

            virtual_table = table_generator.generate_table(_actual=True)
            _virtual_tbl = [[x['team_name'], x['points'], x['actual']] for x in virtual_table]
            _actual_played_teams = [team['team_name'] for team in virtual_table if team['actual']]

            with open(f'static/json/virtual-table-{division}.json', 'w') as json_file:
                json.dump(_virtual_tbl, json_file, indent=2)

            base_table = table_generator.generate_table()
            _base_tbl = [[x['team_name'], x['points'], x['actual']] for x in base_table]
            for item in _base_tbl:
                if item[0] in _actual_played_teams:
                    item[2] = True

            with open(f'static/json/base-table-{division}.json', 'w') as json_file:
                json.dump(_base_tbl, json_file, indent=2)

        return jsonify({'status': 'success', 'message': 'Plik base-table.json został wygenerowany.'})


@settings_blueprint.route('/generate_virtual_table/<division>', methods=['GET'])
def generate_virtual_table(division):
    table_generator = TableGenerator(division=division)
    table = table_generator.generate_table()
    _tbl = [[x['team_name'], x['points']] for x in table]
    with open(f'static/json/virtual-table-{division}.json', 'w') as json_file:
        json.dump(_tbl, json_file, indent=2)

    return jsonify({'status': 'success', 'message': 'Plik virtual-table.json został wygenerowany.'})



@obswebsocketpy_blueprint.route('/ws-controller')
def ws_controller():
    return render_template('ws-controller.html')

@obswebsocketpy_blueprint.route('/showscene/<scenename>')
def show_scene(scenename):
    obs_ws = current_app.config['obs_ws']
    obs_ws.show_scene(scenename)
    return redirect(url_for('obswebsocketpy.ws_controller'))

@obswebsocketpy_blueprint.route('/goal-sequence')
def goal_sequence():
    obs_ws = current_app.config['obs_ws']
    obs_ws.save_replay_buffer()
    return redirect(url_for('obswebsocketpy.ws_controller'))

@obswebsocketpy_blueprint.route('/replay-sequence/<typeofaction>')
def replay_sequence(typeofaction):
    obs_ws = current_app.config['obs_ws']
    obs_ws.save_replay(typeofaction)
    return redirect(url_for('obswebsocketpy.ws_controller'))

@obswebsocketpy_blueprint.route('/play-replay-sequence')
def play_replay_sequence():
    obs_ws = current_app.config['obs_ws']
    obs_ws.play_replay()
    return redirect(url_for('obswebsocketpy.ws_controller'))

@obswebsocketpy_blueprint.route('/start-stop-stream')
def start_stop_stream():
    obs_ws = current_app.config['obs_ws']
    obs_ws.start_stop_stream()
    return redirect(url_for('obswebsocketpy.ws_controller'))

@obswebsocketpy_blueprint.route('/showbanner')
def show_banner():
    obs_ws = current_app.config['obs_ws']
    obs_ws.show_banner()
    return redirect(url_for('obswebsocketpy.ws_controller'))

@obswebsocketpy_blueprint.route('/showaction')
def show_action():
    obs_ws = current_app.config['obs_ws']
    obs_ws.show_action()
    return redirect(url_for('obswebsocketpy.ws_controller'))

@obswebsocketpy_blueprint.route('/showvirtualtable/<division>')
def show_virtual_table(division):
    obs_ws = current_app.config['obs_ws']
    obs_ws.show_virtual_table(division)
    return redirect(url_for('obswebsocketpy.ws_controller'))

if __name__ == '__main__':
    create_app().run(port=5555, use_reloader=False, debug=True)
