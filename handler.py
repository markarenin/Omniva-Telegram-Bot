# Django specific settings
import os
import sys
import traceback
sys.dont_write_bytecode = True
import django
from django.core.exceptions import ObjectDoesNotExist
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
from flask import Flask
from flask import request
django.setup()

# Import models for use in script
from omniva.models import *
import telegram as tg
import functions as f
import main as main

import gettext

global _

app = Flask(__name__)
@app.route('/', methods=["POST"])
def index():
    post = request.get_json()
    chat_id = tg.get_chat_id(post)
    tg_update_id = post['update_id']
    update = Update.objects.filter(update_id = tg_update_id).exists()
    if update == False:
        update = Update.objects.create(update_id = post['update_id'])
        try:
            #When new message receive
            if 'message' in post:
                main.message(chat_id, post['message'])
            #When revieve new Button-Event  
            elif 'callback_query' in post:
                main.callback_query(chat_id, post)
        except Exception as e:
            message = "Error User_ID: %s\n" % chat_id
            tb1 = traceback.TracebackException.from_exception(e) #Get full error message
            exc = '--'.join(tb1.format())
            sender = message + exc
            if len(sender) > 4096:
                for x in range(0, len(sender), 4096):
                    tg.sendMessage(chat_id, sender[x:x+4096])
            else:
                tg.sendMessage(chat_id, sender)
        return "ok"
    else:
        tg.sendMessage(chat_id, "Problem")
        return 'ok'

    return 'ok'

def lang_init(locale = "et_EE"):
    path = sys.argv[0]
    path = os.path.join(os.path.dirname(path),'locale')
    lang = gettext.translation(locale, path, languages=[locale])
    return lang.gettext

_ = lang_init()

if __name__ == "__main__":
    app.run()