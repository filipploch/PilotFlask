import json
import requests
from utils.createeditmatch import CreateEditMatch
from utils.table_generator import TableGenerator
from utils.players_updater import NALFplayersUpdater
from utils.nalf_team_scraper import NALFteamScraper
from utils.nalf_matches_scraper import NALFmatchesScraper
from utils.nalf_league_matches_scraper import NALFleagueMatchesScraper
from utils.nalf_table_scraper import NALFtableScraper
from utils.json_file_generator import JSONFileGenerator
from utils.ball_tracker import BallTracker
from utils.file_utils import copy_file, get_video_length, create_folder
from env.settings import get_settings
from flask import Flask, render_template, jsonify, current_app, Blueprint, request, redirect, url_for, send_file
from flask_cors import CORS
from datetime import datetime, timedelta
from models import Team, Match, Player, MatchesData, Stadium, Staff, MatchCommentator, MatchCameraman, MatchReferee, \
    MatchAction, Division, LeagueMatches, Competitions, TimerDisplayMode, Period
from database import db
from schemas import ma, player_schema, players_schema, match_datas_schema, team_schema, teams_schema, match_data_schema, \
    stadium_schema, matches_schema, staff_schema, match_schema, division_schema, league_match_schema, \
    league_matches_schema, timer_display_mode_schema
import re
from timer import Timer
from replays_timer import ReplaysTimer
from obswebsocketpy import OBSWebsocket
from flask_apscheduler import APScheduler
from collections import OrderedDict
from forms import MatchForm
from forms import CreateTeamForm
import os
import shutil
from threading import Thread
from socketiopy import socketio
from video_recorder import VideoRecorder
from time import sleep

stream_blueprint = Blueprint('stream', __name__)
panel_blueprint = Blueprint('panel', __name__)
timer_blueprint = Blueprint('timer', __name__)
settings_blueprint = Blueprint('settings', __name__)
obswebsocketpy_blueprint = Blueprint('obswebsocketpy', __name__)
socialmedia_blueprint = Blueprint('socialmedia', __name__)


# apscheduler = APScheduler()


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.DevelopmentConfig')
    app.config['SECRET_KEY'] = 'hardsecretkey'

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///futsal.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.register_blueprint(stream_blueprint)
    app.register_blueprint(panel_blueprint)
    app.register_blueprint(timer_blueprint)
    app.register_blueprint(settings_blueprint)
    app.register_blueprint(obswebsocketpy_blueprint)
    app.register_blueprint(socialmedia_blueprint)
    db.init_app(app)
    ma.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    app.config['SOCKETIO'] = socketio
    timer = Timer(app)
    app.config['TIMER'] = timer
    obs_ws = OBSWebsocket(app)
    app.config['obs_ws'] = obs_ws
    app.config['MATCHDATA'] = get_match_data(app)
    app.config['MATCH_IDENTIFIER'] = get_match_identifier(app)
    app.config['RECORDING_START_TIME'] = get_recording_start_time(app)
    replays_timer = ReplaysTimer(app)
    app.config['REPLAYS_TIMER'] = replays_timer
    socketio.start_background_task(timer.control_timer)
    socketio.start_background_task(obs_ws.connect_websocket, app)
    # socketio.start_background_task(video_recorder.record_video)
    app.config['BANNER_FOLDER'] = os.path.join(app.root_path, 'templates', 'banner')

    CORS(app)
    return app


def get_period_type_name(periods_nr):
    match periods_nr:
        case 2:
            return 'połowa'
        case 3:
            return 'tercja'
        case 4:
            return 'kwarta'
        case default:
            return ''


def get_division_id_by_letter(letter):
    with current_app.app_context():
        if letter == 'a':
            return current_app.config['GROUP_A']
        elif letter == 'b':
            return current_app.config['GROUP_B']
        else:
            return current_app.config['GROUP_A']


def get_match_identifier(app, match=None):
    with app.app_context():
        if match is None:
            _match = Match.query.filter_by(actual=1).first()
        else:
            _match = match
        try:
            _date = _match.date.split()[0]
            _time = _match.date.split()[1].replace(':', '-')
            _team_a = team_schema.dump(Team.query.filter_by(id=_match.team_a).first())['short_name']
            _team_b = team_schema.dump(Team.query.filter_by(id=_match.team_b).first())['short_name']
            return f'{_date}_{_time}_{_team_a}x{_team_b}'
        except:
            return '0000-00-00_00-00_TEAxTEB'


def get_recording_start_time(app):
    with app.app_context():
        _recording_filename = f"C1_{app.config['MATCH_IDENTIFIER']}_output.mp4"
        _directory = app.config['REPLAYS_FILES_DIRECTORY']
        _video_path = f"{_directory}\\{_recording_filename}"
        if os.path.exists(_video_path):
            print('video_length:', get_video_length(_video_path))
            return get_video_length(_video_path)
        print('video_length:', 0)
        return 0


@settings_blueprint.route('/nalf')
def nalf():
    _actual_match = Match.query.filter_by(actual=1).first()
    if not _actual_match:
        return redirect(url_for('settings.matches'))
    _teams_names = {'teama': Team.query.filter_by(id=_actual_match.team_a).first().full_name,
                    'teamb': Team.query.filter_by(id=_actual_match.team_b).first().full_name}
    return render_template('index.html', actualMatch=_actual_match, teamsNames=_teams_names)


@settings_blueprint.route('/')
def index():
    _actual_match = Match.query.filter_by(actual=1).first()
    if not _actual_match:
        return redirect(url_for('settings.failure_actual_match'))
    _teams_names = {'teama': Team.query.filter_by(id=_actual_match.team_a).first().full_name,
                    'teamb': Team.query.filter_by(id=_actual_match.team_b).first().full_name}
    return render_template('staff.html', actualMatch=_actual_match, teamsNames=_teams_names)


@settings_blueprint.route('/failure-actual-match')
def failure_actual_match():
    return render_template('failure-actual-match.html')


@timer_blueprint.route('/control-timer', methods=['POST'])
def control_timer():
    control_variable = request.get_json()['control_variable']
    Match.query.filter_by(actual=1).first().is_timer_active = int(control_variable)
    db.session.commit()
    with current_app.app_context():
        current_app.config['MATCHDATA']['match']['is_timer_active'] = int(control_variable)
    return jsonify({'is_timer_active': Match.query.filter_by(actual=1).first().is_timer_active})


@stream_blueprint.route('/start')
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


@stream_blueprint.route('/start-x')
def start_x():
    _match = matchdata().get_json()
    _match_details = _match['match']
    _match_details['date'] = decode_date(_match_details['date'])[1:3]
    _logos = {'logo_a': _match['teama']['logo_file'],
              'logo_b': _match['teamb']['logo_file']}
    _teams = {'team_a': Team.query.filter_by(id=_match['teama']['id']).first(),
              'team_b': Team.query.filter_by(id=_match['teamb']['id']).first()
              }
    return render_template('start-x.html', logos=_logos, teams=_teams, match=_match_details)


@stream_blueprint.route('/match-preview')
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


@stream_blueprint.route('/match-preview-x26')
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


@stream_blueprint.route('/match-preview-x27')
def match_preview_x27():
    _match = matchdata().get_json()
    _match_details = _match['match']
    _match_details['date'] = decode_date(_match_details['date'])[1:3]
    _logos = {'logo_a': _match['teama']['logo_file'],
              'logo_b': _match['teamb']['logo_file']}
    _teams = {'team_a': Team.query.filter_by(id=_match['teama']['id']).first(),
              'team_b': Team.query.filter_by(id=_match['teamb']['id']).first()
              }
    return render_template('match-preview-x27.html', logos=_logos, teams=_teams, match=_match_details)


def decode_date(date_to_decode):
    re_pattern = '^(\d{4}-\d{2}-\d{2}) (\d{1,2}:\d{2})$'
    return re.split(re_pattern, date_to_decode)


@stream_blueprint.route('/match')
def match():
    with current_app.app_context():
        _matchdata = matchdata().get_json()
        _seconds = current_app.config['TIME_DATA']['seconds']
        _added_seconds = current_app.config['TIME_DATA']['added_seconds']
        _time_data = {'seconds': _seconds, 'added_seconds': _added_seconds}
        return render_template('match.html', matchdata=_matchdata, time_data=_time_data)


@stream_blueprint.route('/action')
def action():
    _action = MatchesData.query.filter_by(actual=1).first()
    _match = Match.query.filter_by(actual=1).first()
    # _periods_end_times = get_periods_end_times(_match)
    # _current_period = get_current_period(_match.current_period)
    _current_period = _match.current_period
    _time_limit = Period.query.filter_by(id=_current_period).first().end_time
    if _action:
        _time = get_action_time(_action.seconds, _action.added_seconds, _time_limit)

        return render_template('action.html', action=match_data_schema.dump(_action), time_minutes=_time)
    return redirect(url_for('stream.match'))


def get_action_time(seconds, added_seconds, time_limit):
    if seconds == time_limit and added_seconds == 0:
        _action_time = str(time_limit / 60)
    elif seconds > time_limit:
        _added_time = (seconds - time_limit) / 60 + 1
        _action_time = f'{str(time_limit / 60)} +{_added_time}'
    else:
        _action_time = str(seconds / 60 + 1)
    return _action_time


@stream_blueprint.route('/teams')
def teams():
    _match = matchdata().get_json()
    _goals = {'goals_a': MatchesData.query.filter_by(match_id=_match['match']['id']
                                                     , team_id=_match['teama']['id']
                                                     , action_id=1
                                                     , is_hided=0
                                                     ).all(),
              'goals_b': MatchesData.query.filter_by(match_id=_match['match']['id']
                                                     , team_id=_match['teamb']['id']
                                                     , action_id=1
                                                     , is_hided=0
                                                     ).all(),
              'own_goals_a': MatchesData.query.filter_by(match_id=_match['match']['id']
                                                         , team_id=_match['teamb']['id']
                                                         , action_id=4
                                                         , is_hided=0
                                                         ).all(),
              'own_goals_b': MatchesData.query.filter_by(match_id=_match['match']['id']
                                                         , team_id=_match['teama']['id']
                                                         , action_id=4
                                                         , is_hided=0
                                                         ).all()
              }

    _strikers = {'strikers_a': get_strikers(_goals['goals_a'] + _goals['own_goals_b']),
                 'strikers_b': get_strikers(_goals['goals_b'] + _goals['own_goals_a'])}
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


