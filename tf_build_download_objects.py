#!/usr/bin/env python3
import requests
import subprocess
import os
import sys
import argparse
from os import path
from os.path import join


FILES_TO_SKIP = [
    'gmock_archive',
    'linenoise',
    'jsoncpp_git',
    'boringssl'
]

def from_internet(tf_file, out_dir):
    """
    use to download from the connected internet
    """
    with open(tf_file, 'r') as f:
        contents = f.read()
    for line in contents.split('\n'):
        if line.strip().startswith('url'):
            if 'eigen' in line:
                continue
            url = line.split('"')[1]
            subpath = '/'.join(url.split('/')[3:])
            subdirname = '/'.join(url.split('/')[3:-1])
            print('url', url, 'subdirname', subdirname)
            target_dir = join(out_dir, subdirname)
            target_file = join(out_dir, subpath)
            if not path.isdir(target_dir):
                print('creating %s' % target_dir)
                os.makedirs(target_dir)
            if not path.isfile(target_file):
                print(subprocess.check_output([
                    'wget', url
                ], cwd=target_dir).decode('utf-8'))


def from_local(tf_file, out_dir, binaries_dir):
    """
    Use if you're on a plane and found your bazel needed fixing, and you dont have internet...

    binaries_dir should be a folder with the already-downloaded tars
    """
    with open(tf_file, 'r') as f:
        contents = f.read()
    name = None
    for line in contents.split('\n'):
        if line.strip().startswith('name'):
            name = line.strip().split('"')[1]
        if line.strip().startswith('url'):
            if 'eigen' in line:
                continue
            url = line.split('"')[1]
            subpath = '/'.join(url.split('/')[3:])
            subdirname = '/'.join(url.split('/')[3:-1])
            print('url', url, 'subdirname', subdirname)
            target_dir = join(out_dir, subdirname)
            target_file = join(out_dir, subpath)
            if not path.isdir(target_dir):
                print('creating %s' % target_dir)
                os.makedirs(target_dir)
            if not path.isfile(target_file):
                assert name is not None
                print('name', name)
                if name in FILES_TO_SKIP:
                    print('skipping %s' % name)
                    continue
                filename = target_file.split('/')[-1]
                print('copying:', target_file, name, filename)
                sourcedirpath = join(binaries_dir, name)
                if not path.isfile(join(sourcedirpath, filename)):
                    sourcedirpath += '/FILE'
                print(subprocess.check_output([
                    'cp', join(sourcedirpath, filename), target_file]).decode('utf-8'))
            name = None


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--tensorflow-dir', type=str, default='.', help='path to the cloned tensorflow repository')
    parser.add_argument('--cache-dir', type=str, default='~/.tf_objects_cache', help='local path for tensorflow cache')
    args = parser.parse_args()

    if not path.isdir(join(args.tensorflow_dir, 'tensorflow')):
        print('The directory [%s] does not appear to be a cloned tensorflow repository?' % args.tensorflow_dir)
        sys.exit(0)

    if not path.isdir(join(args.tensorflow_dir, 'bazel-out')):
        print('You need to have run ./configure, to download the dependencies, prior to running this script')
        sys.exit(0)

    # from_internet(tf_file='tensorflow/workspace.bzl', out_dir='/norep/Downloads/tensorflow-objects')
    args.cache_dir = args.cache_dir.replace('~', os.environ['HOME'])
    from_local(
        tf_file=join(args.tensorflow_dir, 'WORKSPACE'), out_dir=args.cache_dir,
        binaries_dir=join(args.tensorflow_dir, 'bazel-out/../external'))
    from_local(
        tf_file=join(args.tensorflow_dir, 'tensorflow/workspace.bzl'), out_dir=args.cache_dir,
        binaries_dir=join(args.tensorflow_dir, 'bazel-out/../external'))
