"""
URL configuration for osscheduler project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.template, name='template'),

    path('api/fcfs/', views.fcfs_view, name='fcfs'),
    path('api/sjf/', views.sjf_view, name='sjf'),
    path('api/ljf/', views.ljf_view, name='ljf'),
    path('api/lrtf/', views.lrtf_view, name='lrtf'),
    path('api/priority/',views.priority_view, name='priority'),
    path('api/srtf/', views.srtf_view, name='srtf'),

    
    path('api/fcfs/', views.fcfs_visualization_view, name='fcfs'),
    path('api/sjf/', views.sjf_visualization_view, name='sjf'),
    path('api/ljf/', views.ljf_visualization_view, name='ljf'),

    path('api/srtf/', views.srtf_visualization_view, name='srtf'),
    path('api/lrtf/', views.lrtf_visualization_view, name='lrtf'),

    path('api/priority/', views.priority_visualization_view, name='priority'),
    path('api/prtf/', views.prtf_visualization_view, name='prtf'),
]
