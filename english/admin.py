from django.contrib import admin
from english.models import *

# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ('userid','username','password','sex','email')
    list_display_links = ('userid','username','password','sex','email')

class CatagoryAdmin(admin.ModelAdmin):
    list_display = ('catid','name','first','second','third','forth')
    list_display_links = ('catid','name',)
    list_editable = ('first','second','third','forth')

class WordAdmin(admin.ModelAdmin):
    list_display = ('wordid', 'word','mean_en','mean_zh')
    list_display_links = ('wordid',)
    list_editable = ('word',)

class HistoryAdmin(admin.ModelAdmin):
    list_display = ('hisid', 'user', 'grade', 'date',)
    list_display_links = ('hisid', 'user')

class WrongAdmin(admin.ModelAdmin):
    list_display = ('wrongid', 'user', 'word', 'date', 'times')
    list_display_links = ('wrongid', 'user', 'word', 'date',)

admin.site.register(User,UserAdmin)
admin.site.register(Catagory,CatagoryAdmin)
admin.site.register(Word,WordAdmin)
admin.site.register(History,HistoryAdmin)
admin.site.register(Wrong,WrongAdmin)

