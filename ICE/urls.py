from django.urls import path

from . import views

urlpatterns = [
    path('', views.monkeyPageView),
    path('course/', views.courseView)
]