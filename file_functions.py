import json
import random
from os.path import isfile, join
from os import listdir, remove, makedirs
from logging_config import get_logger

logger = get_logger(__name__)

PATHS = {
    'test': "testing",
    'characters': "characters",
    'data': "data"
}

# Ensure required directories exist
for directory in PATHS.values():
    makedirs(directory, exist_ok=True)

def save_file(dict, path_key, name_override=None):
    try:
        if not name_override:
            filename = dict["name"] + "_" + str(random.randint(1000000, 9999999))
        else:
            filename = name_override
            
        filepath = f"{PATHS[path_key]}/{filename}.json"
        logger.debug(f"Saving file to: {filepath}")
        
        with open(filepath, 'w') as fp:
            json.dump(dict, fp)
            logger.info(f"Successfully saved file: {filepath}")
            
    except Exception as e:
        logger.error(f"Failed to save file {filename}: {e}")
        raise

def open_file(filename, path_key):
    filepath = f"{PATHS[path_key]}/{filename}.json"
    
    try:
        if not isfile(filepath):
            logger.error(f"File not found: {filepath}")
            raise FileNotFoundError(f"{filename} file does not exist")
            
        logger.debug(f"Opening file: {filepath}")
        with open(filepath, 'r') as fp:
            dict = json.load(fp)
            logger.info(f"Successfully opened file: {filepath}")
            return dict
            
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from {filepath}: {e}")
        raise
    except Exception as e:
        logger.error(f"Error opening file {filepath}: {e}")
        raise

def list_files(path_key, file_type):
    try:
        directory = PATHS[path_key] + "/"
        logger.debug(f"Listing files in {directory} with type {file_type}")
        
        files = [f for f in listdir(directory) if f.endswith(file_type)]
        logger.info(f"Found {len(files)} files with type {file_type} in {directory}")
        return files
        
    except Exception as e:
        logger.error(f"Error listing files in {directory}: {e}")
        raise

def remove_file(filename, path_key):
    filepath = f"{PATHS[path_key]}/{filename}"
    
    try:
        logger.debug(f"Attempting to remove file: {filepath}")
        remove(filepath)
        logger.info(f"Successfully removed file: {filepath}")
        return True
        
    except OSError as e:
        logger.error(f"Failed to remove file {filepath}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error removing file {filepath}: {e}")
        raise

#[f for f in listdir(paths[path_key]) if (isfile(join(paths[path_key], f)))]

