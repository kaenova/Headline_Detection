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
    config_attr = ["account_username", "min_reply", "since", "until", 
                   "num_crawl", "out_csv"]
    for i in config_attr:
        if i not in config.keys():
            return False
        
    # TODO: Check if 'since' and 'until' is formatted correctly with YYYY-MM-DD
    
    return True
