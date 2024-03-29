import json
import os
import logging

def load_config(path: str, log: logging) -> dict:
    if not (os.path.isfile(path)):
        log.fatal(f"Config not defined, please create config file in '{path}'")
        exit(1)
    f = open(path)
    config = json.load(f)
    f.close()
    return config

def check_headline_config(config: dict) -> bool:
    """
    Returns true if config is valid
    """
    config_attr = ["min_reply", "since", "until", 
                   "num_crawl", "out_csv", "api_key"]
    for i in config_attr:
        if i not in config.keys():
            return False
        
    # TODO: Check if 'since' and 'until' is formatted correctly with YYYY-MM-DD
    
    return True

def check_reply_config(config: dict) -> bool:
    """
    Returns true if config is valid
    """
    config_attr = ["username", "in_csv", "out_csv", "min_faves"]
    for i in config_attr:
        if i not in config.keys():
            return False
        
    # TODO: Check if 'since' and 'until' is formatted correctly with YYYY-MM-DD
    
    return True
