# Globals
import datetime
import getopt
import time
import sys

import praw
from slacker import Slacker

from config import (
    weekly_threads,
    post_is_suspicious
)

from util import (
    retrieve_credentials,
    get_most_recent_thread
)


post_limit = 10
dry_run = False


def notify_slack(submission):
    slack = Slacker(credentials['slack_key'])

    message = '========================'
    if post_is_suspicious(submission):
        message += '\n\n@everyone: *SUSPICIOUS*'
    message += '\n\n*%s*' % submission.title
    message += '\n\nID: %s' % submission.id
    message += '\n\nComments link: %s' % submission.permalink
    if submission.url and 'www.reddit.com' not in submission.url:
        message += '\n\nPost link: %s' % submission.url
    if submission.selftext:
        message += '\n\n> %s' % submission.selftext.partition('\n')[0]
    slack.chat.post_message('#newposts', message, as_user='postbot')


if __name__ == '__main__':
    credentials = retrieve_credentials()
    channel_id = credentials['channel_id']

    # Set up praw
    r = praw.Reddit('androiddev_watcher by /u/pandanomic')
    r.login(credentials['reddit_username'], credentials['reddit_pwd'], disable_warning=True)
    subreddit = r.get_subreddit('androiddev')

    try:
        opts, args = getopt.getopt(sys.argv[1:], "dpu:", ["dry", "poll", "unsticky="])
    except getopt.GetoptError:
        print('check_and_delete.py -d -p -u')
        sys.exit(2)

    if len(opts) != 0:
        for o, a in opts:
            if o in ("-d", "--dry"):
                dry_run = True
            elif o in ("-p", "--poll"):
                now = datetime.datetime.utcnow()
                now_minus_10 = now + datetime.timedelta(minutes=-10)
                float_now = time.mktime(now_minus_10.timetuple())
                print("Checking for new posts")
                posts = [p for p in subreddit.get_new(limit=post_limit) if p.created_utc > float_now]
                if len(posts) is 0:
                    print("Nothing new")
                else:
                    print("Length is %s" % len(posts))
                    for post in sorted(posts, key=lambda p: p.created_utc):
                        if not dry_run:
                            notify_slack(post)
                        print("Notified")
            elif o in ("-u", "--unsticky"):
                if a in weekly_threads and datetime.datetime.now().strftime("%A") != weekly_threads[a]['day']:
                    print("%s threads should will only be removed on %ss" % (
                        weekly_threads[a]['name'].capitalize(), weekly_threads[a]['day']))
                    break
                sub = get_most_recent_thread(r, a)
                if not dry_run:
                    sub.unsticky()
                print("Unstickied %s" % sub.url)
            else:
                sys.exit('No valid args specified')
