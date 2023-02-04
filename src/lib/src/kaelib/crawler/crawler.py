import snscrape.modules.twitter as sntwitter
import tweepy
import tweepy.models
import pandas as pd
import os
import logging


def twitter_search_dataframe_snscrape(
    username: str,
    min_reply: int,
    since: str,
    until: str,
    num_tweets: int,
    temp_path: str,
    log: logging,
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

    query = f"(from:{username}) min_replies:{min_reply} since:{since} until:{until}"

    counter = 1
    temporary_csv_file = f"{temp_path}/temp_{counter}.csv"
    tweets_list = []

    scraper = sntwitter.TwitterSearchScraper(query)

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

    # Delete all files
    for file in files:
        os.remove(f"{temp_path}/{file}")

    return full_df


def twitter_search_reply_dataframe(
    reply_to_username: str,
    min_reply_faves: int,
    conversation_ids,
    since: str,
    until: str,
    temp_path: str,
    log: logging,
) -> pd.DataFrame:

    BATCH = 300
    TWEET_COLUMNS = [
        "tweet_id",
        "tweet_url",
        "tweet_date",
        "tweet_conversation_id",
        "reply_count",
        "like_count",
        "tweet",
    ]

    query = f"(to:{reply_to_username}) min_faves:{min_reply_faves} until:{until} since:{since} -filter:links filter:replies"
    
    log.info(f"Querying: {query}")

    counter = 1
    temporary_csv_file = f"{temp_path}/temp_{counter}.csv"
    tweets_list = []

    scraper = sntwitter.TwitterSearchScraper(query)

    for _, tweet in enumerate(scraper.get_items()):
        if (
            tweet.inReplyToTweetId is None
            or tweet.inReplyToTweetId not in conversation_ids
        ):
            continue

        tweets_list.append(
            [
                tweet.id,
                tweet.url,
                tweet.date,
                tweet.inReplyToTweetId,
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

    # Delete all files
    for file in files:
        os.remove(f"{temp_path}/{file}")

    return full_df

def twitter_search_dataframe_tweepy(
    username: str,
    min_reply: int,
    since: str,
    until: str,
    auth_token: str,
    num_tweets: int,
    temp_path: str,
    log: logging,
) -> pd.DataFrame:

    query = f"(from:{username}) min_replies:{min_reply} since:{since} until:{until}"

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

    # Cursor tracking pagination twitter with date
    str_oldest_tweet = None

    # counter for temporary file
    counter = 1
    temporary_csv_file = f"{temp_path}/temp_{counter}.csv"

    while total_data_crawled < num_tweets:
        results = twitter_api.search_tweets(
            query, count=100, result_type="recent", until=str_oldest_tweet
        )

        # No results
        if len(results) == 0:
            log.info(f"No results. Total crawled {total_data_crawled}")
            break

        # Update cursor pagination using oldest date
        oldest_tweet = results[0].created_at
        str_oldest_tweet = oldest_tweet.strftime("%Y-%m-%d")

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

            # Check and update oldest tweet
            if tweet.created_at < oldest_tweet:
                oldest_tweet = tweet.created_at
                str_oldest_tweet = oldest_tweet.strftime("%Y-%m-%d")

            # Save temp data to csv
            if len(tweets_list) == BATCH:
                pd.DataFrame(tweets_list, columns=TWEET_COLUMNS).to_csv(
                    temporary_csv_file, index=False
                )
                counter += 1
                temporary_csv_file = f"{temp_path}/temp_{counter}.csv"
                tweets_list = []

            # Break if reach total data
            if total_data_crawled == num_tweets:
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

    # Delete all files
    for file in files:
        os.remove(f"{temp_path}/{file}")

    return full_df
