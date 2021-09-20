"""myproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from myapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sample/', views.sample),
    path('dashboard/',views.dashboard),
    path('',views.entry,name="entry"),
    path('ajax-load/', views.load_charts, name='ajax_load'),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path('load-expiry/', views.ajax_load_expiry, name='ajax_load_expiry'),
    path('load-optionChain/', views.ajax_optionChain, name='ajax_optionChain'),
    path('load-equity/', views.ajax_equity, name='ajax_equity'),
    path('selected-equity/', views.selected_equity, name='selected_equity'),
    path('main/', views.mainView, name='mainView'),
    path('notification1/', views.ajaxNot1, name='ajaxNot1'),
    path('notification2/', views.ajaxNot2, name='ajaxNot2'),
    path('OptionChainSingle/', views.load_optionChain, name='load_optionChain'),
]

