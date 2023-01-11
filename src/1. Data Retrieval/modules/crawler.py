import snscrape.modules.twitter as sntwitter
import pandas as pd
import os
import logging


def twitter_search_dataframe(
    query: str, num_tweets: int, temp_path: str, log: logging
) -> pd.DataFrame:
    BATCH = 300
    TWEET_COLUMNS = ["tweet_id", "tweet_url", "tweet_date", 
                     "reply_count", "like_count", "tweet"]
    counter = 1
    temporary_csv_file = f"{temp_path}/temp_{counter}.csv"
    tweets_list = []
    
    scraper = sntwitter.TwitterSearchScraper(query, top=True)

    for i, tweet in enumerate(scraper.get_items()):
        tweets_list.append([tweet.id, tweet.url, tweet.date, tweet.replyCount, tweet.likeCount, tweet.rawContent])

        # Create csv batch and reset tweets_list
        if len(tweets_list) == BATCH:
            pd.DataFrame(tweets_list, columns=TWEET_COLUMNS).to_csv(
                temporary_csv_file, index=False
            )
            counter += 1
            temporary_csv_file = f"{temp_path}/temp_{counter}.csv"
            tweets_list = []

        if i == num_tweets:
            break

    pd.DataFrame(tweets_list, columns=TWEET_COLUMNS).to_csv(
        temporary_csv_file, index=False
    )
    del tweets_list, counter, temporary_csv_file

    # Load all csv in temporary path
    files = os.listdir(temp_path)
    dfs = []
    for i in files:
        file_path = f"{temp_path}/{i}"
        # TODO: Check if file is a valid csv
        try:
            dfs.append(pd.read_csv(file_path, engine="python"))
        except Exception:
            log.warning(f"Cannot load file '{file_path}'")
    full_df = pd.concat(dfs).reset_index(drop=True)
    
    return full_df