from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    path('', views.monkeyPageView),
    path('course/', views.courseView),
    path('category/', views.category_list_view),
    path('modules/', views.module_list_view),
    url(r'^modules_component/(?P<module_ID>[0-9]+)/$',views.component_list_view)
]