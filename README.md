# Reddytt

A silly little python script to play and save subreddit youtube-links from the command line (with mpv).

## Dependencies

Python modules: pickle, bs4, urllib3, certifi; Player: mpv

## Usage

Run by
```
$ python3 reddytt.py [subredditname] [depth]
```
note that `[subredditname]` is just the name, e.g. `deepintoyoutube` not `r/deepintoyoutube` or anything else. The integer `[depth]` measures how many pages into the subreddit you wish to go.

It saves seen videos to `~/.reddytt/[subreddit]/seen` and a list of unseen videos to `~/.reddytt/[subreddit]/unseen` (using pickle).

## Notes

It has only been tried with

* "deepintoyoutube" subreddit
* linux (gentoo)
* python3

it has not been tried with

* a non-existent subreddit
* any malicious input

No warranty that anything will work, or that it won't destroy your system.
