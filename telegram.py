import json
import os
import requests

#config
import config

def sendMessage(chat_id, 
                text, 
                reply_markup = '', 
                parse_mode = '', 
                disable_notification = False, 
                allow_sending_without_reply = False):
    r = requests.post(
        url = "https://api.telegram.org/bot%s/sendMessage" % config.token,
        data = {
            'chat_id': chat_id,
            'text': text,
            'reply_markup': reply_markup,
            #'parse_mode': parse_mode,
            #'disable_notification': disable_notification,
            #'allow_sending_without_reply': allow_sending_without_reply
        }
    )
    rjson = json.loads(r.content)
    print(r.content)
    return rjson

def editMessage(chat_id, 
                message_id, 
                text = '', 
                reply_markup = '',
                parse_mode = '', 
                disable_notification = False, 
                allow_sending_without_reply = False):
    r = requests.post(
        url = "https://api.telegram.org/bot%s/editMessage" % config.token,
        data = {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': text,
            'reply_markup': reply_markup
            #'parse_mode': parse_mode,
            #'disable_notification': disable_notification,
            #'allow_sending_without_reply': allow_sending_without_reply
        }
    )
    rjson = json.loads(r.content)
    print(r.content)
    return rjson

def deleteMessage(chat_id,
                message_id):
    r = requests.post(
        url = "https://api.telegram.org/bot%s/deleteMessage" % config.token,
        data = {
            'chat_id': chat_id,
            'message_id': message_id
            #'parse_mode': parse_mode,
            #'disable_notification': disable_notification,
            #'allow_sending_without_reply': allow_sending_without_reply
        }
    )
    rjson = json.loads(r.content)
    print(r.content)
    return rjson

def get_chat_id(post):
    if 'message' in post:
        return post['message']['from']['id']
    elif 'callback_query' in post:
        return post['callback_query']['from']['id']

