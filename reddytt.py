#!/usr/bin/env python3

################################################################################
            ######  ####### ######  ######  #     # ####### #######
            #     # #       #     # #     #  #   #     #       #
            #     # #       #     # #     #   # #      #       #
   #####    ######  #####   #     # #     #    #       #       #       #####
            #   #   #       #     # #     #    #       #       #
            #    #  #       #     # #     #    #       #       #
            #     # ####### ######  ######     #       #       #
################################################################################
#
#   reddytt.py
#   https://github.com/johanbluecreek/reddytt
#
__version__ = "1.4.8"
user_agent = "Reddytt v{}".format(__version__)
#
################################################################################
################################################################################

################################################################################
              ### #     # ######  ####### ######  #######  #####
               #  ##   ## #     # #     # #     #    #    #     #
               #  # # # # #     # #     # #     #    #    #
               #  #  #  # ######  #     # ######     #     #####
               #  #     # #       #     # #   #      #          #
               #  #     # #       #     # #    #     #    #     #
              ### #     # #       ####### #     #    #     #####
################################################################################

import os
import pickle
import requests
import json
import re
import subprocess
import sys
import argparse as ap
import copy
from datetime import date
import time
import random
from shutil import copyfile

################################################################################
      ####### #     # #     #  #####  ####### ### ####### #     #  #####
      #       #     # ##    # #     #    #     #  #     # ##    # #     #
      #       #     # # #   # #          #     #  #     # # #   # #
      #####   #     # #  #  # #          #     #  #     # #  #  #  #####
      #       #     # #   # # #          #     #  #     # #   # #       #
      #       #     # #    ## #     #    #     #  #     # #    ## #     #
      #        #####  #     #  #####     #    ### ####### #     #  #####
################################################################################

 ####  #####  ######   ##   ##### ######         # #    # #####  #    # #####
#    # #    # #       #  #    #   #              # ##   # #    # #    #   #
#      #    # #####  #    #   #   #####          # # #  # #    # #    #   #
#      #####  #      ######   #   #              # #  # # #####  #    #   #
#    # #   #  #      #    #   #   #              # #   ## #      #    #   #
 ####  #    # ###### #    #   #   ######         # #    # #       ####    #
                                         #######

def create_input(work_dir):
    """
        create_input(work_dir)

    Create `mpv` `input.conf`-file to overide default settings.
    """
    # Create path to file
    input_file = work_dir + "/input.conf"
    # Make a backup if relevant
    if os.path.isfile(input_file):
        backup_file = input_file + "-" + date.today().isoformat() + "-" + str(int(time.time()))
        print("Reddytt: Creating backup of old `input.conf`: %s" % backup_file)
        copyfile(input_file, backup_file)

    with open(input_file, 'w') as f:
        f.write('> quit 0\n')
        f.write('q quit 4\n')
        f.write('R run "/bin/bash" "-c" "echo \\\"${title}: ${path}\\\" >> ~/.reddytt/remember"\n')
        f.write('i show-text "${title}"\n')
        f.write('Ctrl+o run "/bin/bash" "-c" "xdg-open \\\"${path}\\\""\n')


##### #    # #####          # #    # #####  #    # #####
  #   ##  ## #    #         # ##   # #    # #    #   #
  #   # ## # #    #         # # #  # #    # #    #   #
  #   #    # #####          # #  # # #####  #    #   #
  #   #    # #              # #   ## #      #    #   #
  #   #    # #              # #    # #       ####    #
                    #######

def tmp_input(work_dir, link, num):
    """
        tmp_input(work_dir, link, num)

    Generates temporary `input.conf` from the base one.
    """
    # Create paths to files
    input_file = work_dir + "/input.conf"
    tmp_file = work_dir + "/input.conf_tmp"

    # Copy the base
    copyfile(input_file, tmp_file)

    # Add the extra mappings
    # Map 'Ctrl+r' to open Reddit-link in browser
    crtlr_string = ""
    try:
        crtlr_string = 'Ctrl+r run "/bin/bash" "-c" "xdg-open \\\"{}{}\\\""\n'.format("https://www.reddit.com", link[2])
    except IndexError:
        print("Reddytt: Old link encountered.")
        crtlr_string = 'Ctrl+r show-text "Reddytt: Reddit link not available."\n'

    # Map 'n' to show links-left number
    n_string = 'n show-text "{}"\n'.format(str(num))

    with open(tmp_file, 'a') as f:
        f.write(crtlr_string)
        f.write(n_string)

 ####  #      ######   ##   #    #         #   # #####
