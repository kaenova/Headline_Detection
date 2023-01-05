import os
import logging
import pandas
import modules.config as config
import modules.crawler as crawler
import uuid

# Setup environment
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
RUN_ID = str(uuid.uuid4())
logging.info(f"Run ID: {RUN_ID}")
logging.info("Preparing environemnt")
TEMP_DIR = "./temp"
TEMP_RUN_DIR = f"{TEMP_DIR}/{RUN_ID}"
CONFIG_PATH = "./src/1. Data Retrieval/headline_config.json"
CONFIG_EXAMPLE_PATH = "./src/1. Data Retrieval/headline_config.example.json"

# Get configuration
RUN_CONFIG = config.load_config(CONFIG_PATH, logging)
if not (config.check_headline_config(RUN_CONFIG)):
    logging.fatal(f"Invalid config, please check the example at {CONFIG_EXAMPLE_PATH}")
logging.info("Valid config")

# Create temp folder
if not (os.path.isdir(TEMP_DIR)):
    os.mkdir(TEMP_DIR)

# Create run temp folder
if not (os.path.isdir(TEMP_RUN_DIR)):
    os.mkdir(TEMP_RUN_DIR)

# Build query
min_reply = RUN_CONFIG["min_reply"]
account_username = RUN_CONFIG["account_username"]
since = RUN_CONFIG["since"]
until = RUN_CONFIG["until"]
number_tweets = RUN_CONFIG["num_crawl"]
query = f"(from:{account_username}) min_replies:{min_reply} since:{since} until:{until}"

# Crawl data
out_csv_path = RUN_CONFIG["out_csv"]
df = crawler.twitter_search_dataframe(query, number_tweets, TEMP_RUN_DIR, logging)
df.to_csv(out_csv_path, index=False)