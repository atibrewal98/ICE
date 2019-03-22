from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    path('', views.monkeyPageView),
    path('course/', views.courseView),
    path('modules/', views.ModuleViewAll.as_view(), name='module'),
    path('modules_component/<int:moduleID>', views.ModuleViewComponents.as_view(), name='module-list'),
    path('category/', views.category_list_view),
    path('modules1/', views.module_list_view),
    # path("modules_component1/$", views.component_list_view),
    url(r'^modules_component1/(?P<module_ID>[0-9]+)/$',views.component_list_view)
]