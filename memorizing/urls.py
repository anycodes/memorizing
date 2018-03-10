"""memorizing URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
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
from english.views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^writeinfo', writeinfo),
    url(r'^index', index),
    url(r'^about', aboutus),
    url(r'^writeresult', writeresult),
    url(r'^userinfo', infoview),
    url(r'^catlist_one', catlist_one),
    url(r'^catlist_two', catlist_two),
    url(r'^beisong', memoword_list),
    url(r'^beistz', memoword_tz),
    # url(r'^djcatlist', djcatlist),
    url(r'^looklist', wordlist),
    url(r'^modle_1_question', memoword_mo_one),
    url(r'^modle_1_result', word_result_one),
    url(r'^modle_2_question', memoword_mo_two),
    url(r'^modle_2_result', word_result_two),
    url(r'^modle_3_question', memoword_mo_three),
    url(r'^modle_3_result', word_result_three),
    url(r'^history', history),
    url(r'^wrong', wrong),
    url(r'^test', translation),
    url(r'^picpage',picpage),
    url(r'^help',help),
    url(r'^$',index),
    url(r'^get_from_wechat',getChat),
    url(r'^gengxincaidan', gengxincaidan),
    url(r'^piliang', piliang),
    url(r'^fankui', fankui),
]
