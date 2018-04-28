# !/usr/bin/python
# -*- coding: utf-8 -*-
from credentials import *
import argparse
from datetime import datetime
import os
import pywikibot as pwb
import random
import requests
import time
import tweepy


EXTENSIONS = ["jpg", "jpeg", "png"]
TIMER = 2
VARIATION = 16


def get_time(formt):
    now = datetime.now()
    if formt == 12:
        fstr = '%I:%M'
    elif formt == 24:
        fstr = '%H:%M'
    return datetime.strftime(now, fstr)


def make_cat(tme):
    return "Time_{}".format(tme)


def get_cat_members(cat):
    base = "https://commons.wikimedia.org/w/api.php?" \
        "action=query&list=categorymembers&format=json" \
        "&cmtype=file&cmtitle=Category:{}"
    category = base.format(cat)
    r = requests.get(category).json()
    return r["query"]["categorymembers"]


def select_random(lst):
    only_good = [x for x in lst if x["title"].split(
        ".")[-1].lower() in EXTENSIONS]
    return random.choice(only_good)


def tweet_it(pg, tme):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    thumbnail = pg.get_file_url(url_width=1200)
    fname = pg.title(withNamespace=False)
    full_url = pg.full_url()
    fle = requests.get(thumbnail)
    with open(fname, 'wb') as f:
        f.write(fle.content)
    status = "🕰️ It's {} on #WikimediaCommons!\r\n\r\n".format(tme)
    status += full_url
    # api.update_status(status)
    # api.update_with_media(fname, status)
    print(status)
    os.remove(fname)


def wait_it(hourz):
    now = datetime.strftime(datetime.now(), '%H:%M')
    rand_variation = random.randint(-VARIATION, VARIATION)
    minutes = (hourz * 60) + rand_variation
    seconds = minutes * 60
    print("[{}] Sleeping for {} minutes…".format(now, minutes))
    time.sleep(seconds)


def main(timer):
    commons = pwb.Site("commons", "commons")
    while True:
        category = make_cat(get_time(12))
        pgs = get_cat_members(category)
        pg = select_random(pgs).get("title")
        pg = pwb.FilePage(commons, pg)
        tweet_it(pg, get_time(24))
        wait_it(timer)


if __name__ == "__main__":
    pars = argparse.ArgumentParser()
    pars.add_argument('timer', nargs='?', default=TIMER, type=int)
    main(pars.parse_args().timer)
