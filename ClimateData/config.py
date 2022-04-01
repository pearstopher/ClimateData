import json
import os
from datetime import datetime, date

# Config path
_config_path = 'config.json'

# Config object
_config = {}
_config_default = {
  "Database": {
    "Host": "localhost",
    "Name": "postgres",
    "User": "postgres",
    "Password": "PASSWORD",
    "LastUpdated": None
  }
}

# loads configuration from the config file
def config_load():
  # initialize with defaults
  _config.update(_config_default.copy())

  # if config file doesn't exist, create new with defaults
  if os.path.exists(_config_path):
    with open(_config_path, 'r') as f:
      _config.update(json.load(f))
  else:
    config_save()

# saves configuration to config file
def config_save():
  with open(_config_path, 'w') as w:
    w.write(json.dumps(_config, indent=4))

# whether or not the config has the given path
# path is a list of strings
def config_has(path):
  if _config is None:
    return False

  # check each string in path
  item = _config
  for field in path:
    if field not in item:
      return False
    item = item[field]
  
  return True

# returns the config value at path or the default value at path
# path is a list of strings
def config_get(path):
  item = _config if config_has(path) else _config_default
  for field in path:
    item = item[field]
  
  return item

# returns the config value at path or the default value at path
# path is a list of strings
def config_set(path, value):
  item = _config
  path_len = len(path)
  for i in range(path_len):
    is_last = i == (path_len-1)
    field = path[i]

    if is_last:
      item[field] = value
    elif field not in item:
      item[field] = {}
    
    item = item[field]


#DATABASE SECTION---------------------------------------------------------------------
def config_get_db_host() -> str:
  return config_get(["Database", "Host"])
def config_set_db_host(host):
  config_set(["Database", "Host"], host)

def config_get_db_name() -> str:
  return config_get(["Database", "Name"])
def config_set_db_name(name):
  config_set(["Database", "Name"], name)

def config_get_db_user() -> str:
  return config_get(["Database", "User"])
def config_set_db_user(user):
  config_set(["Database", "User"], user)

def config_get_db_password() -> str:
  return config_get(["Database", "Password"])
def config_set_db_password(password):
  config_set(["Database", "Password"], password)

def config_get_db_last_updated() -> datetime:
  try:
    return datetime.fromisoformat(config_get(["Database", "LastUpdated"]))
  except:
    return None
def config_set_db_last_updated(last_updated: datetime):
  config_set(["Database", "LastUpdated"], last_updated.isoformat())
def config_set_db_last_updated_utc_now():
  config_set_db_last_updated(datetime.utcnow())
