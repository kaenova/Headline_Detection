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
TWITTER_USERNAMES = [
    # "CNNIndonesia",
    "detikcom",
    # "tvOneNews",
    # "VIVAcoid",
    
    # "kompascom",
    # "KompasTV",
    # "kumparan",
    # "liputan6dotcom",
    # "republikaonline",
    # "tempodotco",
]

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
api_key = RUN_CONFIG["api_key"]
min_reply = RUN_CONFIG["min_reply"]
since = RUN_CONFIG["since"]
until = RUN_CONFIG["until"]
number_tweets = RUN_CONFIG["num_crawl"]

for i in TWITTER_USERNAMES:
    logging.info(f"Retrieving @{i}")
    
    query = f"(from:{i}) min_replies:{min_reply} since:{since} until:{until}"
    logging.info(query)

    # Crawl data
    out_csv_path = RUN_CONFIG["out_csv"]
    df = crawler.twitter_search_dataframe_snscrape(query, number_tweets, TEMP_RUN_DIR, logging)
    total_data = len(df)
    logging.info(f"crawled {i} with total_data {total_data}")
    df.to_csv(f"{out_csv_path}/{i}.csv", index=False)