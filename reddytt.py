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
__version__ = "1.3.2"
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
from bs4 import BeautifulSoup
import urllib3
import certifi
import re
import subprocess
import sys
import argparse as ap
import copy
from datetime import date
import time
#from argparse import ArgumentParser, REMINDER

################################################################################
      ####### #     # #     #  #####  ####### ### ####### #     #  #####
      #       #     # ##    # #     #    #     #  #     # ##    # #     #
      #       #     # # #   # #          #     #  #     # # #   # #
      #####   #     # #  #  # #          #     #  #     # #  #  #  #####
      #       #     # #   # # #          #     #  #     # #   # #       #
      #       #     # #    ## #     #    #     #  #     # #    ## #     #
      #        #####  #     #  #####     #    ### ####### #     #  #####
################################################################################

# Function to flatten a list
flatten = lambda l: [item for sublist in l for item in sublist]
# cheers to https://stackoverflow.com/a/952952


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
        os.system("cp {} {}".format(input_file, backup_file))
    # Start creating the file
    os.system("echo \"\" > %s" % input_file)
    # Fill the file
    ## Exits
    # Remap '>' which is the default for next in playlist to trigger
    # exit code to play next
    os.system("echo \"> quit 0\" >> %s" % input_file)
    # Remap 'q' to give an exit code to end this program.
    os.system("echo \"q quit 4\" >> %s" % input_file)
    # Map 'R' ro save link to the remember file (${path} and not ${filename}
    # to get full URL)
    os.system("echo \"R run \\\"/bin/bash\\\" \\\"-c\\\" \\\"echo \\\\\\\"\${title}: \${path}\\\\\\\" >> ~/.reddytt/remember\\\" \" >> %s" % input_file)
    # uses bash and quotes around ${path} to sanitize possible injection
    # cheers to https://stackoverflow.com/a/4273137
    # Map 'i' to display title
    os.system("echo \"i show-text \\\"\${title}\\\"\" >> %s" % input_file)


 ####  ###### #####  ####   ####  #    # #####
#    # #        #   #      #    # #    # #    #
#      #####    #    ####  #    # #    # #    #
#  ### #        #        # #    # #    # #####
#    # #        #   #    # #    # #    # #
 ####  ######   #    ####   ####   ####  #


def getsoup(link, rec=False):
    """
        getsoup(link)

    Calls BeautifulSoup.
    """
    pm = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',ca_certs=certifi.where())
    html_page = pm.request('GET', link)
    soup = BeautifulSoup(html_page.data, "lxml")

    # The absense of 'after' is the sign for when Issue #8 will be triggered.
    has_after = not all([ not 'after=' in a.get('href') for a in soup('a') if a.get('href') ])
    if (not has_after) and (not rec):
        print('Reddytt: Fetching links did not go as planned. Will try some more times and then give up.')
        tries = 0
        while tries <= 3 and not has_after:
            soup = getsoup(link, True)
            has_after = not all([ not 'after=' in a.get('href') for a in soup('a') if a.get('href') ])
            tries +=1
        if not has_after:
            print('Reddytt: The problem was not resolved. This can mean that you are trying to access more depth than is available, or that reddit.com is refusing to cooperate.')
        else:
            print('Reddytt: The problem was resolved.')

    return soup

 ####  ###### ##### #      # #    # #    #  ####
#    # #        #   #      # ##   # #   #  #
#      #####    #   #      # # #  # ####    ####
#  ### #        #   #      # #  # # #  #        #
#    # #        #   #      # #   ## #   #  #    #
 ####  ######   #   ###### # #    # #    #  ####

def getlinks(link):
    """
        getlinks(link)

    Get and parse out Reddytt-supported links at `link`.
    """
    # Prepare the soup that is a reddit page
    soup = getsoup(link)

    # Pick out all links that has a text, and their text.
    lts = [
        (a.get('href'), a.get_text())
    for a in soup('a') if all([a.get('href'), not a.get_text() == ''])]

    # Collect all the supported links
    ybe_links = [x for x in lts if re.match("^https://youtu\.be", x[0])]
    yt_links = [x for x in lts if re.match("^https://www\.youtube\.com/watch", x[0])]
    tc_links = [x for x in lts if re.match("^https://clips\.twitch\.tv/", x[0])]
    # In principle, add anything here you want. I guess all of these should
    # work: https://rg3.github.io/youtube-dl/supportedsites.html

    # Reformat links where necessary
    yt_links_n = []
    for lk in yt_links:
        videolabel = re.search('v=([^&?]*)', lk[0]).group(1)
        if videolabel is None:
            print('Reddytt: skipping URL without video label:', lk)
            continue
        yt_links_n.append(('https://www.youtube.com/watch?v=' + videolabel, lk[1]))

    # Collect all links
    all_links = ybe_links + yt_links_n + tc_links

    return all_links, list(map(lambda x: x[0], lts))

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

    parser = ap.ArgumentParser(usage='%(prog)s [options] <subreddit> [-- [mpv-arguments]]', description='Play the youtube links/twitch clips from your favourite subreddit.')

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

    subreddit_link = "https://reddit.com/r/" + subreddit

    sr_dir = work_dir + "/%s" % subreddit
    # File for seen videos
    seen_file = sr_dir + "/seen"
    seen_links = []
    # File for unseen videos
    unseen_file = sr_dir + "/unseen"
    unseen_links = []
    # File for overiding mpv input.conf
    input_file = work_dir + "/input.conf"
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
        new_links, links = getlinks(subreddit_link)

    # Go deeper
    if depth > 0:
        for d in range(depth):
            link = ""
            for l in links:
                if re.search("after=", l):
                    link = l
            if link == "":
                print("Reddytt: Could not identify 'after'-variable to progress deeper.")
            else:
                newer_links, links = getlinks(link)
                new_links += newer_links
                new_links = list(set(new_links))

    # We also want to watch the stored ones
    new_links += unseen_links
    # Remove repeted entries of links as well as the ones already seen
    new_links = list(set(new_links)-set(seen_links))
    print("Reddytt: Links to watch: %i" % len(new_links))

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
    save_links = copy.copy(new_links)
    for link in new_links:

        # Verify integrety of `link` variable, this is to avoid bug that can appear using files generated from reddytt older than v1.2
        if not type(link) == tuple:
            link = (link, '')

        if link[0] in map(lambda x: x[0], seen_links):
            print("Reddytt: Link seen. Skipping.")
            # Link is seen, do not need to save.
            save_links.remove(link)
            print("Reddytt: Links left: %i" % len(save_links))
        else:
            print("\nReddytt: Playing: %s\n" % link[1])
            p = subprocess.Popen(
                [
                    'mpv',
                    link[0],
                    '--input-conf=%s' % input_file,
                    '--title=\"%s\"' % link[1]
                ] + args.mpv
            , shell=False)
            p.communicate()
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
