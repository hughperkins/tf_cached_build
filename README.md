# tf_cached_build

Cache tensorflow build dependencies, to accelerate repeated tf configures, or run on a plane

## Background

By default, when you run `./configure`, it will download the dependencies, from `.tar.gz` files, scattered around the internet.  This takes time, and chews up ones 4G
bandwidth and/or is slow.

This document provides information on creating a local cache, using the python SimpleHTTPServer, to serve these files from your local cmoputer, and point bazel
at them. Thus, Bazel no longer needs to systematically download the dependencies from the internet.

## Security implications

These instructions are highly untested.  Please make sure to take the time to understand what they do, and why. Note that
you will be creating a webserver on your computer, running on port 8000. Please make sure to understand the implications of this, for the security of your computer,
and the data on it.  You should enable a firewall and appropriate configuration/rule setup, to avoid publishing port 8000 to your local network.

These tips are provided under the [Apache 2.0 license](https://www.apache.org/licenses/LICENSE-2.0.html).  Please ensure that you take the time to understand:
- what these do
- how they work
- what implications they might have for the security and privacy of your computer
- what implications they might have for any files you have on your computer

## Concept

- cache the files locally
- run a python `SimpleHTTPServer` to serve them
- point bazel at them

## Procedure

### Setup a firewall

Ensure you enable a firewall on your computer, to block connections from your local network, to port 8000 of your computer.  How to do this is outside the scope of this document.  It is very important to do this.  Not enabling a firewall prior to running this procedure means that other people and computers might be able to access files on your computer, to read them, to modify them, and to use them as a means to obtain additional access to your computer.  If you are not sure how to enable a Firewall on your computer, and to configure it appropriately, then
please either stop using this document, or seek the advice of an expert in computer security to look into this for you.

### Cache files locally

- clone this repo, `git clone https://github.com/hughperkins/tf_cached_build`
- if you havent already done so, clone tensorflow(-cl), and run an initial `./configure`, to download the dependencies
- Use `python3` to run `tf_build_download_objects.py` script
  - Either downlaod into the default ~/.tf_objects_cache` directory, or use option `--cache-dir` to specify a directory of your choice
    - this directory should only be used for caching these objects, not for anything else
    - be aware that the contents of this directory will be freely browseable and downloadable, by anyone with access to port 8000 of your computer
  - Either run this script from the cloned tensorflow directory, or use `--tensorflow-dir` to specify the path of the tensorflow directory

IMPORTANT: the `out_dir` should not contain any files you dont want to make available to the network around you.  You should enable a firewall, on your computer,
to prevent other computers from connecting on this port, ie port 8000.  Failure to setup a firewall on your computer, to block access to this port, means that other people or
computers around you might be able to access sensitive information on your computer.  Failure to choose an `out_dir` that doesnt contain files you are not willing to share
might lead to said files being accessed by other people or computers.

Note that you'll have to have run a full standard `./configure` first, before running this script.  When you run this script after the configure, it will
copy the files that `bazel` downloaded, into the `out_dir` folder, ready for us to serve using `SimpleHTTPServer`

### Serve the files using SimpleHTTPServer

- run the script `tf_build_start_web.sh`
- if you used a non-default directory to store your cache, then pass it as the first argument, eg:
```
./tf_build_start_web.sh ~/my/tf/objects/cache
```

CAUTION: this will start and actual web server, on port 8000, and share all files in the directory you specify to anyone with access to your port 8000!

### Point Bazel at the local cache server

This will involve some search and replace. I dont have a script for this, for now. You'll need to do it by hand.  Open the `WORKSPACE` file, and:
- replace `https://github.com` with `http://localhost:8000`
- ditto for `https://raw.githubusercontent.com` => `http://localhost:8000`

Now do the same for `tensorflow/workspace.bzl` file. Note that you'll have to replace also:
- `http://zlib.net` => `http://localhost:8000`
- `http://pkgs.fedoraproject.org`
- `http://pypi.python.org`
- `http://www.ijg.org`
- `http://bitbucket.org`

Lastly, for linenoise, you have two options:
- leave as it is (its not big)
- but, if you're on a plane, leaving it where it is, ie on the internet, isnt really an option so:

To fix linenoise:
- update the linenoise section from being a `new_git_repository` to using a `new_http_archive`:
```
  native.new_http_archive(
    name = "linenoise",
    url = "http://localhost:8000/linenoise.tar.gz",
    sha256 = "ef341226c14219e747feea199ec152ae53084325c7319e0cf0ea841dd5ba77aa",
    build_file = str(Label("//:linenoise.BUILD")),
  )
```
- create this tar file, in your cache folder. I dont remember exactly how I created it :-P. So, this bit will need a bit of hacking. Or just leave linenoise to come down from the
internet for now is ok too.
