from preprocess import processFiles, create_working_directory
from database import setup_database
from UI import start_ui
from config import config_load, config_save, config_set_db_last_updated_utc_now, config_get_db_last_updated

if __name__ == '__main__':
  # read config
  config_load()

  # if first time startup, run preprocess and db setup
  if config_get_db_last_updated() is None:

    # preprocess files
    create_working_directory()
    processFiles()

    # build database
    setup_database()

    # update db last updated
    config_set_db_last_updated_utc_now()
    config_save()

  # start UI
  start_ui()

