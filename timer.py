import time
import datetime
from models import Match
from database import db
from flask import current_app


class Timer:
    def __init__(self, app):
        with app.app_context():
            self.actual_match = Match.query.filter_by(actual=1).first()
            self.start_time = time.time()
            self.end_time = time.time()

    def control_timer(self, app):
        with app.app_context():
            # self.start_time = time.time()
            while True:
                if Match.query.filter_by(actual=1).first().is_timer_active == 1:
                    self.timer_add_seconds(seconds=1)
                elif Match.query.filter_by(actual=1).first().is_timer_active == 2:
                    self.timer_add_seconds(seconds=0)
                    self.timer_reset()
                else:
                    self.timer_add_seconds(seconds=0)
                time.sleep(1)

    def timer_add_seconds(self, seconds: int):
        match_time = Match.query.filter_by(actual=1).first().seconds
        match_time += seconds
        Match.query.filter_by(actual=1).first().seconds = match_time
        db.session.commit()

    def timer_reset(self):
        Match.query.filter_by(actual=1).first().seconds = 0
        db.session.commit()
