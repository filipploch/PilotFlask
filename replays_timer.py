import time
import os
from utils.file_utils import get_video_length


class ReplaysTimer:
    def __init__(self, app):
        self.app = app
        self.obs_ws = self.app.config['obs_ws']

    def start_timer(self):
        with self.app.app_context():
            recording_start_time = self.app.config['RECORDING_START_TIME']
            t0 = time.time()
            while self.app.config['OBS_RECORD_STATUS']:
                if time.time() >= t0 + 1:
                    recording_start_time += 1
                    self.app.config['RECORD_TIME'] = recording_start_time
                    print('recording_start_time:', recording_start_time)
                    t0 = time.time()
            # files_number = count_files_with_name_fragment(self.app.config['PROCESSED_FILES_DIRECTORY'],
            #                                               self.app.config['RECORDING_FILE_NAME'])


    def get_recording_start_time(self):
        _recording_filename = f"C1_{self.app.config['MATCH_IDENTIFIER']}_output.mp4"
        _directory = self.app.config['REPLAYS_FILES_DIRECTORY']
        _video_path = f"{_directory}\\{_recording_filename}"
        if os.path.exists(_video_path):
            print('video_length:', get_video_length(_video_path))
            return get_video_length(_video_path)
        print('video_length:', 0)
        return 0
