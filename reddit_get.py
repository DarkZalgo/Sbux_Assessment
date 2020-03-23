#!/usr/bin/env python3
import sys
import os
from queue import PriorityQueue


def main():
    if len(sys.argv) is not 5:
        usage()
        exit()

    try:
        import praw
    except ModuleNotFoundError:
        print("praw module not found")
        install_choice = input("Would you like to install praw? Y/N\n")
        if install_choice.lower() == "y" or install_choice.lower == "yes":
            try:
                os.system("pip3 install praw")
            except:
                print("Could not install praw module")
                exit(-1)
            print("\npraw module installed successfully\nRunning original command")
            cmdstr = ""
            for arg in sys.argv:
                cmdstr += arg + " "
            os.system(cmdstr)
            exit(0)

    reddit = praw.Reddit(
        username=sys.argv[1],
        password=sys.argv[2],
        client_id=sys.argv[3],
        client_secret=sys.argv[4],
        user_agent="pc:reddit_get:v1 (by u/dark_zalgo)",
    )

    more_than_one_k_str = ""
    more_than_one_k_count = 0

    unique_sub_set = set()
    more_than_once_dict = dict()

    oc_count = 0
    oc = ""

    top_ten = PriorityQueue(maxsize=10)
    top_ten_str = ""

    for submission in reddit.subreddit("popular").hot(limit=100):
        title = str(submission.title)
        sub_name = submission.subreddit_name_prefixed
        comment_votes = "Comments = " + str(submission.num_comments) + " Upvotes = " + str(submission.ups)

        '''
        Checks for OC, if exists adds it to str and counts it
        '''
        if (
            " OC " in title.upper()
            or "[OC]" in title.upper()
            or "ORIGINAL CONTENT" in title.upper()
        ):
            oc_count+=1
            oc += title + "\n" + comment_votes + "\n\n"
        '''
        Checks if submission has more than 1000 comments then adds it to str
        '''
        if submission.num_comments > 1000:
            more_than_one_k_count += 1
            more_than_one_k_str += title + "\n" + comment_votes + "\n\n"

        '''
        Adds submissions to top 10 then after all 10 are added, checks if incoming
        submission has more upvotes than the lowest submission then adds it to str
        '''
        if top_ten.qsize() < 10:
            top_ten.put((submission.ups, submission))
        elif top_ten.qsize() == 10 and submission.ups > top_ten.queue[9][0]:
            top_ten.get()
            top_ten.put((submission.ups, submission))

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

    top_ten_desc = [tup for tup in top_ten.queue]
    top_ten_desc.sort(key=lambda x: -x[0])
    unique_sub_set = list(unique_sub_set)

    for i in range(len(top_ten_desc)):
        submission = top_ten_desc[i][1]
        title = str(submission.title)
        comment_votes = "Comments = " + str(submission.num_comments) + " Upvotes = " + str(submission.ups)
        top_ten_str += title + "\n" + comment_votes + "\n\n"

    multi_reddits = [subreddit for subreddit in more_than_once_dict.keys() if more_than_once_dict[subreddit] > 1]
    multi_reddits.sort()

    print_center("OC Posts")
    print(oc)
    print("Number of OC posts", oc_count)

    print_center("Greater than 1k comments")
    print(more_than_one_k_str)
    print("Number of posts greater than 1K comments:", more_than_one_k_count)

    print_center("Top Ten Posts")
    print(top_ten_str)

    print_center("Unique subreddits")
    print_center(sorted(unique_sub_set),num=len(max(unique_sub_set,key=lambda x: len(x)))+2)
    print("Number of unique subreddits:", len(unique_sub_set))

    print_center("Creating multi reddit with the following reddits:", num=55)
    print_center(multi_reddits, first=False,num=55)

    #reddit.multireddit.create("More Than Once r/popular", multi_reddits)


def usage():
    print("./reddit_get.py <reddit username> <reddit password> <client secret> <client id>")


def center(dash, string):
    return f"{{:^{len(dash)}}}".format(string)


def print_center(in_str, num=27,first=True):
    dashes = "-" * num
    if first:
        print("\n"+dashes)
    if isinstance(in_str, list):
        for s in in_str:
            print(center(dashes,s))
    if isinstance(in_str, str):
        print("\n")
        print(center(dashes, in_str))
        print("\n")
    print(dashes+"\n")


if __name__ == "__main__":
    main()

