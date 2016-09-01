"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from cmdb import views
from article import views as article

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^index/', views.index),
    url(r'^login/', views.login),
    url(r'^regist/', views.regist),
    url(r'^services/', views.services),
    url(r'^demo/', views.demo),
    url(r'^blog/', article.demo),
    url(r'^$', views.login,name='home'),
    url(r'^home/', article.home),
    # url(r'^(?P<my_args>\d+)/$',article.detail,name='detail'),
    url(r'^(?P<id>\d+)/$', article.detail, name='detail'),
]


