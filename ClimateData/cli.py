from preprocess import processFiles, create_working_directory
from database import setup_database
from UI import start_ui

if __name__ == '__main__':
  # preprocess files
  create_working_directory()
  processFiles()

  # build database
  # we need a way to run this only when we need to rebuild the database
  setup_database()

  # start UI
  start_ui()

