from django.urls import path
from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^learnerCourse/courseID=(?P<course_ID>[0-9]+)&moduleID=(?P<module_ID>[0-9]+)/$',views.learnerModuleCourseView),
    url(r'^instructorCourse/courseID=(?P<course_ID>[0-9]+)&moduleID=(?P<module_ID>[0-9]+)/$',views.instructorCourseModuleView),
    url(r'^liveCourse/courseID=(?P<course_ID>[0-9]+)/$',views.liveCourseView),
    url(r'^moduleQuiz/(?P<id>[0-9]+)/$', views.intructor_view_quiz),
    url(r'category/categoryID=(?P<category_id>[0-9]+)/$', views.category_list_view),
    url(r'^courseDescription/courseID=(?P<course_id>[0-9]+)/$', views.courseDescriptionView),
    url(r'^addCourse/$', views.course_form),
    url(r'^addModule/courseID=(?P<course_id>[0-9]+)/$', views.module_form),
    url(r'^editModule/moduleID=(?P<module_id>[0-9]+)/$', views.edit_module_form),
    # url(r'^addModuleQuiz/(?P<id>[0-9]+)/$',views.quiz_form),
    # url(r'^addComponent/moduleID=(?P<module_id>[0-9]+)/',views.component_form),
    url(r'^importComponent/moduleID=(?P<module_id>[0-9]+)/',views.import_component_form),
    url(r'^importQuiz/moduleID=(?P<module_ID>[0-9]+)/',views.import_quiz),
    url(r'^dashboard/$',views.course_learner_view, name="course_learner"),
    url(r'^history/$',views.course_history_view, name="history"),
    url(r'^instructorDashboard/$',views.course_instructor_view, name="course_instructor"),
    url(r'^underDevelopment/$',views.course_development_view, name="development"),
    url(r'^quiz/moduleID=(?P<module_ID>[0-9]+)$', views.learner_quiz),
    url(r'accounts/', include('django.contrib.auth.urls')),
    url(r'login_success/$', views.login_success, name='login_success'),
    url(r'invite/', views.invite, name='invite'), #for admin to invite instructors
    url(r'learner_get_token/', views.learner_get_token, name='learner_get_token'), #for learner to get token
    path('signup/<uidb64>/<token>', views.signup, name='signup'),
]