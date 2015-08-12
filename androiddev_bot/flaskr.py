import getopt
import json
import os
import shlex
from urllib.parse import parse_qs

from flask import (
    Flask,
    request,
    Response
)
import praw
from slacker import Slacker
from rx import Observable, Observer
from rx.concurrency import new_thread_scheduler

from util import (
    retrieve_credentials,
    get_most_recent_thread
)
from config import cans


standard_commands = [
    'rm',
    'flair',
    'ban',
    'running',
    'help'
]


def process_command(text):
    print("Text is %s" % text)
    argv = shlex.split(text)
    print("Tokenized text is %s" % str(argv))

    if len(argv) < 2:
        return 'usage: postbot %s' % standard_commands

    command = argv[1]
    if command not in standard_commands or command == 'help':
        return 'usage: postbot %s' % standard_commands
    elif command == 'running':
        return 'banana'

    if len(argv) < 4:
        return 'usage: postbot %s' % standard_commands

    target = argv[2]
    args = argv[3:]

    if command == 'rm':
        # target is the post id
        try:
            opts, args = getopt.getopt(args, "sm:c:", ["spam", "message=", "canned="])
        except getopt.GetoptError as err:
            return str(err)

        is_spam = False
        comment_text = None

        for o, a in opts:
            if o in ("-s", "--spam"):
                is_spam = True
            elif o in ("-m", "--message"):
                comment_text = a
                break  # Only take one of message or canned
            elif o in ("-c", "--canned"):
                comment_text = cans[a]
                if a == "questions_thread":
                    comment_text = comment_text + "\n\nToday's thread can be found here: " \
                                                + get_most_recent_thread(r, "questions").url
                break  # Only take one of message or canned

        has_comment = comment_text is not None

        # Now delete
        submission = r.get_submission(submission_id=target)
        if has_comment:
            comment = submission.add_comment(comment_text)
            comment.distinguish()
        submission.remove(spam=is_spam)
        return "Deleted!"
    elif command == 'flair':
        text = args[0]
        submission = r.get_submission(submission_id=target)
        submission.set_flair(text)
        return "Flaired!"
    elif command == 'ban':
        # # target is the user id
        # try:
        # opts, args = getopt.getopt(args, "tm:n:", ["temp", "message=", "note="])
        # except getopt.GetoptError as err:
        #     return str(err)
        #
        # # TODO ban the user
        # subreddit.add_ban(target)
        return "Unsupported until next version of PRAW"

    return 'Something went wrong...'


def send_message(response_text):
    if response_text.startswith("postbot"):
        # NO DON'T DO THAT BECAUSE THE TRIGGER WILL INFINITE LOOP
        response_text = "//" + response_text
    slack.chat.post_message('#newposts', response_text, as_user='postbot')


class BotObserver(Observer):
    def on_next(self, x):
        print("Got: %s" % x)
        if x.startswith("postbot"):
            # NO DON'T DO THAT BECAUSE THE TRIGGER WILL INFINITE LOOP
            x = "//" + x
        slack.chat.post_message('#newposts', x, as_user='postbot')

    def on_error(self, e):
        print("Got error: %s" % e)
        slack.chat.post_message('#newposts', "Something went wrong, see logs", as_user='postbot')

    def on_completed(self):
        print("Sequence completed")


app = Flask(__name__)
app.config['DEBUG'] = True

credentials = retrieve_credentials()
slack = Slacker(credentials['slack_key'])

# Set up praw
r = praw.Reddit('androiddev_slacker by /u/pandanomic')
r.login(credentials['reddit_username'], credentials['reddit_pwd'], disable_warning=True)
subreddit = r.get_subreddit('androiddev')


@app.route('/message', methods=['POST'])
def message():
    data = parse_qs(request.get_data(False, True, False))

    # For some reason these values are lists first
    data = {x: data[x][0] for x in data}
    token = data['token']

    print("Credentials are - \n" + str(credentials))
    print("Token received is " + token)
    print("Stored token   is " + credentials['slack_token'])

    # Verify it came from slack
    if token != credentials['slack_token']:
        return Response(json.dumps({'text': 'Invalid'}), status=403, mimetype='application/json')
    else:
        message_data = data['text']
        Observable.just(message_data, new_thread_scheduler)\
            .map(lambda s: process_command(s))\
            .subscribe(BotObserver())\

    resp = Response(None, status=200, mimetype='application/json')
    return resp


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
