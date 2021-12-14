import sys
# Turn off bytecode generation
from requests.models import cookiejar_from_dict
sys.dont_write_bytecode = True

# Django specific settings
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
from flask import request, render_template
from flask import Flask
from bs4 import BeautifulSoup
from pprint import pprint
from datetime import datetime
from requests.api import delete
import requests
import json
import re #Regular Expressions
import gettext
import functions as m
import telegram as tg
import buttons as b

def message(chat_id, message):
    _ = lang_init("en_US")
    user = m.add_get_user(chat_id)
    todelete = list()
    if user.lang == 0:
        _ = lang_init("ru_RU")
    elif user.lang == 1:
        _ = lang_init("en_US")
    else:
        _ = lang_init("et_EE")
    m.deletemessages(user)
    text = ""
    if "text" in message:
        text = message['text']
    if text == "/start":
        tg.sendMessage(chat_id, _("Select the language"), b.language(_))
    elif text == _("My packages") or text == "/mypackages":
        sender = _("{} | {}\nLatest information: \nEvent: {} \nDate: {} \nLocation: {}")
        packages = m.get_packages(chat_id)
        todelete.append(message['message_id'])
        if len(packages) > 0:
            for result in packages:
                url = "https://www.omniva.ee/api/search.php?search_barcode={}&lang={}"
                if user.lang == 0:
                    url = url.format(result.code, 'rus')
                elif user.lang == 1:
                    url = url.format(result.code, 'eng')
                else:
                    url = url.format(result.code, 'est')
                r = requests.get(url)

                if "orange_font inner_subtitle" in r.text: #If don't have information
                    noinformation = _("{} | {}\nNo information")
                    sent = tg.sendMessage(chat_id, noinformation.format(result.name, result.code), b.parcel_more_delete(_, url, result.code))
                else:
                    soup = BeautifulSoup(r.text, 'html.parser')
                    p_event = soup.tbody.tr.findChildren("td")[0].text
                    p_date = soup.tbody.tr.findChildren("td")[1].text
                    p_location = soup.tbody.tr.findChildren("td")[2].text
                    m.save_tracknumber(user, result.code, result.name, p_date)
                    sent = tg.sendMessage(chat_id, sender.format(result.name, result.code, p_event, p_date, p_location), b.parcel_more_delete(_, url, result.code))
                #To delete list
                todelete.append(sent['result']['message_id'])
        else:
            tg.deleteMessage(chat_id, message['message_id'])
            tg.sendMessage(chat_id, _("First add the parcels. Just enter the track number in the messages"))
        user.last_messages = json.dumps(todelete)
        user.save()
        print("ok")
    elif text == _("Language") or text == "/language":
        sent = tg.sendMessage(chat_id, _("Select the language"), b.language(_))
    else: 
        if user.telegram_id == 644873114:
            if "admin" in text:
                users = m.get_all_users()
                for _user in users:
                    if _user.lang == 0:
                        _ = lang_init("ru_RU")
                    elif _user.lang == 1:
                        _ = lang_init("en_US")
                    else:
                        _ = lang_init("et_EE")
                    tg.sendMessage(_user.telegram_id, _("Update:\n    - Added mandatory naming of parcels\n    - Bug fixes\n    - Added Help Button\n    - Added English language\n    - Added Estonian language\nIf you encounter problems. Contact @paneelmaja"), b.keyboard(_))
                    tg.sendMessage(_user.telegram_id, _("Select the language"), b.language(_))
                return "ok"
            elif "remove" in text:
                remover = {
                    "remove_keyboard": True
                }
                tg.sendMessage(chat_id, "removed", json.dumps(remover))
                return "ok"
        if text == _("Help"):
            tg.sendMessage(chat_id, _("Choose what the problem is"), b.help(_))
            return "ok"
        elif "name" not in user.comment: #When user writed Code
            if len(text) < 4 or len(text) >  16:
                tg.sendMessage(chat_id, _("Error: Check is that correct track number")+" #0")
                return "ok"
            reg = re.compile('^[A-Za-z0-9\.]+$')
            if reg.match(text) is None:
                tg.sendMessage(chat_id, _("Error: Check is that correct track number")+" #1")
                return "ok"
            
            m.set_status(user, "name|" + text)
            sent = tg.sendMessage(chat_id, _("Enter a name for the track number %s") % (text,), b.cancel(_))
            #todelete.append(post['message']['message_id'])
            todelete.append(sent['result']['message_id'])
            user.last_messages = json.dumps(todelete)
            user.save()
        elif 'name' in user.comment: #When user have to write name of parcel
            if len(text) < 1 or len(text) >  64:
                tg.sendMessage(chat_id, _("Error: Check is that correct name")+" #0")
                return "ok"
            sent = tg.sendMessage(chat_id, _("Wait, getting parcel information"))
            sent = sent['result']['message_id']
            code = user.comment.split('|')[1]
            url = "https://www.omniva.ee/api/search.php?search_barcode={}&lang={}"
            if user.lang == 0:
                url = url.format(code, 'rus')
            elif user.lang == 1:
                url = url.format(code, 'eng')
            else:
                url = url.format(code, 'est')
            r = requests.get(url)
            if "orange_font inner_subtitle" in r.text:
                soup = BeautifulSoup(r.text, 'html.parser')
                m.save_tracknumber(user, code, text)
                tg.editMessage(chat_id, sent, _("We saved the track number and the bot will let you know as soon as there is any information"))
                tg.sendMessage(chat_id, soup.h6.text)
                m.set_status(user, "None")
                return 'ok'
            
            #PARSING
            soup = BeautifulSoup(r.text, 'html.parser')
            sender = _("{} | {}\nLatest information: \nEvent: {} \nDate: {} \nLocation: {}")
            p_event = soup.tbody.tr.findChildren("td")[0].text
            p_date = soup.tbody.tr.findChildren("td")[1].text
            p_location = soup.tbody.tr.findChildren("td")[2].text
            #PARSING

            m.set_status(user, "None")
            m.save_tracknumber(user, code, text, p_date)
            tg.editMessage(chat_id, sent, sender.format(text, code, p_event, p_date, p_location), b.parcel_more_delete(_, url, code))
        else:
            tg.sendMessage(chat_id, _("Error. If there is a problem, contact us @paneelmaja"))
    ###########################################        
    return "ok"

