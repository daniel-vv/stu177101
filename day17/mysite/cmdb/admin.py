from django.contrib import admin
from .models import UserInfo
from article.models import Article

# Register your models here.

admin.site.register(UserInfo)
admin.site.register(Article)
