import time
import datetime
from models import Match
from database import db
from variables import MATCH_ID


class Timer:
    def __init__(self, app):
        with app.app_context():
            self.seconds = Match.query.get(MATCH_ID).seconds

    def start_timer(self, app):
        with app.app_context():
            time_lapsed = 0.0
            start_time = time.time()
            actual_match = Match.query.filter_by(id=MATCH_ID).first()
            while True:
                print('timer is_timer_active', Match.query.filter_by(id=MATCH_ID).first().is_timer_active)
                if Match.query.filter_by(id=MATCH_ID).first().is_timer_active == 1:
                    time.sleep(0.1)
                    end_time = time.time()

                    if end_time - start_time >= 0.5:
                        time_lapsed += 0.5
                        start_time = time.time()
                        if time_lapsed.is_integer():
                            self.seconds += 1
                            actual_match.seconds = self.seconds
                            db.session.commit()
                            print(datetime.timedelta(seconds=self.seconds), flush=True)
                else:
                    time.sleep(0.1)
                    print('timer not active', flush=True)
