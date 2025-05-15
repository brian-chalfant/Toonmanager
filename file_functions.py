import json
import random
from os.path import isfile, join
from os import listdir, remove
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename="logs/toonmng.log", level=logging.INFO)
PATHS = {'test': "testing"}

def save_file(dict, path_key, name_override=None):

    if not name_override:
        filename = dict["name"] + "_" + str(random.randint(1000000, 9999999))
    else:
        filename = name_override
    with open(PATHS[path_key] + "/" +filename + ".json", 'w') as fp:
        json.dump(dict, fp)


def open_file(filename, path_key):

    if(isfile(PATHS[path_key] + "/" + filename + ".json")):
        with open(PATHS[path_key] + "/" +filename + ".json", 'r') as fp:
            logger.info(f"opening {filename} in {PATHS[path_key]}")
            dict = json.load(fp)
            return dict
    else:
        logger.warning(f"{filename} file does not exist")

def list_files(path_key, file_type):

    return [f for f in listdir(PATHS[path_key] + "/") if f.endswith(file_type)]


def remove_file(filename, path_key):
        try:
           remove(PATHS[path_key] + "/" + filename)
           return True
        except OSError as e:
           logger.warning(f"{filename} could not be removed: {e}")

#[f for f in listdir(paths[path_key]) if (isfile(join(paths[path_key], f)))]

