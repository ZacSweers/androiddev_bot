import json
import os
import praw


def retrieve_credentials():
    if os.path.isfile('credentials.json'):
        with open('credentials.json') as data_file:
            return json.load(data_file)
    elif 'HEROKU' in os.environ.keys():
        return {
            "reddit_username": os.environ.get('reddit_username'),
            "reddit_pwd": os.environ.get('reddit_pwd'),
            "slack_key": os.environ.get('slack_key'),
            "slack_token": os.environ.get('slack_token'),
            "channel_id": os.environ.get('channel_id')
        }
    else:
        return None


def get_most_recent_thread(r, keyword):
    """
    A function for retrieving the most recent Automoderator thread with a given keyword

    :param r: Reddit instance for making the search call
    :param keyword: Keyword to search on
    :rtype : praw.objects.Submission
    """
    results = r.search("title:\"" + keyword + " thread\" author:\"AutoModerator\"", subreddit="androiddev", sort="new")
    l = list(results)
    return l[0]
