#!/usr/bin/env python3
import praw
import sys

def main():
    if len(sys.argv) < 4:
        usage()
        exit()

    reddit = praw.Reddit(
        username=sys.argv[1],
        password=sys.argv[2],
        client_id=sys.argv[3],
        client_secret=sys.argv[4],
        user_agent="pc:reddit_get:v1 (by u/dark_zalgo)",
    )

    gt1k = ""
    oc = ""
    sub_set = set()
    sub_dict = dict()

    for subreddit in reddit.subreddit("popular").hot(limit=100):
        sub_set.add(subreddit.subreddit_name_prefixed)

    for submission in reddit.subreddit("popular").hot(limit=100):
        title = str(submission.title)
        sub_name = submission.subreddit_name_prefixed

        comment_votes =                    \
            "Comments = "                  \
            + str(submission.num_comments) \
            + " Upvotes = "                \
            + str(submission.ups)

        comment_votes = "Comments = " + str(submission.num_comments) + " Upvotes = " + str(submission.ups)


        if sub_name not in sub_dict.keys():
            sub_dict[sub_name] = 1
        elif sub_name in sub_dict.keys():
            sub_dict[sub_name] += 1

        if submission.num_comments > 1000:
            gt1k += title + "\n" + comment_votes + "\n"

        if (
            " OC " in str(title).upper()
            or "[OC]" in str(title).upper()
            or "ORIGINAL CONTENT" in str(title).upper()
        ):
            oc += submission.title + "\n" + comment_votes + "\n"

    multi_reddits = [subreddit for subreddit in sub_dict.keys() if sub_dict[subreddit] > 1]
    reddit.multireddit.create("Assessment Multi", multi_reddits)

    print("Unique subreddits")
    for unique in sub_set:
        print(unique)
    print("\nGreater than 1k comments")
    print(gt1k)
    print("OC Posts")
    print(oc)


def usage():
    print("./reddit_get.py <reddit username> <reddit password> <client secret> <client id>")

if __name__ == "__main__":
    main()