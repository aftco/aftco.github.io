from os import path
import sys


PROJECT_ROOT = path.normpath(path.join(path.dirname(path.realpath(__file__)), '..'))
DEFAULT_GIT_REPO = path.join(PROJECT_ROOT, '.git')

def main(git_repo_path, max_tweets):
    msg = "Checking repository '{}' for new posts. Will tweet a maximum of {} posts.".format(git_repo_path, max_tweets)
    print(msg)
    return 0


def get_args():
    import argparse
    parser = argparse.ArgumentParser(description='Checks a repository for new posts and creates a tweet for each new post.')
    parser.add_argument('-g','--git-repo', type=str, help='The git repo to check.', default=DEFAULT_GIT_REPO)
    parser.add_argument('-m','--max-tweets', type=int, help='Sets a limit on the number of posts to tweet.', default=2)
    args = parser.parse_args()

    return args.git_repo, args.max_tweets


if __name__ == "__main__":
    git_repo, max_tweets = get_args()
    sys.exit(main(git_repo, max_tweets))


