# Globals
import praw
import time
from slacker import Slacker
from util import retrieve_credentials

suspect_title_strings = ['?', 'help', 'stuck', 'why', 'my', 'feedback']
post_limit = 10


def post_is_suspicious(post_to_check):
    return \
        any(word in post_to_check.title.lower() for word in suspect_title_strings) \
        or post_to_check.domain == 'stackoverflow.com' \
        or (post_to_check.selftext and 'stackoverflow' in post_to_check.selftext.lower()) \
        or (post_to_check.selftext_html and any(block in post_to_check.selftext_html for block in ['<code', '%3Ccode']))


def notify_slack(submission):
    message = '========================'
    message += '\n\n*%s*' % submission.title
    message += '\n\nID: %s' % submission.id
    message += '\n\nComments link: %s' % submission.permalink
    if submission.url and 'www.reddit.com' not in submission.url:
        message += '\n\nPost link: %s' % submission.url
    if submission.selftext:
        message += '\n\n> %s' % submission.selftext.partition('\n')[0]
    slack.chat.post_message('#newposts', message, as_user='postbot')


credentials = retrieve_credentials()
channel_id = credentials['channel_id']

# Set up slack
slack = Slacker("")

# Set up praw
r = praw.Reddit('androiddev_watcher by /u/pandanomic')
r.login(credentials['reddit_username'], credentials['reddit_pwd'])
subreddit = r.get_subreddit('androiddev')

old_time = time.time()  # Start with the current time
while True:
    print("Checking for new posts")
    posts = [p for p in subreddit.get_new(limit=post_limit) if p.created_utc > old_time]
    if len(posts) is 0:
        print("Nothing new")
    else:
        print("Length is %s" % len(posts))
        for post in sorted(posts, key=lambda p: p.created_utc):
            old_time = post.created_utc
            print("Post is suspicious, notifying")
            notify_slack(post)
            print("Notified")
    time.sleep(300)