@stream_blueprint.route('/lineup/<team>')
def lineup(team):
    _team_id = matchdata().get_json()[team]['id']
    _team = Team.query.filter_by(id=_team_id).first()
    _lineup = [player for player in _team.players if player.squad]
    _logo = _team.logo_file
    return render_template('lineup.html', _lineup=_lineup, _logo=_logo)


@stream_blueprint.route('/table')
def table():
    return render_template('table.html')


@stream_blueprint.route('/results')
def results():
    return render_template('results.html')


@stream_blueprint.route('/controller-lineup/<team>')
def panel_lineup(team):
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


@stream_blueprint.route('/controller-lineup-edit/<team>')
def panel_lineup_edit(team):
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


@stream_blueprint.route('/end-screen')
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


@stream_blueprint.route('/virtualtable/<division>')
def virtualtable(division):
    _division = division
    json_file_base_table_path = os.path.join(settings_blueprint.root_path, 'static', 'json',
                                             f'base-table-{division}.json')
    json_file_virtual_table_path = os.path.join(settings_blueprint.root_path, 'static', 'json',
                                                f'virtual-table-{division}.json')

    # Odczytaj dane z pliku JSON
    with open(json_file_base_table_path, 'r') as json_file:
        data_b = json.load(json_file)

    # Odczytaj dane z pliku JSON
    with open(json_file_virtual_table_path, 'r') as json_file:
        data_v = json.load(json_file)

    short_names = {'Brotherm': 'Brotherm',
                   'MK Team': 'MK Team',
                   'Ukrainian Legion': 'Legion',
                   'IGLOMEN&RodzinneRestauracje': 'IGLOMEN&RR',
                   'Boanerges': 'Boanerges',
                   'eNHa': 'eNHa',
                   'DRUGony': 'DRUGony',
                   'Drink Team': 'Drink Team',
                   'Trivium Słomniki Warriors': 'Warriors',
                   'WKS Futsal Team': 'WKS',
                   'Amiz Transport Złote Chłopaki': 'Złote Chłopaki',
                   'Żarłacze': 'Żarłacze',
                   'Galactik Futsal': 'Galactik',
                   'Nowy Ład': 'Nowy Ład',
                   'Laga Bonito': 'Laga Bonito',
                   'Hattrick': 'Hattrick',
                   'eNHa II': 'eNHa II',
                   'Popalone Styki': 'Popalone Styki',
                   'OIA Kraków': 'Kraków',
                   'OIA Bielsko-Biała': 'Bielsko-Biała',
                   'OIA Gdańsk': 'Gdańsk',
                   'OIA Katowice': 'Katowice',
                   'OIA Łódź': 'Łódź',
                   'OIA Poznań': 'Poznań',
                   'OIA Bydgoszcz': 'Bydgoszcz',
                   'OIA Warszawa': 'Warszawa',
                   'OIA Wrocław-Opole': 'Wrocław-Opole',
                   'OIA Szczecin': 'Szczecin',
                   'Nowohucki Klub Sportowy': 'Nowohucki KS'
                   }
    _base_table = data_b
    _base_table = [[actual,
                    nazwa,
                    wartosc,
                    promo,
                    group] for actual, nazwa, wartosc, promo, group in _base_table]
    _virtual_table = data_v
    _virtual_table = [[actual,
                       nazwa,
                       wartosc,
                       promo,
                       group] for actual, nazwa, wartosc, promo, group in _virtual_table]
    return render_template('virtualtable.html', division=division.upper(), base_table=_base_table,
                           virtual_table=_virtual_table)


def _get_short_team_name(full_name):
    team = Team.query.filter_by(full_name=full_name).first()
    return team.short_name


@stream_blueprint.route('/show-stats/<team>')
def show_stats(team):
    with open(f'static/json/match-stats-{team}.json', 'r') as json_file:
        _data = json.load(json_file)
    _team_id = matchdata().get_json()[team]['id']
    _team = Team.query.filter_by(id=_team_id).first()
    _logo = _team.logo_file
    return render_template('statistics.html', data=_data, logo=_logo, team=team)


@stream_blueprint.route('/render-statistics/<stats_content>', methods=['GET'])
def render_statistics(stats_content):
    obs_ws = current_app.config['obs_ws']
    current_scene = obs_ws.get_current_scene()
    if current_scene['currentProgramSceneName'] == 'STATYSTYKI_A':
        team = 'teama'
    elif current_scene['currentProgramSceneName'] == 'STATYSTYKI_B':
        team = 'teamb'
    else:
        return jsonify({'message': 'no team!'})
    with open(f'static/json/match-stats-{team}.json', 'r') as json_file:
        _data = json.load(json_file)
        # print('_data:', _data)
    rendered_html = render_template(f'statistics-{stats_content}.html', data=_data)
    # print('rendered_html:', rendered_html)
    with open(f'static/txt/statistics-{team}.txt', 'w', encoding='utf-8') as txt_file:
        txt_file.write(rendered_html)

    return jsonify({'message': 'OK'})


def prepare_data_to_render(data, title):
    data['title'] = title
    return data


@stream_blueprint.route('/render-round-data/<division_id>', methods=['GET'])
def render_round_data(division_id):
    _actual_match = Match.query.filter_by(actual=1).first()
    _table_data = generate_table(division_id)
    current_date = datetime.strptime(_actual_match.date, "%Y-%m-%d %H:%M")
    _matches = LeagueMatches.query.filter_by(division_id=division_id).filter(
        LeagueMatches.date.between(current_date - timedelta(days=1), current_date + timedelta(days=1))
    ).all()
    for _data in _table_data:
        print(_data)
    data = {
        'competition_name': Division.query.filter_by(id=division_id).first().name,
        'title': '',
        'results': _matches,
        'table': _table_data
    }
    _table = render_template('league-table-template.html', data=prepare_data_to_render(data, 'Tabela'))
    with open(f'templates/table.html', 'w', encoding='utf-8') as txt_file:
        txt_file.writelines(_table)
    _results = render_template('league-results-template.html', data=prepare_data_to_render(data, 'Wyniki'))
    with open(f'templates/results.html', 'w', encoding='utf-8') as txt_file:
        txt_file.writelines(_results)
    return jsonify({'message': 'OK'})


def prepare_table(data_list):
    transformed_data = []
    for sublist in data_list:
        for dictionary in sublist:
            team_name = list(dictionary.keys())[0]
            team_data = dictionary[team_name]
            new_dict = {'name': team_name}
            new_dict.update(team_data)
            transformed_data.append(new_dict)
    return transformed_data


# @stream_blueprint.errorhandler(Exception)
# def handle_error(error):
#     # print(error)
#     _error = str(error).split(' ')[0]
#     return render_template('error.html', error=_error)
#
#
# @stream_blueprint.route('/raise-error')
# def raise_error():
#     abort(500)


@stream_blueprint.route('/playoffs')
def playoffs():
    with open(f'static/json/playoffs.json', 'r') as json_playoffs_file:
        json_data = json.load(json_playoffs_file)
    _data = {
        'json_data': json_data
    }
    return render_template('playoffs.html', data=_data)


@stream_blueprint.route('/charts')
def charts():
    return render_template('charts.html')


@panel_blueprint.route('/panel')
def panel():
    _matchdata = matchdata().get_json()
    _seconds = current_app.config['TIME_DATA']['seconds']
    _added_seconds = current_app.config['TIME_DATA']['added_seconds']
    _time_data = {'seconds': _seconds, 'added_seconds': _added_seconds}
    return render_template('panel.html', matchdata=_matchdata, time_data=_time_data)


@panel_blueprint.route('/matchdata')
def matchdata():
    _matchdata = get_match_data(current_app)
    return jsonify(current_app.config['MATCHDATA'])


