class Config:
    # GROUP_A = 5
    # GROUP_B = 6
    GROUP_A = 1
    GROUP_B = 3
    DIVISION_CONFIG = {
        3: {
            'regular_round_matches': 80,
        }
    }
    CAMERAS = {}
    OBS_RECORD_STATUS = False
    OBS_STREAM_STATUS = False
    OBS_REPLAY_BUFFER_STATUS = False
    CAMERAS_RECORDING_STATUS = True
    REPLAY_FILE_NAME = None
    FRACTION_TIME = 1
    VIRTUAL_CAMERAS = ['OBS-Camera', 'OBS-Camera2']
    MATCH_IDENTIFIER = '2024-01-01_TEAxTEB'
    MATCHDATA = {'match': {
        'is_timer_active': 0,
        'is_added_time_allowed': 1,
        # 'periods_end_times': [1, 2],
        'current_period': 1
    }}
    TIME_DATA = {'seconds': 0,
                 'added_seconds': 0}
    ACTIONS_SETS = {'no_team_set': [6, 10, 11],
                    'goal_set': [1, 4]}
    PROCESSED_FILES_DIRECTORY = 'C:\\Users\\Filip\\PycharmProjects\\PilotFlask\\static\\video\\processed'
    REPLAYS_FILES_DIRECTORY = 'C:\\Users\\Filip\\PycharmProjects\\PilotFlask\\static\\video\\replays'
    REPLAYS_FILES_ARCH_DIRECTORY = 'C:\\Users\\Filip\\PycharmProjects\\PilotFlask\\static\\video\\replays\\arch'
    OBS_DROP_REPLAY = False
    RECORD_TIME = None
    REPLAY_FILE_TYPE = '.mkv'
    VIDEO_LENGTH = {'C1': 0, 'C2': 0}


class DevelopmentConfig(Config):
    DEBUG = True
    # Other development-specific configurations can be added here.


class ProductionConfig(Config):
    # Configuration for production environment.
    # For example, you might configure the database connection, set secure session options, etc.
    pass
