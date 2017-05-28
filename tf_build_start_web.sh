#!/bin/bash

# cd /norep/Downloads/tensorflow-objects
# cd ~/Downloads/tensorflow-objects

CACHEDIR=$1
if [[ x$CACHEDIR == x ]]; then {
   CACHEDIR=~/.tf_objects_cache
} fi
if [[ ! -d $CACHEDIR ]]; then {
    echo Usage: $0 [path to tensorflow-objects dir]
    exit 0
} fi

cd $CACHEDIR
/usr/local/bin/python -m SimpleHTTPServer 8000
