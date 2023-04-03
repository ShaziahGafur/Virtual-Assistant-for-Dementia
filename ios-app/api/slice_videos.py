import time
from datetime import date, datetime
from pytz import timezone
from flask import Flask, request
from flask_cors import CORS, cross_origin
from config import *

# Audio and Video Manipulation
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips
from pydub import AudioSegment
from pydub.playback import play

# Imports the Google Cloud client library
from google.cloud import speech
from google.cloud import storage

import glob, os
from os import listdir
from os.path import isfile, join
import io
import random
import re
import shutil

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

tz = timezone('EST')
date_today = datetime.now(tz).strftime("%B %d, %Y")
month = datetime.now(tz).strftime("%B")
year = datetime.now(tz).strftime("%Y")

# Change these
patient_ID = 1
FP_ID = 2
file_name_in_cloud = "short_prompts.mp4"
source_video="Patients/"+str(patient_ID)+"/Familiar Person/"+str(FP_ID)+"/combinedVideos/"+file_name_in_cloud

try:
    ## DOWNLOADING VIDEO
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GOOGLE_APPLICATION_CREDENTIALS
    client=storage.Client()
    bucket_name = "familiar-person" 
    bucket=client.get_bucket(bucket_name)

    blob_video = bucket.blob(source_video)

    start_byte = 0 # Reading from beginning
    end_byte = 9999999999 # SETTING MAX SIZE FOR VIDEO & AUDIO

    destination_file_name = "tmp/media_from_bucket/"+file_name_in_cloud
    blob_video.download_to_filename(destination_file_name, start=0, end=end_byte)

    print("\n[SUCCESS] Downloaded bytes {} to {} of video object {} from bucket {} to local file {}.".format(
        start_byte, end_byte, source_video, bucket_name, destination_file_name
    ))

except Exception as e:
    if str(e).startswith('404'):
        print("[WARNING] Did not find file(s) in bucket! Perhaps this prompt is invalid.\n")
        print(e)

    else:
        print("[ERROR]: Could not download media files from bucket.\n")
        print(e)


## SLICING VIDEO

short_clips_video = VideoFileClip(destination_file_name)

short_clips = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
        "first",
        "second",
        "third",
        "fourth",
        "fifth",
        "sixth",
        "seventh",
        "eighth",
        "ninth",
        "tenth",
        "eleventh",
        "twelfth",
        "thirteenth",
        "fourteenth",
        "fifteenth",
        "sixteenth",
        "seventeenth",
        "eighteenth",
        "nineteenth",
        "twentieth",
        "twenty-first",
        "twenty-second",
        "twenty-third",
        "twenty-fourth",
        "twenty-fifth",
        "twenty-sixth",
        "twenty-seventh",
        "twenty-eighth",
        "twenty-ninth",
        "thirtieth",
        "thirty-first",
        "twenty twenty-three"
    ]

pos = 0
for clip in short_clips[:50]:
    video = short_clips_video.subclip(pos, pos + 2.5)
    pos = pos + 2.5
    video.write_videofile("voice_clone/Real_Time_Voice_Cloning/audio_clips/output/mp4/"+clip+".mp4")

clip = short_clips[49]
video = short_clips_video.subclip(pos, pos + 3)
video.write_videofile("voice_clone/Real_Time_Voice_Cloning/audio_clips/output/mp4"+clip+".mp4")

## UPLOAD FILES TO BUCKET
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GOOGLE_APPLICATION_CREDENTIALS
client=storage.Client()
bucket_name = "familiar-person" 
bucket=client.get_bucket(bucket_name)

# Get list of files to upload
mp4path = os.getcwd() + r"/voice_clone/Real_Time_Voice_Cloning/audio_clips/output/mp4/"
videofiles = [f for f in listdir(mp4path) if isfile(join(mp4path, f))]
destination = "Patients/"+str(patient_ID)+"/Familiar Person/"+str(FP_ID)+"/combinedVideos/"

# Upload each .mp4 file
for clip in videofiles:
    blob = bucket.blob(destination + clip) 
    blob.upload_from_filename(mp4path + clip)

outputpath = os.getcwd() + r"/voice_clone/Real_Time_Voice_Cloning/audio_clips/output/"
audiofiles = [f for f in listdir(outputpath) if isfile(join(outputpath, f))]

# Delete all clips generated by the cloner + splitted video files + the copy of the original FP clip
try:
    for clip in audiofiles:
        os.remove(outputpath + clip)

except Exception as e:
    print(e)

try:
    for clip in videofiles:
        os.remove(mp4path + clip)

except Exception as e:
    print(e)

try:
    os.remove(outputpath[:-7] + "FP_audio_clip.wav")

except Exception as e:
    print(e)