def get_match_data(app):
    with app.app_context():
        match = Match.query.filter_by(actual=1).first()
        team_a = Team.query.filter_by(id=match.team_a).first()
        team_b = Team.query.filter_by(id=match.team_b).first()
        players_a = Player.query.filter_by(team=team_a.id).all()
        players_b = Player.query.filter_by(team=team_b.id).all()
        stadium = Stadium.query.filter_by(id=match.stadium).first()
        division = Division.query.filter_by(id=match.division).first()
        app.config['MATCHDATA'] = {'teama':
                                       {'id': team_a.id,
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
                                   'teamb':
                                       {'id': team_b.id,
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

                                   'match':
                                       {'id': match.id,
                                        'periods': match.periods,
                                        'period_length': match.period_length,
                                        'is_added_time_allowed': match.is_added_time_allowed,
                                        'extra_time_periods': match.extra_time_periods,
                                        'extra_time_period_length': match.extra_time_period_length,
                                        # 'periods_end_times': get_periods_end_times(match),
                                        'current_period': match.current_period,
                                        'period_time_limit': get_period_time_limit(match),
                                        'is_timer_active': match.is_timer_active,
                                        'panel_timer_display_mode':
                                            get_timer_display_mode(match.panel_timer_display_mode),
                                        'is_panel_timer_ascending':
                                            get_is_timer_ascending(match, match.is_panel_timer_ascending),
                                        'stream_timer_display_mode':
                                            get_timer_display_mode(match.stream_timer_display_mode),
                                        'is_stream_timer_ascending':
                                            get_is_timer_ascending(match, match.is_stream_timer_ascending),
                                        'stadium': stadium_schema.dump(stadium),
                                        'date': match.date,
                                        'referee': staff_schema.dump(match.referee),
                                        'cameraman': staff_schema.dump(match.cameraman),
                                        'commentator': staff_schema.dump(match.commentator),
                                        'division': division_schema.dump(division)
                                        }
                                   }
        return app.config['MATCHDATA']


def get_timer_display_mode(display_mode_id):
    display_mode_format = TimerDisplayMode.query.filter_by(id=display_mode_id).first().format
    return display_mode_format


# def get_current_period(current_period):
#     if current_period:
#         return current_period
#     return 1


def get_is_timer_ascending(match, db_value):
    if match.is_added_time_allowed:
        return 1
    return db_value


# def get_periods_end_times(match):
#     periods_end_times = []
#     _time = 0
#     base_periods_number = match.periods
#     base_period_length = match.period_length
#     extra_periods_number = match.extra_time_periods
#     extra_period_length = match.extra_time_period_length
#     for period in range(base_periods_number):
#         _time += base_period_length
#         periods_end_times.append(_time)
#     for period in range(extra_periods_number):
#         _time += extra_period_length
#         periods_end_times.append(_time)
#     return periods_end_times


def get_period_time_limit(match):
    print(match_schema.dump(match))
    print(match.current_period)
    return Period.query.filter_by(id=match.current_period).first().end_time


@panel_blueprint.route('/update-value', methods=['POST'])
def update_value():
    if request.method == 'POST':
        with current_app.app_context():
            value = request.get_json()['value']
            divId = request.get_json()['divId']
            if divId == 'fouls-a-value':
                Match.query.filter_by(actual=1).first().fouls_a = int(value)
            elif divId == 'score-a-value':
                Match.query.filter_by(actual=1).first().score_a = int(value)
            elif divId == 'score-b-value':
                Match.query.filter_by(actual=1).first().score_b = int(value)
            elif divId == 'fouls-b-value':
                Match.query.filter_by(actual=1).first().fouls_b = int(value)
            db.session.commit()
            current_app.config['SOCKETIO'].emit('update-value', {'value': value, 'divId': divId})
            # return jsonify({'value': value})
            return '', 204


@panel_blueprint.route('/get-seconds')
def get_seconds():
    seconds = Match.query.filter_by(actual=1).first().seconds
    return jsonify(seconds)


@panel_blueprint.route('/get-actual-match')
def get_actual_match_id():
    actual_match_id = Match.query.filter_by(actual=1).first().id
    return jsonify(actual_match_id)


@panel_blueprint.route('/set-panel-timer-display-mode', methods=['GET', 'POST'])
def set_panel_timer_display_mode():
    if request.method == 'POST':
        value = request.get_json()['panel_timer_display_mode']
        Match.query.filter_by(actual=1).first().panel_timer_display_mode = int(value)
        db.session.commit()
        return jsonify(Match.query.filter_by(actual=1).first().seconds)


@panel_blueprint.route('/get-match-actions/<team_id>')
def get_match_actions(team_id):
    actual_match = matchdata().get_json()['match']
    actual_match_id = actual_match['id']
    match_actions = MatchesData.query.filter_by(match_id=actual_match_id, team_id=team_id).all()
    return match_datas_schema.dump(match_actions)


@panel_blueprint.route('/set-match-actions-non-actual', methods=['POST'])
def set_match_actions_non_actual():
    if request.method == 'POST':
        actual_match_id = matchdata().get_json()['match']['id']
        match_actions = MatchesData.query.filter_by(match_id=actual_match_id).all()
        for action in match_actions:
            action.actual = 0
            db.session.commit()
        return '', 204


@panel_blueprint.route('/update-match-actions', methods=['POST'])
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


@panel_blueprint.route('/add-match-action', methods=['POST'])
def add_match_action():
    if request.method == 'POST':
        response = request.get_json()
        actual_match = Match.query.filter_by(actual=1).first()
        seconds = actual_match.seconds
        match_data = MatchesData(
            action_id=response['action_id'],
            player_id=response['player_id'],
            team_id=get_team_id_by_description(response['team'], actual_match),
            seconds=seconds,
            match_id=actual_match.id,
            actual=1,
            is_hided=0,
            replay_file='None'
        )
        db.session.add(match_data)
        db.session.commit()
        return 'match action added'


@panel_blueprint.route('/drop_replay/<action_type>')
def drop_replay(action_type):
    current_app.config['OBS_DROP_REPLAY'] = True
    _action_type = int(action_type)
    obs_ws = current_app.config['obs_ws']
    socketio = current_app.config['SOCKETIO']
    _replay_file = get_replay_file_name(_action_type)
    current_app.config['REPLAY_FILE_NAME'] = _replay_file
    action_data = {
        'seconds': current_app.config['TIME_DATA']['seconds'],
        'added_seconds': current_app.config['TIME_DATA']['added_seconds'],
        'current_period': current_app.config['MATCHDATA']['match']['current_period'],
        'match_id': current_app.config['MATCHDATA']['match']['id'],
        'action_id': int(_action_type),
        'player_id': None,
        'team_id': None,
        'actual': 1,
        'is_hided': 0,
        'replay_file': _replay_file,
        'record_time': current_app.config['RECORD_TIME']
    }
    current_app.config['ACTION_DATA'] = action_data

    if _action_type == 0:
        socketio.start_background_task(obs_ws.drop_replay, instant=True)
        _action_type = 1
    else:
        socketio.start_background_task(obs_ws.drop_replay)

    if _action_type in current_app.config['ACTIONS_SETS']['no_team_set']:
        print('no team')
        insert_action_to_db(action_data)
        return '', 204
    matchdata = current_app.config['MATCHDATA']
    goal_set = current_app.config['ACTIONS_SETS']['goal_set']
    return render_template('ws-controller-fill-action-data.html',
                           action_data=action_data, matchdata=matchdata, goal_set=goal_set)


def save_dropped_replay(action_data):
    _file_name = str({action_data['replay_file']})
    source_path = os.path.join('static', 'video', 'processed', f'replay_stream.mkv')
    destination_path1 = os.path.join('static', 'video', 'replays', _file_name)
    destination_path2 = os.path.join('static', 'video', 'replays', 'arch', _file_name)
    copy_file(source_path, destination_path1)
    copy_file(source_path, destination_path2)


def insert_action_to_db(action_data):
    all_match_data = MatchesData.query.all()
    for data in all_match_data:
        data.actual = 0
    match_data = MatchesData(
        seconds=action_data['seconds'],
        added_seconds=action_data['added_seconds'],
        current_period=action_data['current_period'],
        match_id=action_data['match_id'],
        action_id=action_data['action_id'],
        player_id=action_data['player_id'],
        team_id=action_data['team_id'],
        actual=action_data['actual'],
        is_hided=action_data['is_hided'],
        replay_file=action_data['replay_file'],
        record_time=action_data['record_time']
    )
    db.session.add(match_data)
    db.session.commit()


def get_replay_file_name(action_type):
    with current_app.app_context():
        file_type = current_app.config['REPLAY_FILE_TYPE']
        _action_name = get_type_of_action(action_type)
        _date = datetime.now().strftime("%Y%m%d-%H%M%S")
        _match = Match.query.filter_by(actual=1).first()
        _result = f'{_match.score_a}-{_match.score_b}'
        return f'{_date}_{_result}_{_action_name}{file_type}'


def get_type_of_action(param):
    _action = MatchAction.query.filter_by(id=param).first()
    return _action.desc_polish


# @panel_blueprint.route('/drop_replay')
# def drop_replay():
#     obs_ws = current_app.config['obs_ws']
#     obs_ws.drop_replay()
#     return '', 204


@panel_blueprint.route('/insert-match-action', methods=['POST'])
def insert_match_action():
    if request.method == 'POST':
        response = request.get_json()
        print('response:', response)
        _actual_match = Match.query.filter_by(actual=1).first()
        _action_id = response['action_id']
        _team_id = response['team_id']
        team_id = get_action_team_id(_actual_match, _action_id, _team_id)
        _current_date = get_current_date(response)
        _replay_file = save_replay_file(_action_id, _current_date)
        all_match_data = MatchesData.query.all()
        for data in all_match_data:
            data.actual = 0
        match_data = MatchesData(
            action_id=_action_id,
            player_id=response['player_id'],
            team_id=team_id,
            seconds=response['seconds'],
            added_seconds=response['added_seconds'],
            match_id=_actual_match.id,
            actual=1,
            is_hided=0,
            replay_file=_replay_file
        )
        db.session.add(match_data)
        db.session.commit()
        return 'match action added'


def get_current_date(response):
    if 'current_date' in response:
        return response['current_date']
    return None


def save_replay_file(action_id, current_date):
    if current_date is not None:
        obs_ws = current_app.config['obs_ws']
        replay_file = obs_ws.set_replay_file_name_prefix(action_id, current_date)
        obs_ws.save_replay(action_id, current_date)
        return replay_file
    return None


def get_action_team_id(actual_match, action_id, team_id):
    if action_id == 4:
        if team_id == actual_match.team_a:
            return actual_match.team_b
        else:
            return actual_match.team_a
    return team_id


def get_team_id_by_description(description, actual_match):
    if description == 'teama':
        return actual_match.team_a
    else:
        return actual_match.team_b


@panel_blueprint.route('/delete-match-action', methods=['POST'])
def delete_match_action():
    action_id = request.get_json()['action_id']
    action = MatchesData.query.filter_by(id=action_id).first()
    db.session.delete(action)
    db.session.commit()
    return ''


@panel_blueprint.route('/get-player/<player_id>')
def get_player(player_id):
    player = Player.query.filter_by(id=player_id).first()
    return player_schema.dump(player)


@panel_blueprint.route('/change-scoreboard-side', methods=['PUT'])
def change_scoreboard_side():
    actual_match = Match.query.filter_by(actual=1).first()
    if actual_match.is_scoreboard_reversed == 0:
        actual_match.is_scoreboard_reversed = 1
    else:
        actual_match.is_scoreboard_reversed = 0
    db.session.commit()
    return '', 204
    # return jsonify({'is_scoreboard_reversed': is_scoreboard_reversed})


@panel_blueprint.route('/get-is-scoreboard-reversed')
def get_is_scoreboard_reversed():
    actual_match = Match.query.filter_by(actual=1).first()
    return jsonify({'data': actual_match.is_scoreboard_reversed})


@timer_blueprint.route('/increment-seconds/<difference>')
def increment_seconds(difference):
    _difference = int(difference)
    with current_app.app_context():
        _matchdata = current_app.config['MATCHDATA']['match']
        _time_data = current_app.config['TIME_DATA']
        _timer = current_app.config['TIMER']
        _seconds = _time_data['seconds']
        _added_seconds = _time_data['added_seconds']
        # _periods_end_times = _matchdata['periods_end_times']
        _current_period = _matchdata['current_period']
        _time_limit = Period.query.filter_by(id=_current_period).first().end_time
        _is_added_time_allowed = _matchdata['is_added_time_allowed']
        _timer.timer_add_time(_seconds, _added_seconds, _time_limit, _is_added_time_allowed, _difference)
        return '', 204


@panel_blueprint.route('/change-score-a', methods=['POST'])
def change_score_a():
    if request.method == 'POST':
        value = request.get_json()['value']
        Match.query.filter_by(actual=1).first().score_a += int(value)
        db.session.commit()
        return jsonify(Match.query.filter_by(actual=1).first().score_a)


@panel_blueprint.route('/change-score-b', methods=['POST'])
def change_score_b():
    if request.method == 'POST':
        value = request.get_json()['value']
        Match.query.filter_by(actual=1).first().score_b += int(value)
        db.session.commit()
        return jsonify(Match.query.filter_by(actual=1).first().score_b)


@panel_blueprint.route('/change-fouls-a', methods=['POST'])
def change_fouls_a():
    if request.method == 'POST':
        value = request.get_json()['value']
        Match.query.filter_by(actual=1).first().fouls_a += int(value)
        db.session.commit()
        return jsonify(Match.query.filter_by(actual=1).first().fouls_a)


@panel_blueprint.route('/change-fouls-b', methods=['POST'])
def change_fouls_b():
    if request.method == 'POST':
        value = request.get_json()['value']
        Match.query.filter_by(actual=1).first().fouls_b += int(value)
        db.session.commit()
        return jsonify(Match.query.filter_by(actual=1).first().fouls_b)


@panel_blueprint.route('/get-all-teams/<competition_id>')
def get_all_teams(competition_id):
    teams = Team.query.filter_by(competitions=competition_id).order_by(Team.full_name).all()
    return teams_schema.dump(teams)


@panel_blueprint.route('/get-team/<team_id>')
def get_team(team_id):
    team = Team.query.filter_by(id=team_id).first()
    return team_schema.dump((team))


@panel_blueprint.route('/update-lineup', methods=['POST'])
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


@panel_blueprint.route('/update-tricots', methods=['POST'])
def update_tricots():
    if request.method == 'POST':
        _team = request.get_json()
        team = Team.query.filter_by(id=_team['id']).first()
        team.home_color_1 = _team['home_color_1']
        team.home_color_2 = _team['home_color_2']
        team.home_color_3 = _team['home_color_3']
        team.home_tricot_color_number = _team['home_tricot_color_number']
        team.away_color_1 = _team['away_color_1']
        team.away_color_2 = _team['away_color_2']
        team.away_color_3 = _team['away_color_3']
        team.away_tricot_color_number = _team['away_tricot_color_number']
        team.bibs_color = _team['bibs_color']
        team.color_for_ui = _team['color_for_ui']
        team.selected_tricot = _team['selected_tricot']
        db.session.commit()
        return jsonify(Team.query.filter_by(id=_team['id']).first())


def get_tricot(team):
    if team.selected_tricot == 1:
        tricot = [team.home_color_1, team.home_color_2, team.home_color_3][:team.home_tricot_color_number]
    elif team.selected_tricot == 2:
        tricot = [team.away_color_1, team.away_color_2, team.away_color_3][:team.away_tricot_color_number]
    else:
        tricot = [team.bibs_color]
    return tricot


@panel_blueprint.route('/update-time', methods=['POST'])
def update_time():
    if request.method == 'POST':
        seconds = request.get_json()['seconds']
        Match.query.filter_by(actual=1).first().seconds = int(seconds)
        db.session.commit()
        return jsonify(Match.query.filter_by(actual=1).first().seconds)


@panel_blueprint.route('/get_files')
def get_files():
    directory = 'static/video/replays'
    files = [file for file in os.listdir(directory) if file.endswith('.mkv')]
    return {'files': files}


# @panel_blueprint.route('/get_replays/<camera_prefix>')
# def get_replays(camera_prefix):
#     directory = 'static/video/replays'
#     files = [file for file in os.listdir(directory) if file.endswith(f'{camera_prefix}.mkv')]
#     new_content = render_template('replays-panel.html', files=files)
#     return jsonify({'content': new_content})


@panel_blueprint.route('/get_replays')
def get_replays():
    _match = Match.query.filter_by(actual=1).first()
    _replays_db = MatchesData.query.filter(MatchesData.match_id == _match.id, MatchesData.replay_file.isnot(None)).all()
    # for _replay in _replays:
    # print(len(_replays))
    # print(match_data_schema.dump(_replay))
    '''
    _data = {'id': 2925,
             'seconds': 108,
             'added_seconds': 0,
             'match_id': 98,
             'action_id': 1,
             'player_id': 125,
             'team_id': 6,
             'record_time': 0,
             'actual': 0,
             'player':
                 {'id': 125,
                  'full_name': 'Klęk Kamil',
                  'team': 6,
                  'position': '0',
                  'matches': 12,
                  'goals': 21,
                  'assists': 5,
                  'yellow_cards': 1,
                  'red_cards': 0,
                  'own_goals': 0,
                  'best_five': 3,
                  'first_name': 'Kamil',
                  'last_name': 'Klęk',
                  'default_nr': 99,
                  'squad': 1,
                  'is_active': 1,
                  'captain': '',
                  'link': 'https://nalffutsal.pl/?sp_player=kamil-klek'
                  },
             'action':
                 {'id': 1,
                  'desc_polish': 'GOL',
                  'action_icon': 'goal.png'
                  },
             'team':
                 {'id': 6,
                  'full_name': 'IGLOMEN&RodzinneRestauracje',
                  'competitions': 1,
                  'link': 'bidvest-krakow',
                  'short_name': 'IGL',
                  'home_tricot_color_number': 1,
                  'home_color_1': '#801c71',
                  'home_color_2': '#00ff00',
                  'home_color_3': '#42d2d2',
                  'color_for_ui': '',
                  'away_color_1': '#ffffff',
                  'away_color_2': '#ffffff',
                  'away_color_3': '#ffffff',
                  'selected_tricot': 1,
                  'bibs_color': '#adeb31',
                  'away_tricot_color_number': 3,
                  'logo_file': 'IGLOMENRR.png',
                  'penalty_points': 0,
                  'name_16': 'Iglomen&RR'
                  },
             'is_hided': 0,
             'replay_file': '20240619_205206___0-1_GOL_.mkv'
             }
    '''
    _replays = []
    for _replay in _replays_db:
        _repl = match_data_schema.dump(_replay)
        _replays.append(
            {'id': _repl['id'],
             'seconds': _repl['seconds'],
             'added_seconds': _repl['added_seconds'],
             'formatted_seconds': get_formatted_time(_repl['seconds'], _repl['added_seconds']),
             'replay_end_time': _repl['record_time'],
             'replay_start_time': get_replay_start_time(_repl['record_time']),
             'actual': _repl['actual'],
             'player': get_value('full_name', _repl['player']),
             'action': _repl['action']['desc_polish'],
             'team': get_value('short_name', _repl['team']),
             'record_time': _repl['record_time'],
             'replay_file': _repl['replay_file'],
             'replay_file_path': get_replay_path(_repl['replay_file']),
             'is_edited': 0
             }
        )
        print({'id': _repl['id'],
               'seconds': _repl['seconds'],
               'added_seconds': _repl['added_seconds'],
               'formatted_seconds': get_formatted_time(_repl['seconds'], _repl['added_seconds']),
               'replay_end_time': _repl['record_time'],
               'replay_start_time': get_replay_start_time(_repl['record_time']),
               'actual': _repl['actual'],
               'player': get_value('full_name', _repl['player']),
               'action': _repl['action']['desc_polish'],
               'team': get_value('short_name', _repl['team']),
               'replay_file': get_replay_path(_repl['replay_file'])
               })

    # directory = 'static/video/replays'
    # files = [file for file in os.listdir(directory) if file.endswith('.mkv')]
    new_content = render_template('replays-panel.html', replays=_replays)
    return jsonify({'content': new_content})


def get_replay_start_time(record_time):
    if record_time >= 10:
        return record_time - 10
    return 0

def get_value(_key, _dict):
    if _dict is None:
        return None
    return _dict[_key]


def get_replay_path(replay_file):
    with current_app.app_context():
        replays_dir = current_app.config['REPLAYS_FILES_DIRECTORY']
        match_replays_dir = current_app.config['MATCH_IDENTIFIER']
        return os.path.join(replays_dir, match_replays_dir, replay_file)


def get_formatted_time(_seconds, _added_seconds, _format='min:sec'):
    match _format:
        case 'min:sec':
            mins = int((_seconds - _added_seconds) / 60)
            secs = int((_seconds - _added_seconds) % 60)
            if _added_seconds > 0:
                _added_mins = int(_added_seconds / 60)
                _added_secs = int(_added_seconds % 60)
                return f'{mins}+ {_added_mins}:{'{:02}'.format(_added_secs)}'
            return f'{mins}:{'{:02}'.format(secs)}'




@panel_blueprint.route('/process_file/<filename>')
def process_file(filename):
    replay_name = 'replay_stream.mkv'
    source_path = os.path.join('static/video/replays', filename)
    target_path = os.path.join('static/video/processed', replay_name)

    with open(source_path, 'rb') as source_file, open(target_path, 'wb') as target_file:
        target_file.write(source_file.read())

    return send_file(target_path, as_attachment=True)


@panel_blueprint.route('/actual-match-data/<team>', methods=['GET', 'POST'])
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
            'seconds': sec_to_secmin(_data.seconds),
            'action_type': set_action_type(_data.action_id),
            'player_id': _player.id,
            'player_first_name': _player.first_name,
            'player_last_name': _player.last_name,
            'is_hided': _data.is_hided
        })
    match_data.append(event_data)

    return jsonify(match_data)


