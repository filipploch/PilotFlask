

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
    OBS_DROP_REPLAY = False
    CAMERAS_RECORDING_STATUS = True
    REPLAY_FILE_NAME_PREFIX = None
    VIRTUAL_CAMERAS = ['OBS-Camera', 'OBS-Camera2']


class DevelopmentConfig(Config):
    DEBUG = True
    # Other development-specific configurations can be added here.


class ProductionConfig(Config):
    # Configuration for production environment.
    # For example, you might configure the database connection, set secure session options, etc.
    pass