import snscrape.modules.twitter as sntwitter
import tweepy
import tweepy.models
import pandas as pd
import os
import logging


def twitter_search_dataframe_snscrape(
    query: str, num_tweets: int, temp_path: str, log: logging
) -> pd.DataFrame:
    BATCH = 300
    TWEET_COLUMNS = [
        "tweet_id",
        "tweet_url",
        "tweet_date",
        "reply_count",
        "like_count",
        "tweet",
    ]
    counter = 1
    temporary_csv_file = f"{temp_path}/temp_{counter}.csv"
    tweets_list = []

    scraper = sntwitter.TwitterSearchScraper(query, top=True)

    for i, tweet in enumerate(scraper.get_items()):
        tweets_list.append(
            [
                tweet.id,
                tweet.url,
                tweet.date,
                tweet.replyCount,
                tweet.likeCount,
                tweet.rawContent,
            ]
        )

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


def twitter_search_dataframe_tweepy(
    auth_token: str, query: str, num_tweets: int, temp_path: str, log: logging
) -> pd.DataFrame:
    BATCH = 10
    TWEET_COLUMNS = [
        "tweet_id",
        "tweet_url",
        "tweet_date",
        "favorite_count",
        "retweet_count",
        "tweet",
    ]
    
    # Auth and create clients
    auth = tweepy.OAuth2BearerHandler(auth_token)
    twitter_api = tweepy.API(auth)
    
    total_data_crawled = 0
    tweets_list = []
    
    # Cursor tracking pagination twittera
    last_tweet_id = None
    
    # counter for temporary file
    counter = 1
    temporary_csv_file = f"{temp_path}/temp_{counter}.csv"
    
    while total_data_crawled < num_tweets:
        results = twitter_api.search_tweets(query, 
                                            result_type='recent', 
                                            since_id=last_tweet_id)
        
        # No results
        if len(results) == 0:
            log.info(f"No results. Total crawled {total_data_crawled}")
            break
        
        # Update cursor
        last_tweet_id = results.max_id
        
        for tweet in results:
            tweet_id = tweet.id_str
            author_username = tweet.author.screen_name
            tweet_url = f"https://twitter.com/{author_username}/status/{tweet_id}"
            tweet_created = tweet.created_at.isoformat()
            
            tweets_list.append(
                [
                    tweet_id,
                    tweet_url,
                    tweet_created,
                    tweet.favorite_count,
                    tweet.retweet_count,
                    tweet.text,
                ]
            )
            
            total_data_crawled += 1
            
            if len(tweets_list) == BATCH:
                pd.DataFrame(tweets_list, columns=TWEET_COLUMNS).to_csv(
                    temporary_csv_file, index=False
                )
                counter += 1
                temporary_csv_file = f"{temp_path}/temp_{counter}.csv"
                tweets_list = []
            
            if (total_data_crawled == num_tweets):
                break
    
    # Save remaining tweet_list
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
