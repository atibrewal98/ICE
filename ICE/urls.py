from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    path('', views.monkeyPageView),
    path('course/', views.courseView),
    url(r'^course/(?P<course_ID>[0-9]+)/(?P<learner_ID>[0-9]+)/(?P<module_ID>[0-9]+)/$',views.courseView),
    path('category/', views.category_list_view),
    path('modules/', views.module_list_view),
    path('postmodule/', views.module_form),
    url(r'^module/(?P<id>[0-9]+)/$',views.quiz_form),
    url(r'^modules_component/(?P<module_ID>[0-9]+)/$',views.component_list_view)
]