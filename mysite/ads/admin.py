from django.contrib import admin
from ads.models import Ad, Comment, Fav

# Register your models here.

admin.site.register(Ad)
admin.site.register(Fav)
admin.site.register(Comment)