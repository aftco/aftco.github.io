#!/usr/bin/python

import argparse
import datetime
import os
from os import path
import re

PROJECT_ROOT = path.normpath(path.join(path.dirname(path.realpath(__file__)), '..'))


POST_DEFAULT_DIRECTORY = path.join(PROJECT_ROOT, "_posts")
POST_FILENAME_DATE_FORMAT = "%Y-%m-%d-%H-%M"
POST_FILENAME_FORMAT = "{post_datetime}-{post_filename}.md"
REGEX_FIND_PATTERN = """[ -"',:.?]+"""

POST_BODY_FORMAT="""---
layout: post
title: "{title}"
tags: 
link: {link}
---

"""


def get_title_filename(title):
    t = title.lower()
    t = re.sub(REGEX_FIND_PATTERN, '-', t)
    return t.strip('-')


def get_post_datetime(offset):
#    return datetime.datetime.now().strftime(POST_FILENAME_DATE_FORMAT)
    td_offset = datetime.timedelta(seconds=(offset * 60 * 60))
    dt = datetime.datetime.now() + td_offset
    return dt.strftime(POST_FILENAME_DATE_FORMAT)


def get_post_filename(data):
    filename = POST_FILENAME_FORMAT.format(**data)
    return os.path.join(POST_DEFAULT_DIRECTORY, filename)


def get_post_body(data):
    return POST_BODY_FORMAT.format(**data)


def write_file(data):
    print "%s - open:  %s" % (datetime.datetime.now(), data["post_filename"])
    fh = open(data["post_filename"], "w")
    print "%s - write:" % datetime.datetime.now()
    print data["post_body"]
    fh.write(data["post_body"])
    print "%s - close:  %s" % (datetime.datetime.now(), data["post_filename"])
    fh.close()


def main(args):
    data = {
        "title": args.title,
        "link": args.link,
        "post_filename": get_title_filename(args.title),
        "post_datetime": get_post_datetime(args.offset),
    }
    data["post_filename"] = get_post_filename(data)
    data["post_body"] = get_post_body(data)
#    print data
    write_file(data)


def parse_arguments():
    description = "create a new, preformatted Jekyll post"
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", dest="title", required=True,
        help="title of the Jekyll post")
    parser.add_argument("--link", dest="link", default='',
        help="url link for the Jekyll linked-list post [default: '']")
    parser.add_argument("--offset", dest="offset", default=0, type=int,
        help="hours to offset the timestamp [default: 0]")
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    main(args)
