# Twitter Archiver - by Luna Winters
# A quick bot that mass saves tweets from an account
#
#The MIT License (MIT)
#
#Copyright (c) 2023 Luna Winters
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

from __future__ import absolute_import, print_function

import os
import time
import tweepy
from dotenv import load_dotenv
import urllib.request
import json

load_dotenv()

# == OAuth Authentication ==
#
# This mode of authentication is the new preferred way
# of authenticating with Twitter.

# The consumer keys can be found on your application's Details
# page located at https://dev.twitter.com/apps (under "OAuth settings")
consumer_key=os.getenv('TWITTER_CONSUMER_KEY')
consumer_secret=os.getenv('TWITTER_CONSUMER_SECRET')
username=os.getenv('TWITTER_USER_SCREEN_NAME')

#Authenticate
auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
api = tweepy.API(auth)
# access_token = auth.fetch_token(f"{auth_url}")
# client = tweepy.Client(f"{auth_url}")

base_path = "./twitter-archive-@"+username+"/"
isExist = os.path.exists(base_path)
if not isExist:
  os.makedirs(base_path)

def add_media(status):
  mediacount = 0
  tweetbase = base_path+"media/"+str(status.id)+"/"
  isExist = os.path.exists(tweetbase)
  if not isExist:
    os.makedirs(tweetbase)
  write_json(status._json,tweetbase+"tweet.json")
  for media in medias:
    mediacount+=1
    print(media['media_url'])
    urllib.request.urlretrieve(media['media_url'], tweetbase+str(mediacount)+".jpg")

# function to add to JSON
def write_json(new_data, filename='output.json'):
  file_data = [new_data]
  if os.path.exists(filename):
    with open(filename,'r+') as file:
      if os.path.getsize(filename) > 0:
        file_data = json.load(file)
        file_data.append(new_data)
  with open(filename,'w+') as file:
    json.dump(file_data,file, indent=4)

count = 0
cursor = tweepy.Cursor(api.user_timeline,screen_name=username)
for status in cursor.items():
    count +=1
    print("Saved status " + str(count) + " of " + str(max) + "\n")
    print("id: " + str(status.id) + "\n")
    print("text:\n" + status.text + "\n----")
    medias = status.entities.get('media', [])
    if(len(medias) > 0):
      add_media(status)
    write_json(status._json,base_path+"statuses.json")
    if (count % 1000 == 0):
      print("Processed 1000 items, sleeping for 10s")
      time.sleep(10)