def sec_to_secmin(sec):
    _div = divmod(int(sec), 60)
    secmin = {'minutes': '{:02}'.format(_div[0]), 'seconds': '{:02}'.format(_div[1])}
    return secmin


def set_action_type(action_id):
    _actions = {1: 'G', 2: 'Ż', 3: 'C', 4: 'S', 5: 'T', 6: 'V', 7: 'F', 8: 'O', 9: 'P', 10: 'B', 11: 'H'}
    return _actions[action_id]


@panel_blueprint.route('/prepare-data-to-edit/<int:dataId>')
def prepare_data_to_edit(dataId):
    _match_data = MatchesData.query.filter_by(id=dataId).first()
    data = {}
    _data = {
        'data_id': _match_data.id,
        'seconds': sec_to_secmin(_match_data.seconds),
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


@panel_blueprint.route('/update-data/<int:data_id>', methods=['PUT'])
def update_data(data_id):
    try:
        # Pobierz dane z żądania
        data = request.get_json()

        # Pobierz obiekt z bazy danych
        obj_to_update = MatchesData.query.get(data_id)

        # Zaktualizuj pola obiektu
        obj_to_update.seconds = data['seconds']
        obj_to_update.action_id = data['action']
        obj_to_update.player_id = data['player']

        # Przekonwertuj czas z minut i sekund na sekundy
        time_in_seconds = data['seconds']
        obj_to_update.seconds = time_in_seconds
        obj_to_update.is_hided = data['is_hided']

        # Zapisz zmiany w bazie danych
        db.session.commit()

        return jsonify({'message': 'Dane zaktualizowane pomyślnie'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@panel_blueprint.route('/delete-data/<int:data_id>', methods=['DELETE'])
def delete_data(data_id):
    try:
        data_to_delete = MatchesData.query.get(data_id)

        if data_to_delete:
            db.session.delete(data_to_delete)
            db.session.commit()

            return '', 204
        else:
            return jsonify({'error': 'Rekord o podanym ID nie istnieje'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@panel_blueprint.route('/select-replay', methods=['POST'])
def select_replay():
    if request.method == 'POST':
        replay_id = int(request.get_json()['replayId'])
        _match_id = Match.query.filter_by(actual=1).first().id
        _match_data = MatchesData.query.filter_by(match_id=_match_id).all()
        for _data in _match_data:
            _data.actual = 0
        MatchesData.query.filter_by(id=replay_id).first().actual = 1
        db.session.commit()
        return jsonify({'status': 'OK'})


@panel_blueprint.route('/get-recorded-video-length/<camera_prefix>')
def get_recorded_video_length(camera_prefix):
    return jsonify({'video_length': current_app.config['VIDEO_LENGTH'][camera_prefix]})


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


@settings_blueprint.route('/add-league-match', methods=['GET', 'POST'])
def league_matches():
    if request.method == 'POST':
        team1 = request.form.get('team1')
        team2 = request.form.get('team2')
        # score1 = request.form.get('score1')
        # score2 = request.form.get('score2')
        competitions = request.form.get('competitions')
        division = request.form.get('division')
        date = datetime.strptime(request.form.get('date'), '%Y-%m-%d')

        match = LeagueMatches(team1=team1,
                              team2=team2,
                              score1=None,
                              score2=None,
                              competitions=competitions,
                              division=division,
                              date=date,
                              event_id=None)
        db.session.add(match)
        db.session.commit()

    competitions = Competitions.query.all()
    divisions = Division.query.all()
    teams = Team.query.all()

    return render_template('add-league-match.html', competitions=competitions, divisions=divisions, teams=teams)


@settings_blueprint.route('/add-nalf-league-matches/<page_id>')
def add_nalf_league_matches(page_id):
    scraper = NALFleagueMatchesScraper(page_id)
    data_objects = scraper.scrape_matches()
    matches = data_objects['matches']
    print('matches', matches)
    division = data_objects['division'].split()[1].lower()
    for match in matches:
        _match = LeagueMatches.query.filter_by(event_id=match['event_id']).first()
        if not _match:
            print('not match')
            _match = LeagueMatches(team1=get_team(match['team1']),
                                   team2=get_team(match['team2']),
                                   score1=match['score1'],
                                   score2=match['score2'],
                                   competitions=1,
                                   division=get_division(match['division']),
                                   date=match['date'],
                                   event_id=str(match['event_id']))
            db.session.add(_match)
        else:
            if _match.score1 is None or _match.score2 is None:
                _match.score1 = match['score1']
                _match.score2 = match['score2']
            elif not _match.score1 < 0 or not _match.score2 < 0:
                _match.score1 = match['score1']
                _match.score2 = match['score2']
            _match.competitions = 1
            _match.division = get_division(match['division'])
            _match.date = match['date']
        db.session.commit()
    return jsonify({'message': f'Pobrano wyniki Dywizji {division.upper()}'})


def get_team(team_name):
    team = Team.query.filter_by(full_name=team_name).first()
    return team


def get_division(division_name):
    return Division.query.filter_by(name=division_name).first()


def get_competitions(competitions_id):
    return Competitions.query.filter_by(id=competitions_id).first()


def get_division_id(division_name):
    division_id = Division.query.filter_by(name=division_name).first().id
    return division_id


@settings_blueprint.route('/create-team', methods=['GET', 'POST'])
def create_team():
    form = CreateTeamForm(request.form)
    form.process()

    if request.method == 'POST':
        new_team = Team(
            full_name=request.form.get('full_name'),
            short_name=request.form.get('short_name'),
            link=request.form.get('link'),
            competitions=request.form.get('competitions'),
            home_tricot_color_number=3,
            home_color_1=request.form.get('home_color_1'),
            home_color_2=request.form.get('home_color_2'),
            home_color_3=request.form.get('home_color_3'),
            away_tricot_color_number=3,
            away_color_1=request.form.get('home_color_1'),
            away_color_2=request.form.get('home_color_2'),
            away_color_3=request.form.get('home_color_3'),
            color_for_ui='#D3D3D3',
            selected_tricot=1,
            logo_file=request.form.get('logo_file'),
            penalty_points=0
        )

        db.session.add(new_team)
        db.session.flush()
        db.session.commit()

        return redirect(url_for('settings.nalf'))

    return render_template('create-team.html', form=form)


@settings_blueprint.route('/creatematch', methods=['GET', 'POST'])
def creatematch():
    form = MatchForm(request.form)
    form.competitions.default = 1
    form.process()

    form_content = CreateEditMatch.form_content

    if request.method == 'POST':
        team_a = request.form.get('team_a')
        team_b = request.form.get('team_b')
        periods = 2
        period_length = request.form.get('period_length')
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
                          # , period_length=period_length
                          , stadium=stadium
                          , date=date_time
                          , competitions=competitions
                          , division=division)
        if is_actual:
            db.session.query(Match).update({Match.actual: 0})
            new_match.actual = 1
        db.session.add(new_match)
        db.session.flush()

        for _period in range(periods):
            new_period = Period(
                name=get_period_name(_period, periods)
                , match_id=new_match.id
                , length=period_length
                , start_time=get_start_time(_period, period_length)
                , end_time=get_end_time(_period, period_length)
            )

            new_match.period.append(new_period)
            if _period == 0:
                new_match.current_period = new_period.id

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
        create_replays_folders(new_match)
        _set_actual_match(new_match)
        return redirect(url_for('settings.nalf'))

    return render_template('creatematch.html', form=form, form_content=form_content)


def create_replays_folders(_match):
    with current_app.app_context():
        match_identifier = get_match_identifier(current_app, _match)
        replays_folder = current_app.config['REPLAYS_FILES_DIRECTORY']
        match_replays_folder = os.path.join(replays_folder, match_identifier)
        create_folder(match_replays_folder)
        match_replays_arch_folder = os.path.join(replays_folder, 'arch', match_identifier)
        create_folder(match_replays_arch_folder)


def _set_actual_match(_match):
    with current_app.app_context():
        if _match.actual:
            current_app.config['MATCH_IDENTIFIER'] = get_match_identifier(current_app, _match)


def get_period_name(period, periods):
    if periods in [2, 3, 4]:
        return f'{period + 1}. {get_period_type_name(periods)}'
    elif periods == 1:
        return 'mecz'
    else:
        return f'część {period + 1} z {periods}'


def get_start_time(period_nr, period_length):
    return int(period_nr) * int(period_length)


def get_end_time(period_nr, period_length):
    return (int(period_nr) + 1) * int(period_length) - 1


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

    form_content = CreateEditMatch.form_content

    if request.method == 'POST':
        match.team_a = form.team_a.data
        match.team_b = form.team_b.data
        match.period_length = form.period_length.data
        match.actual = form.is_actual.data
        cameramen = form.cameramen.data
        commentators = form.commentators.data
        referees = form.referees.data
        match.stadium = form.stadium.data
        match.date_time = form.date_time.data

        # Utwórz nowy mecz
        # match = Match(team_a=team_a, team_b=team_b, period_length=period_length, stadium=stadium, date=date_time)
        if match.actual:
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
        create_replays_folders(match)
        _set_actual_match(match)
        return redirect(url_for('settings.nalf'))

    return render_template('edit_match.html', form=form, match=match, selected_commentators=selected_commentators,
                           selected_cameramen=selected_cameramen, selected_referees=selected_referees,
                           form_content=form_content, date_time=date_time)


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
        return True


@settings_blueprint.route('/competition-teams')
def competition_teams():
    _competition_teams = Team.query.filter_by(competitions=1).order_by('full_name')
    return render_template('competition-teams.html', teams=_competition_teams)


@settings_blueprint.route('/edit-team/<edit_type>/<int:team_id>', methods=['GET', 'POST'])
def edit_team(edit_type, team_id):
    if request.method == 'POST':
        _data = request.form.to_dict()
        if 'submit_players' in _data:
            save_players_to_database(_data)
        elif 'submit_colors' in _data:
            save_tricots_colors_to_database(team_id, _data)
        if edit_type == 'edit':
            return redirect(url_for('settings.edit_team', edit_type=edit_type, team_id=team_id))
        elif edit_type == 'set':
            return redirect(url_for('settings.edit_team', edit_type='set', team_id=team_id))
    team = Team.query.filter_by(id=team_id).first()
    players = Player.query.filter_by(team=team_id).order_by(Player.position.desc(),
                                                            Player.default_nr)  # Pobierz graczy z bazy danych
    # .order_by(desc(players.position))
    if edit_type == 'edit':
        return render_template('edit_team.html', edit_type=edit_type, team_id=team_id, team=team, players=players)
    elif edit_type == 'set':
        return render_template('set-lineup.html', edit_type=edit_type, team_id=team_id, team=team, players=players)


# @settings_blueprint.route('/set-lineup/<int:team_id>', methods=['GET', 'POST'])
# def set_lineup(team_id):
#     if request.method == 'POST':
#         _data = request.form.to_dict()
#         if 'submit_players' in _data:
#             print('submit_players', _data, flush=True)
#             save_players_to_database(_data)
#         elif 'submit_colors' in _data:
#             print('submit_colors', _data, flush=True)
#             save_tricots_colors_to_database(team_id, _data)

#         return redirect(url_for('settings.set_lineup', team_id=team_id))
#     team = Team.query.filter_by(id=team_id).first()
#     players = Player.query.filter_by(team=team_id)  # Pobierz graczy z bazy danych
#     return render_template('set-lineup.html', team_id=team_id, team=team, players=players)

def save_players_to_database(player_data):
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
            if '[captain_hidden]' in key:
                key = key.replace('_hidden', '')
            if f'player_{plyr_id}' in key:
                _key = key.split('[')[1][:-1]
                _plyr_data.update({_key: value})

        players_data.update({plyr_id: _plyr_data})

    # # Zapisz dane do bazy danych
    for key in players_data:
        player = Player.query.filter_by(id=key).first()
        if player:
            # print(players_data[key], flush=True)
            # Aktualizuj dane istniejącego gracza
            player.squad = players_data[key].get('squad', '0')
            player.default_nr = players_data[key].get('default_nr', 0)
            player.first_name = players_data[key].get('first_name', 'Imię')
            player.last_name = players_data[key].get('last_name', 'Nazwisko')
            player.position = players_data[key].get('position', 0)
            player.captain = players_data[key].get('captain', 0)

        db.session.commit()


def save_tricots_colors_to_database(team_id, tricots_data):
    # players_ids = []
    # players_data = {}

    # for key, value in player_data.items():
    #     # Sprawdź, czy pole zawiera dane gracza
    #     if '[' in key and ']' in key:
    #         player_id = key.split('[')[0].split('_')[1]
    #         players_ids.append(player_id)
    # players_ids = set(players_ids)
    #
    # for plyr_id in players_ids:
    #     _plyr_data = {}
    #
    #     for key, value in player_data.items():
    #         if f'player_{plyr_id}' in key:
    #             key = key.split('[')[1][:-1]
    #             _plyr_data.update({key: value})
    #     players_data.update({plyr_id: _plyr_data})

    # # Zapisz dane do bazy danych
    team = Team.query.filter_by(id=team_id).first()

    if team:
        team.selected_tricot = tricots_data.get('selected_tricot', 1)
        team.home_tricot_color_number = tricots_data.get('home_tricot_color_number', 1)
        team.away_tricot_color_number = tricots_data.get('away_tricot_color_number', 1)
        team.home_color_1 = tricots_data.get('home_color_1', team.home_color_1)
        team.home_color_2 = tricots_data.get('home_color_2', team.home_color_2)
        team.home_color_3 = tricots_data.get('home_color_3', team.home_color_3)
        team.away_color_1 = tricots_data.get('away_color_1', team.away_color_1)
        team.away_color_2 = tricots_data.get('away_color_2', team.away_color_2)
        team.away_color_3 = tricots_data.get('away_color_3', team.away_color_3)
        team.bibs_color = tricots_data.get('bibs_color', team.bibs_color)

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


@settings_blueprint.route('/show-matches-by-date/<target>/<division>', methods=['GET'])
def show_matches_by_date(target, division):
    # Pobieramy parametr 'days' z zapytania lub używamy domyślnej wartości +1/-1 dni
    days = int(request.args.get('days', 7))

    # Obliczamy daty
    today = datetime.now()
    start_date = today - timedelta(days=days)
    end_date = today + timedelta(days=days)
    print('division:', division)
    division_id = get_division_id_by_letter(division)
    print('division_id:', division_id)
    # Pobieramy dane z pliku matches.json
    matches = LeagueMatches.query.filter_by(division_id=division_id).all()

    data = league_matches_schema.dump(matches)

    # Filtrujemy dane, aby pokazać tylko te w określonym przedziale dat
    filtered_data = []
    for dta in data:
        print(start_date)
        print(datetime.strptime(dta['date'], '%Y-%m-%d %H:%M:%S'))
        print(end_date)
        print('-----------------')
        if start_date <= datetime.strptime(dta['date'], '%Y-%m-%d %H:%M:%S') <= end_date:
            filtered_data.append({"id": dta['event_id'],
                                  "date": dta['date'],
                                  "teams": [
                                      dta['team1']['full_name'],
                                      dta['team2']['full_name']
                                  ],
                                  "result": [
                                      dta['score1'],
                                      dta['score2']
                                  ],
                                  "actual": dta['is_actual'],
                                  "parallel": False,
                                  "penalty_points": [
                                      0,
                                      0
                                  ]
                                  })
    if target == 'controller':
        for dta in filtered_data:
            dta.update({'date': dta['date']})
            dta.update({'teams': [{'short_name': _get_short_team_name(dta['teams'][0]),
                                   'full_name': dta['teams'][0]},
                                  {'short_name': _get_short_team_name(dta['teams'][1]),
                                   'full_name': dta['teams'][1]}]
                        })
        new_content = render_template('update_results_panel.html', data=filtered_data, division=division)
        return jsonify({'content': new_content})
    return render_template('update_results.html', data=filtered_data, division=division)


@settings_blueprint.route('/edit-match-action/<action_id>')
def edit_match_action(action_id):
    _match_data = MatchesData.query.filter_by(id=action_id).first()
    event = {}
    _event = {
        'data_id': _match_data.id,
        'seconds': sec_to_secmin(_match_data.seconds),
        'action_id': _match_data.action_id,
        'player_id': _match_data.player_id,
        'team_id': _match_data.team_id,
        'match_id': _match_data.match_id,
        'is_hided': _match_data.is_hided
    }
    event.update({'event': _event})
    _match = Match.query.filter_by(id=event['event']['match_id']).first()
    _teams_ids = {'normal': _match_data.team_id}
    if int(_match_data.team_id) == int(_match.team_a):
        _teams_ids.update({'og': _match.team_b})
    else:
        _teams_ids.update({'og': _match.team_a})
    event.update({'teams_ids': _teams_ids})
    _actions_types = MatchAction.query.all()
    _actions = {}
    for _action in _actions_types:
        _actions.update({_action.id: _action.desc_polish})
    event.update({'actions': _actions})
    _players = {'normal': players_schema.dump(Player.query.filter_by(team=_teams_ids['normal']).all()),
                'og': players_schema.dump(Player.query.filter_by(team=_teams_ids['og']).all())
                }
    event.update({'players': _players})
    new_content = render_template('panel-sidebar-edit-action.html', data=event)
    return jsonify({'content': new_content})


@settings_blueprint.route('/show-all-matches/<target>/<division>', methods=['GET'])
def show_all_matches(target, division):
    with open(f'static/json/matches-{division}.json', 'r') as json_matches_file:
        data = json.load(json_matches_file)

    # Filtrujemy dane, aby pokazać tylko te w określonym przedziale dat
    if target == 'controller':
        new_content = render_template('update_results_panel.html', data=data, division=division)
        return jsonify({'content': new_content})
    return render_template('update_results.html', data=data, division=division)


@settings_blueprint.route('/scrape-matches/<page_id>', methods=['GET'])
def scrape_matches(page_id):
    scraper = NALFmatchesScraper(page_id)
    data_objects = scraper.scrape_matches()
    matches = data_objects['matches']
    division = data_objects['division'].split()[1].lower()
    with open(f'static/json/penalty-{division}-points.json', 'r') as json_penalty_file:
        penalties_points = json.load(json_penalty_file)
    for _match in matches:
        for _penalty in penalties_points:
            if _match['id'] == _penalty['id']:
                _match['penalty_points'] = _penalty['penalty_points']

    file_generator = JSONFileGenerator(matches)
    file_generator.generate_and_save_file(f'matches-{division}.json')
    return jsonify({'message': f'Pobrano wyniki Dywizji {division.upper()}'})


def generate_table(division, virtual_result=None):
    with current_app.app_context():
        # if request.method == 'POST':
        division_id = division
        if not division.isdigit():
            division_id = get_division_id_by_letter(division)
        results = []
        league_mathes = LeagueMatches.query.filter_by(division_id=division_id).all()
        for match in league_mathes:
            team1 = Team.query.filter_by(id=match.team1_id).first()
            team2 = Team.query.filter_by(id=match.team2_id).first()
            results.append((team1.full_name,
                            team1.id,
                            team2.full_name,
                            team2.id,
                            match.score1,
                            match.score2,))
        _table_generator = TableGenerator()
        try:
            regular_round_matches = current_app.config['DIVISION_CONFIG'][int(division_id)]['regular_round_matches']
        except:
            regular_round_matches = None
        _table = _table_generator.generate_table(results, regular_round_matches)

        return _table


def reduce_table(table, is_actual=False):
    tiny_table = []
    for row in table:
        print(row)
        # print(row[0][list(row[0].keys())[0]]['points'])
        tiny_table.append([is_actual,
                           Team.query.filter_by(full_name=row['name']).first().name_16,
                           row['points'],
                           "",
                           row['group']])
    return tiny_table


@settings_blueprint.route('/save-result/<target>/<division>', methods=['POST'])
def save_result(target, division):
    # Pobierz dane JSON przesłane z przeglądarki
    match_data = request.json
    # print(match_data)

    match = LeagueMatches.query.filter_by(event_id=match_data['id']).first()
    match.is_actual = int(match_data['actual'])
    match.score1 = prepare_result(match_data['result_home'])
    match.score2 = prepare_result(match_data['result_away'])
    if match.score1 is not None and int(match.score1) < 0:
        match.team1_penalty_points = 1
    if match.score2 is not None and int(match.score2) < 0:
        match.team2_penalty_points = 1
    db.session.commit()

    virtual_table = generate_table(division)
    tiny_virtual_table = reduce_table(virtual_table, match_data)

    with open(f'static/json/virtual-table-{division}.json', 'w') as json_file:
        json.dump(tiny_virtual_table, json_file, indent=2)

    if target == 'controller':
        return jsonify({'function': division})
    return redirect(url_for('settings.show_matches_by_date', division=division))


def prepare_result(value):
    if value == '':
        return None
    return value


@settings_blueprint.route('/generate_base_table/<division>', methods=['GET', 'POST'])
def generate_base_table(division):
    with current_app.app_context():
        # if request.method == 'POST':
        base_table = generate_table(division)
        tiny_base_table = reduce_table(base_table)
        with open(f'static/json/base-table-{division}.json', 'w') as json_file:
            json.dump(tiny_base_table, json_file, indent=2)
        # return jsonify({'status': 'success', 'message': f'Plik base-table-.json został wygenerowany.'})
        return jsonify({'status': 'success', 'message': f'Plik base-table-{division}.json został wygenerowany.'})


def style_table(_table, _actual_played_teams, division):
    divide_index = None
    for i in _table:
        if i == 'divide':
            divide_index = _table.index(i)
    if divide_index is not None:
        _promotion_group = _table[:divide_index]
        _demotion_group = _table[divide_index + 1:]
        promotion_group = [[x['actual'], x['team_name'], x['points'], '', 'promotion-group'] for x in _promotion_group]
        demotion_group = [[x['actual'], x['team_name'], x['points'], '', 'demotion-group'] for x in _demotion_group]
        _tbl = promotion_group + demotion_group
    else:
        _tbl = [[x['actual'], x['team_name'], x['points'], '', 'non-divided-group'] for x in _table]
    for item in _tbl:
        if item[1] in _actual_played_teams:
            item[0] = True
    return _tbl


@settings_blueprint.route('/generate_virtual_table/<division>', methods=['GET'])
def generate_virtual_table(division):
    table_generator = TableGenerator(division=division)
    table = table_generator.generate_table()
    _tbl = [[x['team_name'], x['points']] for x in table]
    with open(f'static/json/virtual-table-{division}.json', 'w') as json_file:
        json.dump(_tbl, json_file, indent=2)

    return jsonify({'status': 'success', 'message': f'Plik virtual-table-{division}.json został wygenerowany.'})


@settings_blueprint.route('/update_players/<edit_type>/<team_id>', methods=['GET'])
def update_players(edit_type, team_id):
    # if request.method == 'POST':
    team = Team.query.filter_by(id=team_id).first()
    scraper = NALFteamScraper(team.link)
    nalffutsal_players = scraper.scrape_team_players()
    players_updater = NALFplayersUpdater()
    players_updater.update_players(nalffutsal_players, team_id)
    return redirect(url_for('settings.edit_team', team_id=team_id, edit_type=edit_type))


@settings_blueprint.route('/get-statistics/<team>')
def get_statistics(team):
    _actual_match = Match.query.filter_by(actual=1).first()
    _team_id = get_team_id_by_description(team, _actual_match)
    _team = Team.query.filter_by(id=_team_id).first()
    _team_scraper = NALFteamScraper(_team.link)
    _scraped_team = _team_scraper.scrape_team_players()
    _scraped_table = _team_scraper.scrape_team_table()
    _division = _scraped_table[0]['division']
    content = {
        'table-data': _scraped_table,
        'average-points': _get_average_per_match('points', _scraped_table),
        'average-scored-goals': _get_average_per_match('goals_scored', _scraped_table),
        'average-lost-goals': _get_average_per_match('goals_lost', _scraped_table),
        'best-strikers': _get_best_players('goals', _scraped_team),
        'best-assistants': _get_best_players('assists', _scraped_team),
        'best-canadians': _get_best_canadians(_scraped_team),
        'most-yellow-cards': _get_best_players('yellow_cards', _scraped_team),
        'most-red-cards': _get_best_players('red_cards', _scraped_team),
        'most-best-five': _get_best_players('best_five', _scraped_team),
        'most-best-player': _get_best_players('best_player', _scraped_team),
        'highest-win': _get_higest_results(_team.full_name, _division, 'wins'),
        'highest-tie': _get_higest_results(_team.full_name, _division, 'ties'),
        'highest-lost': _get_higest_results(_team.full_name, _division, 'loses')
    }
    with open(f'static/json/match-stats-{team}.json', 'w') as json_file:
        json.dump(content, json_file, indent=2)
    _message = f'match-stats-{team}.json został wygenerowany.'
    new_content = render_template('after_load_content_message.html', message=_message)
    return jsonify({'content': new_content})


def _get_average_per_match(_type, _data):
    _goals = _data[0][_type]
    _matches = _data[0]['matches']
    return round(_goals / _matches, 2)


def _get_best_players(_type, _data):
    sorted_players = sorted(_data, key=lambda x: x[_type], reverse=True)
    _max = sorted_players[0][_type]
    return [player for player in sorted_players if player[_type] == _max]


def _get_best_canadians(_data):
    for player in _data:
        player['canadian_points'] = player['goals'] + player['assists']
    sorted_players = sorted(_data, key=lambda x: x['canadian_points'], reverse=True)
    _max = sorted_players[0]['canadian_points']
    _best_canadians = [player for player in sorted_players if player["canadian_points"] == _max]
    for player in _data:
        del player["canadian_points"]
    return _best_canadians


def _get_higest_results(team_name, division, _type):
    with open(f'static/json/matches-{division[-1].lower()}.json') as json_file:
        matches = json.load(json_file)
    _matches = []
    results = {
        'wins': [],
        'ties': [],
        'loses': []
    }
    for match in matches:
        if len(match['result']) == 2:
            if team_name in match['teams']:
                if team_name == match['teams'][1]:
                    match['teams'][0], match['teams'][1] = match['teams'][1], match['teams'][0]
                    match['result'][0], match['result'][1] = match['result'][1], match['result'][0]
                    match['penalty_points'][0], \
                        match['penalty_points'][1] = match['penalty_points'][1], match['penalty_points'][0]
                    _matches.append(match)
                else:
                    _matches.append(match)
    for match in _matches:
        if match['result'][0] == match['result'][1]:
            results['ties'].append(match)
        elif match['result'][0] > match['result'][1]:
            results['wins'].append(match)
        else:
            results['loses'].append(match)

    return _calculate_highest_result(results, _type)


def _calculate_highest_result(_matches, _type):
    for _match in _matches[_type]:
        _match['difference_goals'] = abs(int(_match['result'][0]) - int(_match['result'][1]))
        _match['sum_goals'] = int(_match['result'][0]) + int(_match['result'][1])
    sorted_matches = sorted(_matches[_type], key=lambda x: (x['difference_goals'], x['sum_goals']), reverse=True)
    if not sorted_matches:
        return [{'result': None}]
    _max_difference = sorted_matches[0]['difference_goals']
    _max_goals = sorted_matches[0]['sum_goals']
    _highest_result = [_match for _match in sorted_matches if _match["difference_goals"] == _max_difference and
                       _match["sum_goals"] == _max_goals]
    for _match in _matches[_type]:
        del _match["difference_goals"]
    return _highest_result


@settings_blueprint.route('/statistics-staff/<team>')
def statistics_staff(team):
    with open(f'static/json/match-stats-{team}.json', 'r') as json_file:
        _data = json.load(json_file)
    return render_template('statistics-staff.html', data=_data, team=team)


@settings_blueprint.route('/playoffs-edit', methods=['GET', 'POST'])
def playoffs_edit():
    if request.method == 'POST':
        _data = {
            'matches': {
                'match1': {
                    'teams': [request.form['teams10'], request.form['teams11']],
                    'results': [request.form['results10'], request.form['results11']],
                    'penalties': [request.form['penalties10'], request.form['penalties11']]
                },
                'match2': {
                    'teams': [request.form['teams20'], request.form['teams21']],
                    'results': [request.form['results20'], request.form['results21']],
                    'penalties': [request.form['penalties20'], request.form['penalties21']]
                },
                'match3': {
                    'teams': [request.form['teams30'], request.form['teams31']],
                    'results': [request.form['results30'], request.form['results31']],
                    'penalties': [request.form['penalties30'], request.form['penalties31']]
                },
                'match4': {
                    'teams': [request.form['teams40'], request.form['teams41']],
                    'results': [request.form['results40'], request.form['results41']],
                    'penalties': [request.form['penalties40'], request.form['penalties41']]
                },
                # 'match5': {
                #   'teams': [request.form['teams50'], request.form['teams51']],
                #   'results': [request.form['results50'], request.form['results51']],
                #   'penalties': [request.form['penalties50'], request.form['penalties51']]
                # },
                # 'match6': {
                #   'teams': [request.form['teams60'], request.form['teams61']],
                #   'results': [request.form['results60'], request.form['results61']],
                #   'penalties': [request.form['penalties60'], request.form['penalties61']]
                # },
                # 'match7': {
                #   'teams': [request.form['teams70'], request.form['teams71']],
                #   'results': [request.form['results70'], request.form['results71']],
                #   'penalties': [request.form['penalties70'], request.form['penalties71']]
                # },
                # 'match8': {
                #   'teams': [request.form['teams80'], request.form['teams81']],
                #   'results': [request.form['results80'], request.form['results81']],
                #   'penalties': [request.form['penalties80'], request.form['penalties81']]
                # }
            }
        }
        with open(f'static/json/playoffs.json', 'w') as json_file:
            json.dump(_data, json_file, indent=2)
        return '', 204

    teams = Team.query.filter_by(competitions=1).order_by('full_name').all()
    table_a = generate_table('5')[:2]
    table_b = generate_table('6')[:2]

    if len(table_a) < 2:
        table_a = [{'name': ''}, {'name': ''}]
    if len(table_b) < 2:
        table_b = [{'name': ''}, {'name': ''}]

    _data = {
        'a1': table_a[0]['name'],
        'a2': table_a[1]['name'],
        'b1': table_b[0]['name'],
        'b2': table_b[1]['name'],
        'teams': teams
    }
    print(_data)
    with open(f'static/json/playoffs.json', 'r') as json_file:
        _data.update({'matches': json.load(json_file)['matches']})
    return render_template('playoffs-edit.html', data=_data)


@settings_blueprint.route('/edit-match-periods')
def edit_match_periods():
    pass


@obswebsocketpy_blueprint.route('/ws-controller')
def ws_controller():
    return render_template('ws-controller-main.html')


@obswebsocketpy_blueprint.route('/render-content/<content_name>')
def render_content(content_name):
    _matchdata = matchdata().get_json()
    banner_folder = current_app.config['BANNER_FOLDER']
    folders = [folder for folder in os.listdir(banner_folder) if os.path.isdir(os.path.join(banner_folder, folder))]
    return render_template(f'ws-controller-{content_name}.html',
                           matchdata=_matchdata,
                           folders=folders)


@obswebsocketpy_blueprint.route('/render-round-tab')
def render_round_tab():
    _actual_match = Match.query.filter_by(actual=1).first()
    _division = Division.query.filter_by(id=_actual_match.division).first()
    response = requests.get(request.url_root + f'render-round-data/{_division.id}')
    _competitions = Competitions.query.filter_by(id=_division.competition_id).first()
    _divisions = Division.query.filter_by(competition_id=_actual_match.competitions).all()
    _data = {
        'division': _division,
        'divisions': _divisions,
    }
    new_content = render_template(f'ws-controller-round-data.html', data=_data)
    return jsonify({'content': new_content})


@obswebsocketpy_blueprint.route('/showscene/<scenename>')
def show_scene(scenename):
    obs_ws = current_app.config['obs_ws']
    obs_ws.show_scene(scenename)
    return '', 204


@obswebsocketpy_blueprint.route('/goal-sequence')
def play_goal_sequence():
    obs_ws = current_app.config['obs_ws']
    obs_ws.play_instant_replay()
    return '', 204


@obswebsocketpy_blueprint.route('/save-replay/<typeofaction>')
def save_replay(typeofaction):
    obs_ws = current_app.config['obs_ws']
    obs_ws.save_replay(typeofaction)
    return '', 204


@obswebsocketpy_blueprint.route('/play-replay-sequence')
def play_replay_sequence():
    obs_ws = current_app.config['obs_ws']
    obs_ws.play_replay()
    return '', 204


@obswebsocketpy_blueprint.route('/start-stop-stream')
def start_stop_stream():
    obs_ws = current_app.config['obs_ws']
    obs_ws.start_stop_stream()
    return '', 204


@obswebsocketpy_blueprint.route('/start-stream')
def start_stream():
    obs_ws = current_app.config['obs_ws']
    obs_ws.start_stream_cascade()
    _status = obs_ws.get_stream_status()
    return _status


@obswebsocketpy_blueprint.route('/get-stream-status')
def get_stream_status():
    obs_ws = current_app.config['obs_ws']
    _status = obs_ws.get_stream_status()
    return _status


@obswebsocketpy_blueprint.route('/stop-stream')
def stop_stream():
    obs_ws = current_app.config['obs_ws']
    obs_ws.stop_stream_cascade()
    return '', 204


@obswebsocketpy_blueprint.route('/show-half-time-scene')
def show_half_time_scene():
    obs_ws = current_app.config['obs_ws']
    obs_ws.show_half_time_scene()
    return '', 204


@obswebsocketpy_blueprint.route('/show-match-scene')
def show_match_scene():
    obs_ws = current_app.config['obs_ws']
    obs_ws.show_match_scene()
    return '', 204


@obswebsocketpy_blueprint.route('/show-start-scene')
def show_start_scene():
    obs_ws = current_app.config['obs_ws']
    obs_ws.start_scene_cascade()
    return '', 204


@obswebsocketpy_blueprint.route('/show_banner')
def show_banner():
    obs_ws = current_app.config['obs_ws']
    obs_ws.show_banner()
    return '', 204


@obswebsocketpy_blueprint.route('/select_banner')
def select_banner():
    banner_folder = current_app.config['BANNER_FOLDER']
    folders = [folder for folder in os.listdir(banner_folder) if os.path.isdir(os.path.join(banner_folder, folder))]
    for folder in folders:
        print(folder, flush=True)
    return render_template('ws-controller-banner.html', folders=folders)


@obswebsocketpy_blueprint.route('/replace_files/<folder_name>')
def replace_files(folder_name):
    banner_folder = current_app.config['BANNER_FOLDER']
    selected_folder_path = os.path.join(banner_folder, folder_name)

    # Usuń wszystkie pliki (bez folderów) z /templates/banner/
    for file_name in os.listdir(banner_folder):
        file_path = os.path.join(banner_folder, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)

    # Skopiuj pliki ze wskazanego folderu do /templates/banner/
    for file_name in os.listdir(selected_folder_path):
        file_path = os.path.join(selected_folder_path, file_name)
        if os.path.isfile(file_path):
            shutil.copy(file_path, banner_folder)
    _matchdata = matchdata().get_json()
    new_content = render_template(f'ws-controller-match.html', matchdata=_matchdata)
    return jsonify({'content': new_content})


@obswebsocketpy_blueprint.route('/showaction')
def show_action():
    obs_ws = current_app.config['obs_ws']
    obs_ws.show_action()
    return '', 204


@obswebsocketpy_blueprint.route('/showvirtualtable/<division>')
def show_virtual_table(division):
    obs_ws = current_app.config['obs_ws']
    obs_ws.show_virtual_table(division)
    return '', 204


@obswebsocketpy_blueprint.route('/toggle_filter_enable/<source_name>/<filter_name>')
def toggle_filter_enable(source_name, filter_name):
    obs_ws = current_app.config['obs_ws']
    obs_ws.toggle_filter_enable(source_name, filter_name)
    return '', 204


@obswebsocketpy_blueprint.route('/get_filter_status/<source_name>/<filter_name>')
def get_filter_status(source_name, filter_name):
    obs_ws = current_app.config['obs_ws']
    return jsonify({'status': obs_ws.get_filter_status(source_name, filter_name)})


@obswebsocketpy_blueprint.route('/set_source_index/<scene_name>/<source_name>/<source_index>')
def set_source_index(scene_name, source_name, source_index):
    scene_name = scene_name.replace('%2', ' ')
    source_name = source_name.replace('%2', ' ')
    source_index = int(source_index)
    obs_ws = current_app.config['obs_ws']
    if source_index == -1:
        source_index = len(obs_ws.get_scene_item_list(scene_name)) - 1
    source_id = obs_ws.get_scene_item_id(scene_name, source_name)
    obs_ws.set_scene_item_index(scene_name, source_id, source_index)
    return '', 204


@socialmedia_blueprint.route('/maketableimg/<division>')
def maketableimg(division):
    _settings = get_settings(division)
    table_screaper = NALFtableScraper(_settings['table']['link_to_table'])
    _table = table_screaper.scrape_league_table()
    return render_template('table-img.html', table=_table, division=division, settings=_settings)


# @socialmedia_blueprint.route('/make_yt_short/<video_file>')
# def make_yt_short(video_file):
#
#     apscheduler.add_job(func=BallTracker.track_ball, args=[video_file, apscheduler], id='yt_short')
#     apscheduler.start()
#     return "Zadanie zostało rozpoczęte."
#
# def track_ball(video_file):
#     # Logika śledzenia piłki
#     pass

@socialmedia_blueprint.route('/make_yt_short/<video_file>')
def make_yt_short(video_file):
    t = Thread(target=BallTracker.track_ball, args=[video_file])
    t.start()
    t.join()
    # thread.
    return "Zadanie zostało zakończone."


if __name__ == '__main__':
    # create_app().run(host='0.0.0.0', port=5555, use_reloader=False, debug=True)
    socketio.run(create_app(), host='0.0.0.0', port=5555, allow_unsafe_werkzeug=True, use_reloader=False, debug=True)
