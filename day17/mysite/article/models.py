from django.db import models

# Create your models here.
class Article(models.Model):
    '''
    title: 题目
    category: 标签
    date_time: 创建日期, 自动创建
    content: 博客正文
    '''
    title = models.CharField(max_length=100)
    category = models.CharField(max_length=50, blank=True)
    date_time = models.DateTimeField(auto_now_add=True)
    content = models.TextField(blank=True, null=True)

    def __str__(self):
        '''通过这个函数可以告诉系统使用title字段来表示这个对象'''
        return self.title

    class Meta:
        '''按时间下降顺序'''
        ordering = ['-date_time']