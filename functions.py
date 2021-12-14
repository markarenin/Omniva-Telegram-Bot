from django.core.exceptions import ObjectDoesNotExist
import os
from django.db.models.manager import EmptyManager
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import json
from flask import Flask 
from flask import request, render_template
from datetime import datetime
import django
import telegram as tg


django.setup()
#import db as db
# Import your models for use in your script
from omniva.models import *
 
def set_status(user, comment):
    if comment is None:
        comment = "None"
    user.comment = str(comment)
    user.save()

def save_tracknumber(user, track_number, name, updatetime = datetime.now().strftime('%d.%m.%Y %H:%M')):
    try:
        track = Tracks.objects.get(telegram_id = user.telegram_id, code = track_number)
        track.last_update = updatetime
        track.name = name
        track.save()
        return user
    except ObjectDoesNotExist: #if null then
        track = Tracks.objects.create(telegram_id = user.telegram_id, code = track_number, name = name, last_update = updatetime)
        return user

def get_packages(telegram_id):
    tracks = Tracks.objects.filter(telegram_id = telegram_id)
    return tracks

def delete_tracknumber(user, code):
    Tracks.objects.filter(telegram_id = user.telegram_id, code = code).delete()

def get_chat_id(post):
    if 'message' in post:
        return post['message']['from']['id']
    elif 'callback_query' in post:
        return post['callback_query']['from']['id']
    else:
        return "error"

def add_get_user(chat_id):
    try:
        user = Users.objects.get(telegram_id=chat_id)
        return user
    except ObjectDoesNotExist: #if null then
        user = Users.objects.create(telegram_id=chat_id)
        return user

def get_all_users():
    users = Users.objects.all()
    return users

def deletemessages(user):
    js = user.last_messages
    if js == None or js == "":
        return 'ok'
    else:
        js = json.loads(js)
        for jsone in js:
            tg.deleteMessage(user.telegram_id, jsone)
            user.last_messages = None
    user.save()
    return 'ok'
