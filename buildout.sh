#!/bin/sh

if [ "$1" = "-c" ]
then
    shift
    rm -rf bin
    rm -rf develop-eggs
    rm -rf eggs
    rm -rf parts
    rm -f .installed.cfg
fi

python buildout/bootstrap.py -c buildout/buildout.cfg
bin/buildout -c "buildout/buildout.cfg"

