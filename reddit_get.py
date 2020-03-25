#!/usr/bin/env python3
import sys
import os
from queue import PriorityQueue
from datetime import datetime
import csv
import re

now = datetime.now()


def main():
    if len(sys.argv) is not 5:
        usage()
        exit()
    '''
    Tries to import praw and if it's not found will ask for user input to install
    after install will re-run the command given by the user
    '''
    try:
        import praw
    except ModuleNotFoundError:
        print("praw module not found")
        install_choice = input("Would you like to install praw? Y/N\n")
        if install_choice.lower() == "y" or install_choice.lower == "yes":
            try:
                os.system("pip3 install praw")
            except Exception as e:
                print("Could not install praw module")
                print(e)
                exit(-1)

            cmdstr = ""
            for arg in sys.argv:
                cmdstr += arg + " "
            print("\npraw module installed successfully\nRunning original command\n"+cmdstr)
            os.system(cmdstr)
            exit(0)

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
        Checks for OC, if exists adds it to str and counts it
        '''
        if submission.is_original_content:
            oc_count += 1
            oc_list.append(submission)
        '''
        Checks if submission has more than 1000 comments then adds it to str
        '''
        if submission.num_comments > 1000:
            more_than_one_k_count += 1
            more_than_one_k_list.append(submission)

        '''
        Adds submissions to top 10 then after all 10 are added, checks if incoming
        submission has more upvotes than the lowest submission then adds it to str
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
    then sorts it by alphabetical order for easier viewing
    '''
    multi_reddits = [subreddit for subreddit in more_than_once_dict.keys() if more_than_once_dict[subreddit] > 1]
    multi_reddits.sort(key=lambda x: x.upper())

    print("Number of OC posts", oc_count)

    print("Number of posts greater than 1K comments:", more_than_one_k_count)

    print_center("Unique subreddits")
    print_center(sorted(unique_sub_set, key=lambda x: x.upper()), num=len(max(unique_sub_set, key=lambda x: len(x)))+2)
    print("Number of unique subreddits:", len(unique_sub_set))

    print_center("Creating multi reddit with the following reddits:", num=55)
    print_center(multi_reddits, num=55)

    '''
    Creates the multireddit
    '''
    #reddit.multireddit.create("new_multi", multi_reddits)
    sub_to_csv(oc_list, "Original Content")
    sub_to_csv(more_than_one_k_list, "More Than 1000 Comments")
    sub_to_csv(top_ten_list, "Top Ten")


def usage():
    print("./reddit_get.py <reddit username> <reddit password> <client id> <client secret>")


'''
Formats the string centered on the length of the dashes
'''
def center(dash, string):
    return f"{{:^{len(dash)}}}".format(string)


'''
Prints a given list or string centered on dashes
'''
def print_center(in_str, num=27):
    dashes = "-" * num
    print("\n" + dashes)

    if isinstance(in_str, list):
        for s in in_str:
            print(center(dashes, s))

    elif isinstance(in_str, str):
        print("\n")
        print(center(dashes, in_str))
        print("\n")

    print(dashes + "\n")


'''
Given a list of submissions and their category,
writes a CSV file 
'''
def sub_to_csv(submission_list, category):
    with open ('submissions_' + now.strftime("%Y-%m-%d_%I-%M-%S_%p") + ".csv", 'a') as csvfile:

        sub_writer = csv.writer(csvfile, delimiter=",", quotechar='\"', quoting=csv.QUOTE_NONE, escapechar='\\')
        if not hasattr(sub_to_csv, 'created_header'):
            sub_to_csv.created_header = True
            sub_writer.writerow(["Category", "Title", "URL", "Upvotes", "Comments"])


        for sub in submission_list:
            sub_writer.writerow([category, re.sub(",", "", sub.title), "https://www.reddit.com"+sub.permalink, sub.ups, sub.num_comments])
            print(sub.title)


if __name__ == "__main__":
    main()

