# Reddytt

Do you also find yourself not being able to waste time on reddit efficiently enough? With this silly little script you can get rid off that unnecessary time spent on reading titles thinking "is this really the video I want to watch?", clicking on links, clicking your way to the next page, etcetera, etcetera. `reddytt.py` will take care of that for you. It will start showing you videos taken from your favourite subreddit, just the first page or deeper if you want, until all links are consumed and you are faced with reality once again.

## Dependencies

Python modules: pickle, bs4, urllib3, certifi, argparse, lxml; Player: mpv

These dependencies can be installed using the command `pip install -r requirements.txt`, or possibly your system package manager.

## Usage

Short version, take a look at
```
$ ./reddytt.py -h
```

The long version,
```
$ ./reddytt.py [options] <subreddit> [-- [mpv-arguments]]
```
note that `<subreddit>` is just the name, e.g. `deepintoyoutube` not `r/deepintoyoutube` or anything else. The option available to you is `--depth d` which takes you `d` steps beyond the first page of the subreddit. All arguments following those are given to `mpv`.

To stop a video and proceed to the next, press `q` of whatever your binding for stop is in mpv, and press `Ctrl+C` while a video is playing to stop the video, save the remaining links for the next time, and exit the script.

Example,
```
$ ./reddytt.py --depth 2 deepintoyoutube -- --fs
```

It saves seen videos to `~/.reddytt/[subreddit]/seen` and a list of unseen videos to `~/.reddytt/[subreddit]/unseen` (using pickle).

## Supported sites

The following domains are supported by `reddytt.py`

 * `youtu.be`
 * `youtube.com/watch`
 * `clips.twitch.tv`

## Notes

This has not been tested with any malicious input. No warranty that anything will work, or that it won't destroy your system.
