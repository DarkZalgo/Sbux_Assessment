#!/usr/bin/env python3
import sys
from queue import PriorityQueue
from datetime import datetime
import csv
import re
import praw

'''
Gets date for csv timestamp
'''
date = datetime.now().strftime("%Y-%m-%d_%I-%M-%S%p")


def main():
    if len(sys.argv) is not 5:
        usage()
        exit()


    '''
    Instantiates the Reddit object with a user given username, password, client_id, and client_secret
    '''
    username = sys.argv[1]
    reddit = praw.Reddit\
    (
        username=username,
        password=sys.argv[2],
        client_id=sys.argv[3],
        client_secret=sys.argv[4],
        user_agent="pc:reddit_get:v1 (by u/dark_zalgo)"
    )

    more_than_one_k_list = []
    more_than_one_k_count = 0

    unique_sub_set = set()
    more_than_once_dict = dict()

    oc_count = 0
    oc_list = []

    top_ten_q = PriorityQueue(maxsize=10)

    for submission in reddit.subreddit("popular").hot(limit=100):
        sub_name = submission.subreddit_name_prefixed

        '''
        Checks for OC, if exists adds it to list and counts it
        '''
        if submission.is_original_content:
            oc_count += 1
            oc_list.append(submission)
        '''
        Checks if submission has more than 1000 comments then adds it to list
        '''
        if submission.num_comments > 1000:
            more_than_one_k_count += 1
            more_than_one_k_list.append(submission)

        '''
        Adds submissions to top 10 then after all 10 are added, checks if incoming
        submission has more upvotes than the lowest submission then adds it to queue
        '''
        if top_ten_q.qsize() < 10:
            top_ten_q.put((submission.ups, submission))
        elif top_ten_q.qsize() == 10 and submission.ups > top_ten_q.queue[9][0]:
            top_ten_q.get()
            top_ten_q.put((submission.ups, submission))

        '''
        Creates a unique set of every subreddit name
        '''
        unique_sub_set.add(sub_name)

        '''
        Counts the occurrence of each subreddit
        '''
        if sub_name not in more_than_once_dict.keys():
            more_than_once_dict[sub_name] = 1
        elif sub_name in more_than_once_dict.keys():
            more_than_once_dict[sub_name] += 1

    '''
    Sorts the top ten priority queue in descending order in a new list
    '''
    top_ten_list = [tup[1] for tup in sorted(top_ten_q.queue, key=lambda x: -x[0])]

    '''
    Turns the unique subreddit set into a list for sorting and iteration
    '''
    unique_sub_set = list(unique_sub_set)

    '''
    Places all the subreddits that occur more than once into a list
    then sorts it by alphabetical order for easier viewing for multireddit
    '''
    multi_reddits = [subreddit for subreddit in more_than_once_dict.keys() if more_than_once_dict[subreddit] > 1]
    multi_reddits.sort(key=lambda x: x.upper())

    '''
    Checks if multireddit exists, if it does asks for overwrite, if it doesn't, simply creates it.
    '''
    if reddit.subreddits.search_by_name("new_multi"):
        if input("Multireddit exists, would you like to overwrite it?\n").lower() == "y":
            reddit.multireddit(username, 'new_multi').delete()
            reddit.multireddit.create("new_multi", multi_reddits)

            print("Creating multireddit new_multi with the following reddits:")
            [print(reddit) for reddit in multi_reddits]
            print("Done!")
    else:
        reddit.multireddit.create("new_multi", multi_reddits)

        print("Creating multireddit new_multi with the following reddits:")
        [print(reddit) for reddit in multi_reddits]
        print("Done!")

    '''
    Creates the csv for each of the submission lists
    '''
    sub_to_csv(oc_list, "oc")
    sub_to_csv(more_than_one_k_list, "more_than_one_k")
    sub_to_csv(top_ten_list, "top_ten")

    '''
    Creates a CSV without a function because unique_sub_list has different fields
    '''
    with open('unique_submissions_' + date + ".csv", 'w') as unique_csv:
        unique_writer = csv.writer(unique_csv, delimiter=",")
        unique_writer.writerow(["subreddit_name", "subreddit_url"])
        for unique_sub in sorted(unique_sub_set, key=lambda x: x.upper()):
            unique_writer.writerow([unique_sub[2:], "https://reddit.com/"+str(unique_sub)])
    print(sys.version)


def usage():
    print("./reddit_get.py <reddit username> <reddit password> <client id> <client secret>")

'''
Given a list of submissions and their category, writes a CSV file 
'''
def sub_to_csv(submission_list, category):
    with open(category + '_submissions_' + date + ".csv", 'w') as csv_file:
        sub_writer = csv.writer(csv_file, delimiter=",", quotechar=chr(34), quoting=csv.QUOTE_NONE, escapechar=",")

        sub_writer.writerow(["Title", "URL", "Upvotes", "Comments"])

        for sub in submission_list:      #Removes commas that mess up the output of CSV
            sub_writer.writerow([re.sub(",", "", sub.title), "https://www.reddit.com" + sub.permalink,
                                 sub.ups, sub.num_comments])


if __name__ == "__main__":
    main()

