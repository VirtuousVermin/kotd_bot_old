import re
import json
import praw
import time
import random
import requests
import config
import os

reddit = praw.Reddit(user_agent='KickOpenTheDoor bot by u/RPG_Ivan and u/VirtuousVermin',
                  client_id=config.client_id,
                  client_secret=config.client_secret,
                  username=config.username,
                  password=config.password)


def post_recog(easy):
    for submission in r.subreddit(easy).top(limit=10):
        if submission.id in post_list:
            continue
        while True:
            title_digits = re.findall('\\d+', submission.title)
            all_title_digits.extend(title_digits)
            if bool(title_digits) is False:
                break
            else:
                combined_digits = ''.join(str(e) for e in all_title_digits[-1])
                ints = int(combined_digits)
                time.sleep(20)
                break

        if bool(re.search('\\d+', submission.title)):
            if submission.score >= ints:
                img_today = submission.url
                submission.mod.flair('Slain!')

                # r.subreddit(easy).submit(title_names[random.randint(0,9)], url = img_today)
                post_list.append(submission.id)
                with open ("list2.txt", "a") as f:
                    f.write(submission.id + "\n")
                    print("submission filter updated")
            if submission.score != ints and submission.id not in post_list:
                submission.mod.flair(f'{submission.score}/{ints} You\'re nearly there. Keep upvoting!')
                print('challenge flair assigned')

            time.sleep(25)


def list2():
    with open("list2.txt", "r") as f:
        post_list = f.read()
        post_list = post_list.split()
    return post_list


easy = 'kickopenthedoor'


post_list = list2()
all_title_digits = []
r = reddit
subreddit = r.subreddit(easy)

while True:
    post_recog(easy)