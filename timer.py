import time
import datetime
from models import Match, Period
from database import db
from flask import current_app
from schemas import period_schema


class Timer:
    def __init__(self, app):
        with app.app_context():
            self.app = app
            self.actual_match = Match.query.filter_by(actual=1).first()
            self.app.config['TIME_DATA']['seconds'] = self.actual_match.seconds
            self.app.config['TIME_DATA']['added_seconds'] = self.actual_match.added_seconds
            self.start_time = time.time()
            self.end_time = time.time()
            self.socketio = self.app.config['SOCKETIO']

    def control_timer(self):
        with self.app.app_context():
            t0 = time.time()
            fraction_time_flag = True
            while True:
                t1 = t0 + self.app.config['FRACTION_TIME']
                _match = self.app.config['MATCHDATA']['match']
                timer_state = self.app.config['MATCHDATA']['match']['is_timer_active']
                seconds = self.app.config['TIME_DATA']['seconds']
                added_seconds = self.app.config['TIME_DATA']['added_seconds']
                _seconds = seconds
                _added_seconds = added_seconds
                is_added_time_allowed = self.app.config['MATCHDATA']['match']['is_added_time_allowed']
                time_limit = self.get_time_limit(self.app.config['MATCHDATA']['match'])
                if timer_state == 0:
                    if fraction_time_flag:
                        self.app.config['FRACTION_TIME'] = 1 - (time.time() - t0)
                        self.save_time_to_db()
                        fraction_time_flag = False
                    t0 = time.time()
                elif timer_state == 1 and time.time() >= t1:
                    self.timer_add_time(seconds=seconds,
                                        added_seconds=added_seconds,
                                        time_limit=time_limit,
                                        is_added_time_allowed=is_added_time_allowed,
                                        difference=1)
                    t0 = time.time()
                    self.app.config['FRACTION_TIME'] = 1
                    fraction_time_flag = True
                elif timer_state == 2:
                    self.timer_reset()
                    t0 = time.time()
                    self.app.config['FRACTION_TIME'] = 1
                    fraction_time_flag = True

    # def get_time_limit(self, match):
    #     periods_end_times = match['periods_end_times']
    #     current_period = match['current_period']
    #     return periods_end_times[current_period - 1]

    def get_time_limit(self, match):
        _period = Period.query.filter_by(id=match['current_period']).first()
        return _period.end_time

    def timer_add_time(self, seconds: int,
                       added_seconds: int,
                       time_limit: int,
                       is_added_time_allowed: int,
                       difference: int):

        seconds += difference
        if seconds <= time_limit:
            added_seconds = 0
        else:
            if is_added_time_allowed:
                added_seconds = seconds - time_limit
        self.app.config['TIME_DATA']['seconds'] = seconds
        self.app.config['TIME_DATA']['added_seconds'] = added_seconds
        self.socketio.emit('update_time', {'seconds': seconds, 'added_seconds': added_seconds})
        if not seconds % 10:
            match = Match.query.filter_by(actual=1).first()
            match.seconds = seconds
            match.added_seconds = added_seconds
            db.session.commit()

    def timer_reset(self):
        self.app.config['TIME_DATA']['seconds'] = 0
        self.app.config['TIME_DATA']['added_seconds'] = 0
        self.save_time_to_db()
        self.socketio.emit('update_time', {'seconds': 0, 'added_seconds': 0})

    def save_time_to_db(self):
        match = Match.query.filter_by(actual=1).first()
        match.seconds = self.app.config['TIME_DATA']['seconds']
        match.added_seconds = self.app.config['TIME_DATA']['added_seconds']
        db.session.commit()

