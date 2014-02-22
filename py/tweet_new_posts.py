from os import path, listdir
import re
import sys
from git import Repo
import twitter


PROJECT_ROOT = path.normpath(path.join(path.dirname(path.realpath(__file__)), '..'))
DEFAULT_GIT_REPO = path.join(PROJECT_ROOT)
DEFAULT_WORKING_BRANCH = "auto/post_tweeter"
DEFAULT_REMOTE_TO_CHECK = "origin"
DEFAULT_BRANCH_TO_CHECK = "master"

FILE_PARSE_REGEX = re.compile("^.*/(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})-(?P<file>.+)\.\w{2,4}$",re.IGNORECASE)
TITLE_REGEX = re.compile("^title\:\s\"?(?P<title>.+?)\"?$", re.IGNORECASE)
URL_FORMAT="http://2handnews.com/{}/{}/{}/{}.html"


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


def get_url_title_tuples(posts):
    results = []
    for post in posts:
        try:
            fmatch = FILE_PARSE_REGEX.match(post)
            if fmatch is None:
                print("Unexpected file name for post '{}'. Skipping.".format(post))
                continue

            pf = fmatch.groupdict()

            url = URL_FORMAT.format(pf['year'], pf['month'], pf['day'], pf['file'])
            title = None
            with open(post, 'r') as f:
                for l in f:
                    tmatch = TITLE_REGEX.match(l)
                    if tmatch is not None:
                        title = tmatch.groupdict()['title']
                        break

            if title is None:
                print("No title line for post '{}'. Skipping.".format(post))
                continue

            results.append((url, title))

        except Exception as e:
            print("Can't get URL and title for post '{}'. Error: ".format(post, e.message))

    return results


def tweet_posts(url_title_pairs, tapi):
    for url, title in url_title_pairs:
        if len(title) > 117:
            title = title[:114] + "..."

        tweet = title + " " + url

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
        tapi = twitter.Api(consumer_key='TGkY2yQ249sPGtamuNjLUg',
                           consumer_secret=consumer_secret,
                           access_token_key='2326396458-eO0zImMateqrGnkGhF46mglyL77preju5HaOQVC',
                           access_token_secret=token_secret)

    posts = get_new_posts(git_repo_path, remote, branch, working_branch)
    try:
        if len(posts) > max_tweets:
            print("Too many new posts ({}), will only tweet {}.".format(len(posts), max_tweets))
            posts = posts[-max_tweets:]

        url_title_tuples = get_url_title_tuples(posts)
        tweet_posts(url_title_tuples, tapi)
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


