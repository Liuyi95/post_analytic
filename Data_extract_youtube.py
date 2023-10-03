#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  2 22:38:26 2023

@author: liuyichen
"""


from apiclient.discovery import build
import argparse
import csv
import unidecode
import googleapiclient.discovery
import googleapiclient.errors

DEVELOPER_KEY = "AIzaSyBClUmXCK8LjGBhtqn6DkRchVZMFb8uUJ8"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def get_comments(video_id, youtube):
    try:
        comment_request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=15
        )
        comment_response = comment_request.execute()
    
        comments = []  # Initialize an empty list to store comments
    
        for comment_item in comment_response.get("items", []):
            comment = comment_item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            comments.append(comment)  # Append comments to the list
    
        if not comments:
            comments = "No comments"
    
        return comments

    except googleapiclient.errors.HttpError as e:
        if "commentsDisabled" in str(e):
            return "Comments are disabled for this video"
        else:
            raise

def youtube_search(options):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
    search_response = youtube.search().list(q=options.q, part="id,snippet", maxResults=options.max_results).execute()
    
    videos = []
    channels = []
    playlists = []
    # Create a CSV output for the video list    
    with open('a_haunting_in_venice_result.csv', 'w', newline='', encoding='utf-8') as csvFile:
        csvWriter = csv.writer(csvFile)
        csvWriter.writerow(["title", "videoId", "viewCount", "likeCount", "dislikeCount", "commentCount", "favoriteCount", "publishedDate", "comments"])

        for search_result in search_response.get("items", []):
            if search_result["id"]["kind"] == "youtube#video":
                title = search_result["snippet"]["title"]
                title = unidecode.unidecode(title)
                videoId = search_result["id"]["videoId"]
                video_response = youtube.videos().list(id=videoId, part="statistics").execute()
                publishedDate = search_result["snippet"]["publishedAt"]

                viewCount = video_response["items"][0]["statistics"]["viewCount"]
                likeCount = video_response["items"][0]["statistics"].get("likeCount", 0)
                dislikeCount = video_response["items"][0]["statistics"].get("dislikeCount", 0)
                commentCount = video_response["items"][0]["statistics"].get("commentCount", 0)
                favoriteCount = video_response["items"][0]["statistics"].get("favoriteCount", 0)

                comments = get_comments(videoId, youtube)

                csvWriter.writerow([title, videoId, viewCount, likeCount, dislikeCount, commentCount, favoriteCount, publishedDate, comments])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Search on YouTube')
    parser.add_argument("--q", help="Search term", default="a haunting in venice")
    parser.add_argument("--max-results", help="Max results", default=30)
    args = parser.parse_args()
    try:
        youtube_search(args)
    except Exception as e:
        print("An error occurred:", str(e))