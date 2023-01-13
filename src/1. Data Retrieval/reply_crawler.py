import os
import logging
import pandas as pd
import modules.config as config
import modules.crawler as crawler
import uuid
from datetime import datetime

# Setup environment
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
RUN_ID = str(uuid.uuid4())
logging.info(f"Run ID: {RUN_ID}")
logging.info("Preparing environemnt")
TEMP_DIR = "./temp"
TEMP_RUN_DIR = f"{TEMP_DIR}/{RUN_ID}"
CONFIG_PATH = "./src/1. Data Retrieval/reply_config.json"
CONFIG_EXAMPLE_PATH = "./src/1. Data Retrieval/reply_config.example.json"

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
username = RUN_CONFIG["username"]
in_csv = RUN_CONFIG["in_csv"]
out_csv = RUN_CONFIG["out_csv"]
min_faves = RUN_CONFIG["min_faves"]

# Read in CSV
df_in = pd.read_csv(in_csv)
df_in_cols = df_in.columns.values.tolist()
if "tweet_id" not in df_in_cols or "tweet_date" not in df_in_cols:
    raise Exception(
        "df_in doesnt have tweet_id columns which represent an id of a tweet or df_in doesnt have tweet_date columns which represent the date creation of a tweet in ISO Format"
    )

# Get since and until params from tweet_date
all_date = df_in["tweet_date"].map(lambda x: datetime.fromisoformat(x)).sort_values()
newest_date = all_date[0]
oldest_date = all_date[len(all_date) - 1]
newest_date_str = newest_date.strftime("%Y-%m-%d")
oldest_date_str = oldest_date.strftime("%Y-%m-%d")

# Get all conversation ids
ids = tuple(df_in['tweet_id'].sort_values().values.tolist())

final_df = crawler.twitter_search_reply_dataframe(username, min_faves, ids, oldest_date_str, newest_date_str, TEMP_RUN_DIR, logging)

total_data = len(final_df)
logging.info(f"crawled with total_data {total_data}")

final_df.to_csv(out_csv, index=False)
