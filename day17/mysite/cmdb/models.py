from django.db import models

# Create your models here.
#用户数据库类,一定要继承models.Model
class UserInfo(models.Model):
    #id = models.AutoField()
    username = models.CharField(max_length=50,unique=True)
    passwd = models.CharField(max_length=32)
    qq = models.IntegerField()




