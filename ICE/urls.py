from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    path('', views.monkeyPageView),
    url(r'^learnerCourse/courseID=(?P<course_ID>[0-9]+)&learnerID=(?P<learner_ID>[0-9]+)&moduleID=(?P<module_ID>[0-9]+)/$',views.learnerCourseView),
    url(r'^instructorCourse/courseID=(?P<course_ID>[0-9]+)&moduleID=(?P<module_ID>[0-9]+)/$',views.instructorCourseView),
    path('category/', views.category_list_view),
    path('modules/', views.module_list_view),
    url(r'^addModule/(?P<id>[0-9]+)/$', views.module_form),
    url(r'^addModuleQuiz/(?P<id>[0-9]+)/$',views.quiz_form),
    path('component/',views.component_form),
    path('comp/', views.component),
    url(r'^modules_component/(?P<module_ID>[0-9]+)/$',views.component_list_view)
]