# Reddytt

Do you also find yourself not being able to waste time on [reddit](https://www.reddit.com) efficiently enough? With this silly little script you can get rid off that unnecessary time spent on reading titles thinking "is this really the video I want to watch?", clicking on links, clicking your way to the next page, etcetera, etcetera. `reddytt.py` will take care of that for you. It will start showing you videos taken from your favourite subreddit, just the first page or deeper if you want, until all links are consumed and you are faced with reality once again.

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
note that `<subreddit>` is just the name, e.g. `deepintoyoutube` not `r/deepintoyoutube` or anything else. The option available to you is `--depth d` which takes you `d` steps beyond the first page of the subreddit. Note that a negative depth means only already downloaded links will be played. All arguments following those are given to `mpv`.

Example,
```
$ ./reddytt.py --depth 2 deepintoyoutube -- --fs
```

### Key-mapping

Reddytt will generate a `input.conf`-file (to be stored in `~/.reddytt/`) and override the mpv default, or user-set, key mapping (that is, reddytt runs mpv with `--input-conf=` set). Nothing will permanently change for you, but you should be aware of the default key-mapping of reddytt:

 * `q`: Quits and saves remaining links (old `Ctrl+C` behaviour)
 * `>`: Plays next video (old `q` behaviour)
 * `R`: Saves (or **R**emembers) video link in `~/.reddytt/remember`
 * `i`: Prints the Reddit-given title of the video in mpv.

To override, edit `~/.reddytt/input.conf` at your own leisure.

On quit, it saves seen videos to `~/.reddytt/[subreddit]/seen` and a list of unseen videos to `~/.reddytt/[subreddit]/unseen` (using pickle).

## Supported sites

The following domains are supported by `reddytt.py`

 * `youtu.be`
 * `youtube.com/watch`
 * `clips.twitch.tv`
