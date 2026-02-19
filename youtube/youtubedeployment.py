

from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pymongo
import csv
import os
import time

application = Flask(__name__) # initializing a flask app
app=application

@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/review',methods=['POST','GET'])
@cross_origin()
def index():
    if request.method=="POST":
        try:
            api_key = "AIzaSyBK8lYpeqqGkFgAnjLmrUqp-pkJ_HeqKHY"
            #channel_id="UCOeZUa2FdnxCtcdyTdvA1vQ"
            playlist_id=request.form['content'].replace(" ","")

            youtube = build("youtube","v3",developerKey=api_key)
            def get_video_ids(youtube,playlist_id):
                request = youtube.playlistItems().list(
                    part="contentDetails",
                    playlistId=playlist_id,
                    maxResults = 50)
                response=request.execute()
                video_ids=[]
                for i in range(len(response["items"])):
                    video_ids.append(response["items"][i]["contentDetails"]["videoId"])

                next_page_token = response.get("nextPageToken")
                more_pages = True
                
                while more_pages:
                    if next_page_token is None:
                        more_pages=False
                    else:
                        request = youtube.playlistItems().list(
                            part="contentDetails",
                            playlistId=playlist_id,
                            maxResults = 50,
                            pageToken=next_page_token)
                        response=request.execute()
                        for i in range(len(response["items"])):
                            video_ids.append(response["items"][i]["contentDetails"]["videoId"])

                        next_page_token= response.get("nextPageToken")
                return
            @get_video_ids
            def get_video_details(youtube, video_ids):
                video_ids=get_video_ids(youtube,playlist_id)
                filename = searchString + ".csv"
                with open(filename, "w", newline='', encoding='utf-8') as fw:
                        headers = ["Price","Product","Customer Name", "Rating","Heading","Comment"]
                        writer = csv.DictWriter(fw, fieldnames=headers)
                        writer.writeheader()
                        all_video_stats = []
                        for i in range(0,len(video_ids),50):
                            request = youtube.videos().list(
                                part="snippet,contentDetails,statistics",
                                id = ",".join(video_ids[i:i+50]))
                            response=request.execute()
                            for video in response["items"]:
                                video_title=dict(Title = video["snippet"]["title"])
                                video_date=dict( Published_date=video["snippet"]["publishedAt"])
                                video_views=dict(Views = video["statistics"]["viewCount"])
                                video_likes=dict (Likes = video["statistics"]["likeCount"])
                                video_dislikes=dict(Dislikes = video["statistics"]["favoriteCount"])
                                video_comments=dict(Comments = video["statistics"]["commentCount"])

                                video_details = {
                                    "Price": video_title,
                                    "Product": video_date,
                                    "Customer Name": video_views,
                                    "Rating": video_likes,
                                    "Heading": video_dislikes,
                                    "Comment": video_comments}
                                
                                all_video_stats.append(video_details)
                        return all_video_stats
                        writer.writerows(all_video_stats)
            client = pymongo.MongoClient("mongodb+srv://mangeshsambare1:mangeshsambare1@cluster0.cw3cocl.mongodb.net/?retryWrites=true&w=majority")
            db = client['Youtube_scrapping']
            review_col = db['Youtube_data']
            review_col.insert_many(all_video_stats)            
            return render_template('results.html', reviews=all_video_stats[0:(len(all_video_stats)-1)])
        except Exception as e:
            print('The Exception message is: ',e)
            return 'something is wrong'
    else:
        return render_template('index.html')
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8001, debug=True)