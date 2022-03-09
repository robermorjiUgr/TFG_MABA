from os.path import abspath, dirname, join


# Define the application directory
BASE_DIR = dirname(dirname(abspath(__file__)))


SECRET_KEY   = '447ccb5509b313f43cdc75d94bd5882c50c26299'

# App environments
APP_ENV_LOCAL = 'local'
APP_ENV_TESTING = 'testing'
APP_ENV_DEVELOPMENT = 'development'
APP_ENV_STAGING = 'staging'
APP_ENV_PRODUCTION = 'production'
APP_ENV = ''