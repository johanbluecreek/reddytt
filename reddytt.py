
import os

from bs4 import BeautifulSoup
import urllib3
import certifi
import re

# Setup working directory
work_dir = os.environ['HOME'] + "/.reddytt"
seen_file = work_dir + "seen"
unseen_file = work_dir + "unseen"
print("Checking for reddytt working directory (%s)." % work_dir)
if not os.path.isdir(work_dir):
    print("Working directory not found. Creating %s, and files." % work_dir)
    os.mkdir(work_dir)
    os.system("touch %s" % seen_file)
    os.system("touch %s" % unseen_file)
else:
    print("Working directory found. Proceeding.")

# Read subreddit from input
#subreddit = input("Enter subreddit name: ")
# Hard-coding for dev-purposes:
subreddit = "deepintoyoutube"
subreddit = "https://reddit.com/r/" + subreddit

pm = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',ca_certs=certifi.where())
html_page = pm.request('GET', subreddit)
soup = BeautifulSoup(html_page.data, "lxml")
links = []
for link in soup.find_all('a'):
    links.append(str(link.get('href')))

new_links = list(sorted(set(filter(re.compile("^https://youtu.be").match, links))))
new_links += list(sorted(set(filter(re.compile("^https://www.youtube.com").match, links))))

for link in new_links:
    os.system("mpv %s" % link)
