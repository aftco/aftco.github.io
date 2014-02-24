#!/usr/bin/python
# coding=utf-8

import os
import cgi
import json

#
#    path to local git repo _posts dir
#    edit to match your local path
#
_posts_dir = '/home/mjtrumbe/aftco.github.io/_posts'

def main():

    #
    #    parse cgi get request
    #
    link = cgi.FieldStorage()

    #
    #    write lines to file
    #
    with open(os.path.join(_posts_dir, link.getvalue('filename')), 'a') as new_post:
        new_post.write('---\n')
        new_post.write('layout: %s\n' % link.getvalue('layout'))
        new_post.write('title: %s\n' % link.getvalue('title'))
        new_post.write('tags: %s\n' % link.getvalue('tags'))
        new_post.write('link: %s\n' % link.getvalue('link'))
        new_post.write('---\n\n')
        new_post.write(link.getvalue('body'))

    #
    #    git pull, add, commit and push new post
    #
    os.system('cd %s && git pull && git add -A && git commit -m "Creating new post %s via webform" && git push' % (_posts_dir, link.getvalue('filename')))

    #
    #    write content header and return json
    #
    print "Content-type: application/json"
    print 
    response={ 'success':True, 'message':"New post '%s' has been created and checked in!" % link.getvalue('filename') }
    print(json.JSONEncoder().encode(response))

if __name__ == "__main__":
    main()