def callback_query(chat_id, post):
    _ = lang_init("en_US")
    user = m.add_get_user(chat_id)
    todelete = list()
    if user.lang == 0:
        _ = lang_init("ru_RU")
    elif user.lang == 1:
        _ = lang_init("en_US")
    else:
        _ = lang_init("et_EE")
    m.deletemessages(user)
    command = post['callback_query']['data']
    if 'start' in command:
        lang = int(command.split('|')[1])
        if lang == 0:
            _ = lang_init("ru_RU")
            user.lang = 0
            #SET LANG
        elif lang == 1:
            _ = lang_init("en_US")
            user.lang = 1
            #SET LANG
        elif lang == 2:
            _ = lang_init("et_EE")
            user.lang = 2
            #SET LANG
        user.save()
        tg.deleteMessage(chat_id, post['callback_query']['message']['message_id'])
        tg.sendMessage(chat_id, _("Translated by @zadex"))
        tg.sendMessage(chat_id, _("Hi. You can now enter the tracking number to track the parcel.\n"), b.keyboard(_))
    elif 'cancel' in command:
        m.set_status(user, "None")
        message_id = post['callback_query']['message']['message_id']
        tg.deleteMessage(chat_id, message_id)
    elif 'delete' in command:
        m.set_status(user, 'none')
        code = command.split('|')[1]
        message_id = post['callback_query']['message']['message_id']
        tg.deleteMessage(chat_id, message_id)
        m.delete_tracknumber(user, code)
        tg.sendMessage(chat_id, _("Parcel deleted from bot database"))
    elif 'help' in command:
        problem = command.split('|')[1]
        tg.deleteMessage(chat_id, post['callback_query']['message']['message_id'])
        if problem == 'parcel':
            tg.sendMessage(chat_id, 
                _("Contacts Omniva:\n    Telephone: 661 6616\n    Email: info@omniva.ee\n    Mon-Fri 9:00-20:00\n    Sat-Sun and on public holidays 9:00-15:00"), 
                b.omniva(_), 
                parse_mode='HTML'
            )
        elif problem == 'bot':
            tg.sendMessage(chat_id,
                _("<b>Developer: Adam A.</b>\n  Telegram: @paneelmaja\n  Email: adam@cahlan.cc\n\n<b>Translated by @zadex</b>\n  Website: https://crowdin.com/profile/laurisade"),
                reply_markup=b.contact(_),
                parse_mode="HTML"
            )

def schedule():
    _ = lang_init()
    tracks = m.Tracks.objects.all()
    for track in tracks:
        url = "https://www.omniva.ee/api/search.php?search_barcode={}&lang={}"
        user = m.Users.objects.get(telegram_id = track.telegram_id)
        if user.lang == 0:
            _ = lang_init("ru_RU")
            url = url.format(track.code, 'rus')
        elif user.lang == 1:
            _ = lang_init("en_US")
            url = url.format(track.code, 'eng')
        else:
            _ = lang_init()
            url = url.format(track.code, 'est')
        sender = _("New information: {} | {} \nEvent: {} \nDate: {} \nLocation: {}")
        r = requests.get(url)
        if "orange_font inner_subtitle" in r.text: #If don't have information
            noinformation = _("{} | {}\nNo information")
        else:
            soup = BeautifulSoup(r.text, 'html.parser')
            p_event = soup.tbody.tr.findChildren("td")[0].text
            p_date = soup.tbody.tr.findChildren("td")[1].text
            p_location = soup.tbody.tr.findChildren("td")[2].text

            olddate = datetime.strptime("01.09.1977 00:00", "%d.%m.%Y %H:%M")
            if track.last_update is not None:
                olddate = datetime.strptime(track.last_update, "%d.%m.%Y %H:%M")
            print(olddate)
            newdate = datetime.strptime(p_date, "%d.%m.%Y %H:%M")

            if olddate < newdate:
                m.save_tracknumber(user, track.code, track.name, p_date)
                tg.sendMessage(user.telegram_id, sender.format(track.name, track.code, p_event, p_date, p_location), b.parcel_more_delete(_, url, track.code))
    return 'ok'

def lang_init(locale = "et_EE"):
    """
    Initialize a translation framework (gettext).
    Typical use::
        _ = lang_init()

    :return: A string translation function.
    :rtype: (str) -> str
    """

    path = sys.argv[0]
    path = os.path.join(os.path.dirname(path),'locale')
    lang = gettext.translation(locale, path, languages=[locale])
    return lang.gettext