#    # #      #       #  #  ##   #          # #    #
#      #      #####  #    # # #  #           #     #
#      #      #      ###### #  # #           #     #
#    # #      #      #    # #   ##           #     #
 ####  ###### ###### #    # #    #           #     #
                                   #######

def clean_yt(link_list):
    """
        clean_yt(link_list)

    Cleans up all youtube-links.
    """
    # List to return
    new_list = []
    for link in link_list:
        # Only handle youtube links here
        if re.match("^https://www\.youtube\.com/watch", link[0]):
            # Find the label
            videolabel = re.search('v=([^&?]*)', link[0]).group(1)
            # If there for some strange reason would not be one
            if videolabel is None:
                print('Reddytt: skipping URL without video label:', link)
                continue
            # Add the cleaned up link
            try:
                new_list.append(('https://www.youtube.com/watch?v=' + videolabel, link[1], link[2]))
            except IndexError:
                new_list.append(('https://www.youtube.com/watch?v=' + videolabel, link[1]))
        else:
            # Or just add the original link if not youtube
            new_list.append(link)

    return new_list


#####  ######  ####  #      # #    # #    #  ####
#    # #      #    # #      # ##   # #   #  #
#    # #####  #    # #      # # #  # ####    ####
#####  #      #  # # #      # #  # # #  #        #
#   #  #      #   #  #      # #   ## #   #  #    #
#    # ######  ### # ###### # #    # #    #  ####

def reqlinks(link):
    """
        reqlinks(link)

    Request and parse out Reddytt-supported links at `link`.
    """
    # Generate a seed for the user agent and send request
    ua = user_agent + " " + str(random.randint(100,999))
    req = requests.get(link, headers={'User-Agent': ua})
    data = req.json()

    # Handle errors reddit might give us
    if 'error' in data.keys():
        print("Reddytt: Was presened with the Reddit error: " + str(data['error']) + " -- " + data['message'])
        print("Reddytt: Depending on the error, wait a while, or file an issue with Reddytt.")

    # Collect video urls and titles
    links = [ (child['data']['url'], child['data']['title'], child['data']['permalink']) for child in data['data']['children']]

    # Clean up links
    links = clean_yt(links)

    # Find the 'after' variable
    after = data['data']['after']

    return links, after

################################################################################
                          #     #    #    ### #     #
                          ##   ##   # #    #  ##    #
                          # # # #  #   #   #  # #   #
                          #  #  # #     #  #  #  #  #
                          #     # #######  #  #   # #
                          #     # #     #  #  #    ##
                          #     # #     # ### #     #
################################################################################

