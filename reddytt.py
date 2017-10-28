
import os
import pickle

from bs4 import BeautifulSoup
import urllib3
import certifi
import re

import sys

# Find what subreddit you want to watch:
if len(sys.argv) == 1:
    print("No subbreddit entered as argument.")
    subreddit = input("Enter subreddit name: ")
elif len(sys.argv) == 2:
    subreddit = sys.argv[1]
else:
    #TODO: the next argument should be how many pages of the subreddit one should browse.
    subreddit = sys.argv[1]

subreddit_link = "https://reddit.com/r/" + subreddit

# Setup working directory
work_dir = os.environ['HOME'] + "/.reddytt"
sr_dir = work_dir + "/%s" % subreddit
seen_file = sr_dir + "/seen"
seen_links = []
unseen_file = sr_dir + "/unseen"
unseen_links = []
print("Checking for reddytt working directory (%s)." % work_dir)
if not os.path.isdir(work_dir):
    print("Working directory not found. Creating %s, and files." % work_dir)
    os.mkdir(work_dir)
    os.mkdir(sr_dir)
    os.system("touch %s" % seen_file)
    f = open(seen_file, 'wb')
    pickle.dump(seen_links, f)
    f.close()
    os.system("touch %s" % unseen_file)
    f = open(unseen_file, 'wb')
    pickle.dump(unseen_links, f)
    f.close()
elif not os.path.isdir(sr_dir):
    print("Working directory found, but no subreddit directoy. Creating %s, and files." % sr_dir)
    os.mkdir(sr_dir)
    os.system("touch %s" % seen_file)
    f = open(seen_file, 'wb')
    pickle.dump(seen_links, f)
    f.close()
    os.system("touch %s" % unseen_file)
    f = open(unseen_file, 'wb')
    pickle.dump(unseen_links, f)
    f.close()
else:
    print("Working directory found. Loading variables.")
    f = open(seen_file, 'rb')
    seen_links = pickle.load(f)
    f.close()
    f = open(unseen_file, 'rb')
    unseen_links = pickle.load(f)
    f.close()

# Get and parse out the links
pm = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',ca_certs=certifi.where())
html_page = pm.request('GET', subreddit_link)
soup = BeautifulSoup(html_page.data, "lxml")
links = []
for link in soup.find_all('a'):
    links.append(str(link.get('href')))
new_links = list(sorted(set(filter(re.compile("^https://youtu.be").match, links))))
new_links += list(sorted(set(filter(re.compile("^https://www.youtube.com").match, links))))
# we also want to watch the stored ones
new_links += unseen_links
new_links = list(sorted(set(new_links)))

# Start watching
save_links = new_links
for link in new_links:
    if link in seen_links:
        print("Link seen. Skipping.")
    else:
        x = os.system("mpv %s" % link)
        if x == 0:
            # The video finished or you hit 'q' (or whatever your binding is), this is a good exit.
            # Store the video in seen_links.
            seen_links.append(link)
            save_links.remove(link)
        elif x == 1024:
            # You made a hard exit, and want to stop. (Ctrl+C)
            # Store the links and exit the program.
            f = open(seen_file, 'wb')
            pickle.dump(seen_links, f)
            f.close()
            f = open(unseen_file, 'wb')
            pickle.dump(save_links, f)
            f.close()
            # Exit program.
            sys.exit()
        else:
            # Something else happened. Bad link perhaps.
            # Store in seen_links to avoid in the future.
            seen_links.append(link)
            save_links.remove(link)

# The playlist is finished. Save everything.
f = open(seen_file, 'wb')
pickle.dump(seen_links, f)
f.close()
f = open(unseen_file, 'wb')
pickle.dump(save_links, f)
f.close()
