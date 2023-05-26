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
import glob

load_dotenv()

# == OAuth Authentication ==
#
# This mode of authentication is the new preferred way
# of authenticating with Twitter.

# The consumer keys can be found on your application's Details
# page located at https://dev.twitter.com/apps (under "OAuth settings")
consumer_key=os.getenv('TWITTER_CONSUMER_KEY')
consumer_secret=os.getenv('TWITTER_CONSUMER_SECRET')

def get_auth():
  if os.path.exists("./credentials.json") and os.path.getsize("./credentials.json") > 0:
    with open("./credentials.json") as f:
        credentials = json.load(f)
        auth= tweepy.OAuth1UserHandler(
            credentials['consumer_key'],credentials['consumer_secret'],
            credentials['access_token'],credentials['access_token_secret']
          )
  else:
      auth= tweepy.OAuth1UserHandler(
          consumer_key, consumer_secret,
          callback="oob"
      )
      print("Please go to: "+auth.get_authorization_url()+" and get the PIN code")
      verifier = input("Input PIN: ")
      access_token, access_token_secret = auth.get_access_token(
          verifier
      )
      with open("./credentials.json", "w") as f:
          credentials = {
              "consumer_key": consumer_key,
              "consumer_secret": consumer_secret,
              "access_token": access_token,
              "access_token_secret": access_token_secret
          }
          json.dump(credentials, f)
  return auth

def get_current_position(base_path):
  if os.path.exists(f"{base_path}lastrun.json") and os.path.getsize(f"{base_path}lastrun.json") > 0:
    with open(f"{base_path}lastrun.json") as f:
      return json.load(f)
  return 0,None

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

def get_count_in_file(filename):
  if os.path.exists(filename):
    with open(filename,'r+') as file:
      if os.path.getsize(filename) > 0:
        file_data = json.load(file)
        return len(file_data)
  return 0

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

# Create the API object
api = tweepy.API(auth=get_auth())

username=input("Please enter the username to process: ").replace("@","")

base_path = "./twitter-archive-@"+username+"/"
isExist = os.path.exists(base_path)
if not isExist:
  os.makedirs(base_path)

MAX = 250
page_counter, max_id = get_current_position(base_path)

# Run this as long as we can, or until interrupted
running = True
while running:
  cursor = tweepy.Cursor(api.user_timeline,screen_name=username, max_id=max_id)
  if len(list(cursor.items(MAX))) <= 1:
      running = False
  for status in cursor.items(MAX):
      jsonpath = f"{base_path}statuses-{page_counter}.json"
      count = (int(get_count_in_file(jsonpath)) + (MAX*page_counter+1))+1

      print(f"Saved status #{str(count)}\n")
      print(f"id: {str(status.id)} \n")
      print(f"text:\n {status.text} \n----")

      medias = status.entities.get('media', [])
      if(len(medias) > 0):
        add_media(status)
      write_json(status._json,jsonpath)
      if (count % MAX == 0):
        print(f"Processed {MAX} items, sleeping for 3s")
        page_counter += 1
        time.sleep(3)
      with open(f"{base_path}lastrun.json",'w+') as file:
        json.dump((page_counter, status.id),file, indent=4)

jsonpath = f"{base_path}statuses-{page_counter}.json"
count = (int(get_count_in_file(jsonpath)) + (MAX*page_counter+1))+1
print(f"Finished at {count} items. No more available through the API")