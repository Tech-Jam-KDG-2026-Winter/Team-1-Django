from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('diary/write/', views.diary_write, name='diary_write'),
    path('diary/<int:pk>/', views.DiaryDetailView.as_view(), name='diary_detail'),
    path('topic/', views.daily_topic, name='daily_topic'),
    path('setting/', views.SettingUpdateView.as_view(), name='setting'),
    path('signup/', views.user_create, name='user_create'),
]