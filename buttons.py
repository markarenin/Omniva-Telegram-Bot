import gettext
import json

from requests.models import requote_uri

def language(_):
    inline = {
        "inline_keyboard":[
            [
                {"text": _("Russian"), "callback_data": "start|0"},
                {"text": _("English"), "callback_data": "start|1"},
                {"text": _("Estonian"), "callback_data": "start|2"}
            ]
        ]
    }
    return json.dumps(inline)

def parcel_more_delete(_, url, code):
    inline = {
        "inline_keyboard":[
            [
                {"text": _("More"), "url": url}
            ],
            [ 
                {"text": _("Delete"), "callback_data": "delete|"+code}
            ]
        ]
    }
    inline = json.dumps(inline)
    return inline

def help(_):
    inline = {
        "inline_keyboard":[
            [
                {"text": _("Problems with the parcel"), "callback_data": "help|parcel"}
            ],
            [ 
                {"text": _("Problems with the bot"), "callback_data": "help|bot"}
            ]
        ]
    }
    inline = json.dumps(inline)
    return inline

def omniva(_):
    inline = {
        "inline_keyboard":[
            [
                {"text": _("More"), "url":"https://www.omniva.ee/private/help"}
            ]
        ]
    }
    return json.dumps(inline)

def contact(_):
    inline = {
        "inline_keyboard":[
            [
                {"text": _("Write to the developer"), "url":"https://t.me/paneelmaja"}
            ]
        ]
    }
    return json.dumps(inline)


def cancel(_):
    inline = {
    "inline_keyboard":[
            [
                {"text": _("Cancel"), "callback_data": "cancel"}
            ]
        ]
    }
    inline = json.dumps(inline)
    return inline

def keyboard(_):
    keyboard = {
        "keyboard": [
            [
                {"text": _("My packages")},
                {"text": _("Language")}
            ],
            [
                {"text": _("Help")}
            ]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False,
        "input_field_placeholder": _("Example: CE123456789EE")
    }
    return json.dumps(keyboard)
