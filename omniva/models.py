import sys

try:
    from django.db import models
except Exception:
    print('Exception: Django Not Found, please install it with "pip install django".')
    sys.exit()



class Users(models.Model):
    telegram_id = models.IntegerField()
    name = models.TextField()
    lang = models.IntegerField(default=1)
    comment = models.TextField()
    last_messages = models.TextField(blank=True)
   
    def __str__(self):
        return self.telegram_id
        
class Update(models.Model):
    update_id = models.IntegerField()
    
class Tracks(models.Model):
    code = models.TextField()
    name = models.TextField()
    telegram_id = models.IntegerField()
    last_update = models.TextField()
    added = models.DateTimeField(auto_now_add = True)
    def __str__(self):
        return self.code

