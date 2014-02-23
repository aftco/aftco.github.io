from os import path, listdir
import re
import sys
from git import Repo
import twitter


PROJECT_ROOT = path.normpath(path.join(path.dirname(path.realpath(__file__)), '..'))

API_CONSUMER_KEY='TGkY2yQ249sPGtamuNjLUg'
ACCESS_TOKEN_KEY='2326396458-eO0zImMateqrGnkGhF46mglyL77preju5HaOQVC'

DEFAULT_GIT_REPO = path.join(PROJECT_ROOT)
DEFAULT_WORKING_BRANCH = "auto/post_tweeter"
DEFAULT_REMOTE_TO_CHECK = "origin"
DEFAULT_BRANCH_TO_CHECK = "master"

FILE_PARSE_REGEX = re.compile("^.*/(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})-(?P<file>.+)\.\w{2,4}$",re.IGNORECASE)
URL_FORMAT="http://2handnews.com/{}/{}/{}/{}.html"
TITLE_REGEX = re.compile("^title\:\s\"?(?P<title>.+?)\"?$", re.IGNORECASE)
TAGS_REGEX = re.compile("^tags\:\s\"?(?P<tags>.+?)\"?$", re.IGNORECASE)
LINK_REGEX = re.compile("^link\:\s\"?(?P<link>.+?)\"?$", re.IGNORECASE)

PREFERRED_TAGS = ['lions', 'tigers', 'pistons', 'redwings', 'uofm', 'msu', 'cmu', 'mtu']


def get_post_list(repo_path):
    pd = path.join(repo_path, "_posts")
    return [ path.join(pd,f) for f in listdir(pd) if path.isfile(path.join(pd,f)) ]


def get_new_posts(git_repo_path, remote, branch, working_branch):
    remote_branch = "{}/{}".format(remote, branch)

    repo = Repo(git_repo_path)

    # create the working branch if it doesn't exist
    if working_branch not in repo.heads:
        repo.create_head(working_branch, remote_branch)

    # checkout working branch
    repo.heads[working_branch].checkout()

    # fetch from the remote
    repo.remotes[remote].fetch()

    # are there any changes between source and working branches?
    if repo.heads[working_branch].commit == repo.remotes[remote].refs[branch].commit:
        return []

    before_posts = get_post_list(git_repo_path)

    # merge remote branch into working branch
    repo.git.merge(remote_branch)

    after_posts = get_post_list(git_repo_path)
    if len(before_posts) >= len(after_posts):
        return []

    results = []
    for p in after_posts:
        if p not in before_posts:
            results.append(p)

    return results


def revert_git(git_repo_path, branch):
    repo = Repo(git_repo_path)
    repo.heads[branch].checkout()


class Post(object):
    def __init__(self):
        self.url = None
        self.title = None
        self.tags = None
        self.link = None

    def get_tag_text(self, tag, allowed_chars, used_chars):
        if len(tag) + 2 > (allowed_chars - used_chars):
            return None

        return " #" + tag

    def format_for_twitter(self):
        allowed_chars = 140 # number of character twitter allows
        used_chars = 22 # 22 is the number of chars taken by a link

        title = self.title.strip()
        if len(title) > (allowed_chars - used_chars):
            left = allowed_chars - used_chars - 3
            title = title[:left] + "..."

        used_chars += len(title)

        tweet = title + " " + self.url
        if self.tags is None or len(self.tags) == 0 or (allowed_chars - used_chars) < 5:
            return tweet

        used_tags = []
        # preferred tag sweep
        for t in self.tags:
            if t.lower() in PREFERRED_TAGS and t not in used_tags:
                tag_text = self.get_tag_text(t, allowed_chars, used_chars)
                if tag_text is not None:
                    used_tags.append(t)
                    tweet += tag_text
                    used_chars += len(tag_text)

        # second sweep for any non-preferred tags that will fit
        for t in self.tags:
            if t not in used_tags:
                tag_text = self.get_tag_text(t, allowed_chars, used_chars)
                if tag_text is not None:
                    used_tags.append(t)
                    tweet += tag_text
                    used_chars += len(tag_text)

        # final sanity check
        if len(tweet) > allowed_chars:
            return tweet[:allowed_chars]

        return tweet

    @staticmethod
    def read(post_file):
        try:
            fmatch = FILE_PARSE_REGEX.match(post_file)
            if fmatch is None:
                print("Unexpected file name for post '{}'. Skipping.".format(post_file))
                return None

            pf = fmatch.groupdict()

            p = Post()
            with open(post_file, 'r') as f:
                for l in f:
                    tmatch = TITLE_REGEX.match(l)
                    if tmatch is not None:
                        p.title = tmatch.groupdict()['title']

                    gmatch = TAGS_REGEX.match(l)
                    if gmatch is not None:
                        p.tags = gmatch.groupdict()['tags']
                        p.tags = p.tags.split()

                    lmatch = LINK_REGEX.match(l)
                    if lmatch is not None:
                        p.link = lmatch.groupdict()['link']


            if p.title is None:
                print("No title line for post '{}'. Skipping.".format(post_file))
                return None

            p.url = URL_FORMAT.format(pf['year'], pf['month'], pf['day'], pf['file'])

            return p

        except Exception as e:
            print("Can't get URL and title for post '{}'. Error: ".format(post_file, e.message))
            return None


