#!/usr/bin/python
# coding=utf-8

import os
import cgi
import json
import commands

#
#    path to local git repo _posts dir
#    edit to match your local path
#
_posts_dir = '/home/mjtrumbe/aftco.github.io/_posts'


#
#    write content header and return json
#
def return_response(response):
    print "Content-type: application/json"
    print 
    print(json.JSONEncoder().encode(response))


#
#    validate form and return results
#
def validate_form():
    form = { 'is_valid': True, 'message': '', 'fields': {} }

    #
    #    parse cgi get request
    #
    link = cgi.FieldStorage()

    for i in ['filename', 'layout', 'title', 'tags', 'link', 'body']:
        item = link.getvalue(i)
        if item == None or item == '':
            form['is_valid'] = False
            form['message'] = '%s required' % i
            return form
        else:
            form['fields'][i] = item

    #
    #    add .md file ending to filename
    #
    filename = link.getvalue('filename')
    if filename[-3:] != '.md':
        filename = filename + '.md'  
    form['fields']['filename'] = filename

    return form


def main(form):

    #
    #    write lines to file
    #
    with open(os.path.join(_posts_dir, form['fields']['filename']), 'a') as new_post:
        new_post.write('---\n')
        new_post.write('layout: %s\n' % form['fields']['layout'])
        new_post.write('title: "%s"\n' % form['fields']['title'])
        new_post.write('tags: %s\n' % form['fields']['tags'])
        new_post.write('link: %s\n' % form['fields']['link'])
        new_post.write('---\n\n')
          
        for line in form['fields']['body'].split('\\n'):
            new_post.write('%s\n' % line)

    #
    #    git pull, add, commit and push new post
    #
    commands.getoutput('cd %s && git pull && git add -A && git commit -m "Creating new post %s via webform" && git push' % (_posts_dir, form['fields']['filename']))

    form['message'] = 'Post created!'

    return_response(form)


if __name__ == "__main__":
    form = validate_form()
    if form['is_valid']:
        main(form)
    else:
        return_response(form)     



