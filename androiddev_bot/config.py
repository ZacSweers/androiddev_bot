import praw

# Put your vars here
suspect_title_strings = ['?', 'help', 'stuck', 'why', 'my', 'feedback']

subreddit = 'androiddev'

# Canned responses
cans = {
    'questions_thread': "Removed because, per sub rules, this doesn't merit its own post. We have a questions thread every day, please use it for questions like this.",
    'rules': 'Removed because posts like this are against the sub rules.',
    'wiki': "Removed because relevant information can be found in the /r/androiddev [wiki](https://www.reddit.com/r/androiddev/wiki/index)"
}

# Specify the keyword and what days they should be removed
weekly_threads = {
    'anything': {
        'day': 'Saturday',
        'name': 'Weekly \"anything goes\"'
    },
    'hiring': {
        'day': 'Monday',
        'name': 'Weekly \"who\'s hiring?\"'
    }
}

flair_mapping = {
    'Library': 'library',
    'Discussion': 'discussion',
    'News': 'news',
    'Tech Talk': 'talk',
}


def post_is_suspicious(post_to_check: praw.objects.Submission) -> bool:
    """
    A function that can be passed a submission to check against and return whether or not it's "suspicious" or otherwise
    deserving of closer attention.

    :type post_to_check: praw.objects.Submission
    :rtype : bool
    :param post_to_check: The Submission instance to check
    :return: True if suspicious, False if now
    """
    return \
        any(word in post_to_check.title.lower() for word in suspect_title_strings) \
        or post_to_check.domain == 'stackoverflow.com' \
        or (post_to_check.selftext and 'stackoverflow' in post_to_check.selftext.lower()) \
        or (post_to_check.selftext_html and any(block in post_to_check.selftext_html for block in ['<code', '%3Ccode']))
