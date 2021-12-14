import sys
import buttons as b
import time
import os
import functions as m
import gettext
import requests
from bs4 import BeautifulSoup
from datetime import date, datetime

from apscheduler.schedulers.background import BackgroundScheduler

global _

def job():
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

            #if user.telegram_id == 644873114:
            #    sent = m.sendMessage(user.telegram_id, sender.format(track.name, track.code, p_event, p_date, p_location), b.parcel_more_delete(_, url, track.code))
            if olddate < newdate:
                m.save_tracknumber(user, track.code, track.name, p_date)
                m.sendMessage(user.telegram_id, sender.format(track.name, track.code, p_event, p_date, p_location), b.parcel_more_delete(_, url, track.code))

    #os.system('python test.py')

def lang_init(locale = "et_EE"):
    """
    Initialize a translation framework (gettext).
    Typical use::
        _ = lang_init()

    :return: A string translation function.
    :rtype: (str) -> str
    """
    #_locale, _encoding = locale.getdefaultlocale()  # Default system values

    path = sys.argv[0]
    path = os.path.join(os.path.dirname(path),'locale')
    lang = gettext.translation(locale, path, languages=[locale])
    return lang.gettext

if __name__ == '__main__':
    _ = lang_init()
    # creating the BackgroundScheduler object
    scheduler = BackgroundScheduler()
    # setting the scheduled task
    scheduler.add_job(job, 'interval', minutes=15)
    # starting the scheduled task using the scheduler object
    scheduler.start()

    #try:
    #    # To simulate application activity (which keeps the main thread alive).
    #    while True:
    #        time.sleep(1)
    #except (KeyboardInterrupt, SystemExit):
    #    # Not strictly necessary but recommended
    #    scheduler.shutdown()