if __name__ == '__main__':

            #
            #      ##   #####   ####  #    # #    # ###### #    # #####  ####
            #     #  #  #    # #    # #    # ##  ## #      ##   #   #   #
                 #    # #    # #      #    # # ## # #####  # #  #   #    ####
            #    ###### #####  #  ### #    # #    # #      #  # #   #        #
            #    #    # #   #  #    # #    # #    # #      #   ##   #   #    #
            #    #    # #    #  ####   ####  #    # ###### #    #   #    ####

    ### Resolve arguments ###

    parser = ap.ArgumentParser(usage='%(prog)s [options] <subreddit> [-- [mpv]]', description='Play the video links from your favourite subreddit.')

    # Optional arguemnts
    parser.add_argument('--depth', metavar='d', type=int, default=0, help='How many pages into the subreddit you want to go. (`0` is frontpage, each positive number another page after that. Negative will not fetch new links at all.)')
    parser.add_argument('--gen-input', action='store_true', help='Trigger reddytt to generate reddytt\'s default `input.conf`, and backup the old one. (It is good to run this if you have updated reddytt.)')
    parser.add_argument('--version', action='version', version='%(prog)s {}'.format(__version__), help="Prints version number and exits.")

    # Positional arguments
    parser.add_argument('subreddit', type=str, help='The subreddit you want to play.', nargs='?')
    parser.add_argument('mpv', nargs=ap.REMAINDER, help='Arguments to pass to `mpv`.')

    args = parser.parse_args()

    subreddit = args.subreddit

    depth = args.depth
    gen_input = args.gen_input

    if subreddit == None and not gen_input:
        print("Reddytt: No subreddit given, exiting. Try `reddytt --help`.")
        sys.exit()

    if not subreddit == None:
        if "?" in subreddit:
            print("Reddytt: Are you trying to manipulate the Reddit-api call? Stop that!")
            sys.exit()



            #                                       ##
            #    ###### # #      ######  ####      #  #      #####  # #####
            #    #      # #      #      #           ##       #    # # #    #
                 #####  # #      #####   ####      ###       #    # # #    #
            #    #      # #      #           #    #   # #    #    # # #####
            #    #      # #      #      #    #    #    #     #    # # #   #
            #    #      # ###### ######  ####      ###  #    #####  # #    #

    ### Check on directories and files ###

    # Setup working directory
    work_dir = os.environ['HOME'] + "/.reddytt"
    if not os.path.isdir(work_dir):
        os.mkdir(work_dir)

    # New optional flag triggers input.conf generation, or if the file does not exists.
    if gen_input:
        print("Reddytt: Generating 'input.conf' file and exiting.")
        if not os.path.isdir(work_dir):
            os.mkdir(work_dir)
        create_input(work_dir)
        sys.exit()
    elif not os.path.isfile(work_dir + "/input.conf"):
        print("Reddytt: No input-file found, creating 'input.conf' file.")
        create_input(work_dir)

    subreddit_link = "https://reddit.com/r/" + subreddit + "/.json"

    sr_dir = work_dir + "/%s" % subreddit
    # File for seen videos
    seen_file = sr_dir + "/seen"
    seen_links = []
    # File for unseen videos
    unseen_file = sr_dir + "/unseen"
    unseen_links = []
    # File for overiding mpv input.conf
    input_file = work_dir + "/input.conf"
    tmp_input_file = work_dir + "/input.conf_tmp"
    # File for remembering links
    remember_file = work_dir + "/remember"

    if not os.path.isdir(work_dir):
        print("Reddytt: Working directory not found. Creating %s, and files." % work_dir)
        os.mkdir(work_dir)
        os.mkdir(sr_dir)
        os.system("touch %s" % seen_file)
        with open(seen_file, 'wb') as f:
            pickle.dump(seen_links, f)
        os.system("touch %s" % unseen_file)
        with open(unseen_file, 'wb') as f:
            pickle.dump(unseen_links, f)
    elif not os.path.isdir(sr_dir):
        print("Reddytt: Working directory found, but no subreddit directory. Creating %s, and files." % sr_dir)
        os.mkdir(sr_dir)
        os.system("touch %s" % seen_file)
        with open(seen_file, 'wb') as f:
            pickle.dump(seen_links, f)
        os.system("touch %s" % unseen_file)
        with open(unseen_file, 'wb') as f:
            pickle.dump(unseen_links, f)
    else:
        print("Reddytt: Working directory found. Loading variables.")
        try:
            with open(seen_file, 'rb') as f:
                seen_links = pickle.load(f)
        except FileNotFoundError:
            # This allows you to remove the file manually to reset.
            print("Reddytt: (Seen) File not found. Creating empty file.")
            os.system("touch %s" % seen_file)
        try:
            with open(unseen_file, 'rb') as f:
                unseen_links = pickle.load(f)
        except FileNotFoundError:
            # This allows you to remove the file manually to reset.
            print("Reddytt: (Unseen) File not found. Creating empty file.")
            os.system("touch %s" % unseen_file)
        # Resolve compatability issues with older versions:
        seen_links = [ (l, '') if not type(l) == tuple else l for l in seen_links]
        unseen_links = [ (l, '') if not type(l) == tuple else l for l in unseen_links]

            #
            #     ####  ###### #####    #      # #    # #    #  ####
            #    #    # #        #      #      # ##   # #   #  #
                 #      #####    #      #      # # #  # ####    ####
            #    #  ### #        #      #      # #  # # #  #        #
            #    #    # #        #      #      # #   ## #   #  #    #
            #     ####  ######   #      ###### # #    # #    #  ####

    ### Get links to play ###

    new_links = []

    if depth < 0:
        # Just a warning. Negative means not fetching new links.
        print("Reddytt: Depth set to negative. No new links will be fetched.")
    else:
        # Otherwise, proceed to get links.
        print("Reddytt: Fetching links.")
        new_links, after = reqlinks(subreddit_link)

    # Go deeper
    d = 0
    while depth > d and not after == None:
        link = subreddit_link + "?after={}".format(after)

        newer_links, after = reqlinks(link)
        d += 1

        new_links += newer_links
        new_links = list(set(new_links))

    # We also want to watch the stored ones
    watch_links = new_links + unseen_links
    # Remove repeted entries of links as well as the ones already seen
    watch_links = list(set(watch_links)-set(seen_links))

    print("Reddytt: Links to watch: %i" % len(watch_links))

            #
            #     ####  #####   ##   #####  #####
            #    #        #    #  #  #    #   #
                  ####    #   #    # #    #   #
            #         #   #   ###### #####    #
            #    #    #   #   #    # #   #    #
            #     ####    #   #    # #    #   #

    ### Start watching ###

    print("Reddytt: The watch begins.")
    print("")

    save_links = copy.copy(watch_links)
    for link in watch_links:

        # Verify integrety of `link` variable, this is to avoid bug that can appear using files generated from reddytt older than v1.2
        if not type(link) == tuple:
            link = (link, '')

        if link[0] in map(lambda x: x[0], seen_links):
            print("Reddytt: Link seen. Skipping.")
            # Link is seen, do not need to save.
            save_links.remove(link)
            print("Reddytt: Links left: %i" % len(save_links))
        else:
            tmp_input(work_dir, link, len(save_links))
            print("\nReddytt: Playing: %s\n" % link[1])
            p = subprocess.Popen(
                [
                    'mpv',
                    link[0],
                    '--input-conf=%s' % tmp_input_file,
                    '--title=%s' % link[1].replace('"',"'")
                ] + args.mpv
            , shell=False)
            p.communicate()
            os.system("rm {}".format(tmp_input_file))
            # Separate mpv and reddytt output
            print("")
            # Print the link (useful for saving manually if mpv messed up output)
            print("Reddytt: That was: %s" % link[1])
            print("Reddytt:           %s\n" % link[0])
            if p.returncode == 0:
                # The video finished or you hit '>' (default reddyt binding), this is a good exit.
                # Store the video in seen_links.
                seen_links.append(link)
                save_links.remove(link)
                # Print some stats
                print("Reddytt: Links left: %i" % len(save_links))
                # New line to separate next mpv output
                print("")
            elif p.returncode == 4:
                # You made a hard exit, and want to stop. ('q')
                # Store the links and exit the program.
                print("Reddytt: Forced exit detected. Saving and exiting.")
                with open(seen_file, 'wb') as f:
                    pickle.dump(seen_links, f)
                with open(unseen_file, 'wb') as f:
                    pickle.dump(save_links, f)
                # Exit program.
                sys.exit()
            else:
                # Something else happened. Bad link perhaps.
                print("Reddytt: mpv exited in an unexpected way. Exit code: ", p.returncode)
                # New line to separate next mpv output
                print("")
                # Store in seen_links to avoid in the future.
                seen_links.append(link)
                save_links.remove(link)

    print("Reddytt: All links consumed. Saving and exiting.")
    # The playlist is finished. Save everything.
    with open(seen_file, 'wb') as f:
        pickle.dump(seen_links, f)
    with open(unseen_file, 'wb') as f:
        pickle.dump(save_links, f)