def read_posts(post_files):
    results = []
    for post_file in post_files:
        p = Post.read(post_file)
        if p is not None:
            results.append(p)

    return results


def tweet_posts(posts, tapi):
    for post in posts:
        tweet = post.format_for_twitter()

        print("Tweet: ")
        print(tweet)

        if tapi is not None:
            print("Tweeting...")
            try:
                tapi.PostUpdate(tweet)
                print("Tweet successful.")
            except Exception as e:
                print("Error tweeting: {}".format(e))

        print("")


def main(git_repo_path, remote, branch, working_branch, max_tweets, skip_tweeting, consumer_secret, token_secret):
    msg = "Checking repository '{}' for new posts. Will tweet a maximum of {} posts.".format(git_repo_path, max_tweets)
    print(msg)

    tapi = None
    if skip_tweeting:
        print("Will not actually tweet.")
    else:
        tapi = twitter.Api(consumer_key=API_CONSUMER_KEY,
                           consumer_secret=consumer_secret,
                           access_token_key=ACCESS_TOKEN_KEY,
                           access_token_secret=token_secret)

    post_files = get_new_posts(git_repo_path, remote, branch, working_branch)
    try:
        if len(post_files) > max_tweets:
            print("Too many new posts ({}), will only tweet {}.".format(len(posts), max_tweets))
            posts = post_files[-max_tweets:]


        posts = read_posts(post_files)
        tweet_posts(posts, tapi)
    finally:
        try:
            revert_git(git_repo_path, branch)
        except:
            pass

    return 0


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Checks a repository for new posts and creates a tweet for each new post. Only run on a local repository with a clean working directory.')
    parser.add_argument('-g','--git-repo', type=str, help='The git repo to check.', default=DEFAULT_GIT_REPO)
    parser.add_argument('-r','--remote', type=str, help='The remote to fetch.', default=DEFAULT_REMOTE_TO_CHECK)
    parser.add_argument('-b','--branch', type=str, help='The branch on the remote to check for posts.', default=DEFAULT_BRANCH_TO_CHECK)
    parser.add_argument('-w','--working-branch', type=str, help='The branch to do our work on.', default=DEFAULT_WORKING_BRANCH)
    parser.add_argument('-m','--max-tweets', type=int, help='Sets a limit on the number of posts to tweet.', default=2)
    parser.add_argument('-s','--skip-tweeting', action='store_true', help='Prepare the tweets, but don\'t send them.', default=False)
    parser.add_argument('-c','--consumer-secret', type=str, help='The secret for the consumer\s Twitter API key.', default='')
    parser.add_argument('-t','--token-secret', type=str, help='The secret for the Twitter access token key.', default='')
    args = parser.parse_args()

    sys.exit(main(args.git_repo, args.remote, args.branch, args.working_branch, args.max_tweets,
                  args.skip_tweeting, args.consumer_secret, args.token_secret))


