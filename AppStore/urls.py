"""AppStore URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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

    # Main page
    path("",views.login_view,name = 'login'),
    path("login", views.login_view, name='login'),
    path("register", views.register_request, name="register"),
    path("logout", views.logout_request, name= "logout"),
    path("view/<str:id>", views.view, name='view'),
    path("mainpage",views.index,name = "mainpage"),
    path('edit/<str:id>',views.edit, name='edit'),
    path('add',views.add,name = 'add'),
    path('places',views.place_index,name = 'place_view'),
    path("places/<str:id>",views.place_view,name = "places")
]
