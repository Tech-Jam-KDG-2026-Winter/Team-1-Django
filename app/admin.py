from django.contrib import admin
from .models import UserProfile, Diary, DailyThread, ThreadComment

class DailyThreadAdmin(admin.ModelAdmin):
    list_display = ('date', 'title')
    ordering = ('-date',)

class DiaryAdmin(admin.ModelAdmin):
    list_display = ('date', 'user', 'updated_at')
    list_filter = ('user', 'date')
    ordering = ('-date',)

admin.site.register(UserProfile)
admin.site.register(Diary, DiaryAdmin)
admin.site.register(DailyThread, DailyThreadAdmin)
admin.site.register(ThreadComment)