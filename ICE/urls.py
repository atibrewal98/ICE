from django.urls import path
from django.conf.urls import url, include

from . import views

urlpatterns = [
    # path('', views.monkeyPageView),
    #url(r'^learnerCourse/courseID=(?P<course_ID>[0-9]+)&learnerID=(?P<learner_ID>[0-9]+)/$',views.learnerCourseView),
    #url(r'^instructorCourse/courseID=(?P<course_ID>[0-9]+)/$',views.instructorCourseView),
    url(r'^learnerCourse/learnerID=(?P<learner_ID>[0-9]+)&courseID=(?P<course_ID>[0-9]+)&moduleID=(?P<module_ID>[0-9]+)/$',views.learnerModuleCourseView),
    url(r'^instructorCourse/instructorID=(?P<instructor_ID>[0-9]+)&courseID=(?P<course_ID>[0-9]+)&moduleID=(?P<module_ID>[0-9]+)/$',views.instructorCourseModuleView),
    url(r'^moduleQuiz/(?P<id>[0-9]+)/$', views.intructor_view_quiz),
    path('category/', views.category_list_view),
    path('modules/', views.module_list_view),
    url(r'^addModule/instructorID=(?P<instructor_id>[0-9]+)&courseID=(?P<course_id>[0-9]+)/$', views.module_form),
    url(r'^addModuleQuiz/(?P<id>[0-9]+)/$',views.quiz_form),
    url(r'^addComponent/instructorID=(?P<instructor_id>[0-9]+)&moduleID=(?P<module_id>[0-9]+)/',views.component_form),
    path('comp/', views.component),
    url(r'^modules_component/(?P<module_ID>[0-9]+)/$',views.component_list_view),
    url(r'^dashboard/learnerID=(?P<learner_ID>[0-9]+)/$',views.course_learner_view, name="course_learner"),
    url(r'^instructorDashboard/instructorID=(?P<instructor_id>[0-9]+)/$',views.course_instructor_view, name="course_instructor"),
    url(r'^quizform/$', views.some_view),
    path('accounts/', include('django.contrib.auth.urls')),
    url(r'login_success/$', views.login_success, name='login_success')
	# url(r'^register/$', views.UserFormView.as_view(), name='register')
    #path('invite/', views.invite, name='invite'),
    #path('signup/<uidb64>/<token>', views.signup, name='signup'),

]