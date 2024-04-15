

class Config:
    GROUP_A = 1
    GROUP_B = 3


class DevelopmentConfig(Config):
    DEBUG = True
    # Other development-specific configurations can be added here.


class ProductionConfig(Config):
    # Configuration for production environment.
    # For example, you might configure the database connection, set secure session options, etc.
    pass