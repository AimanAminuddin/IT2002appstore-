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
# adsadsad

urlpatterns = [
    path('admin/', admin.site.urls),

    # Main page
    path("",views.login_request,name = 'login'),  
    path("login", views.login_request, name='login'), 
    path("register", views.add, name="register"),
    path("logout", views.logout_request, name= "logout"),
    path("view/<str:id>", views.view, name='view'),
    path("mainpage",views.index,name = "mainpage"),
    path('edit/<str:id>',views.edit, name='edit'),
    path('add',views.add,name = 'add'),
    path('places',views.place_index,name = 'places'),
    path("place_view/<str:id>",views.place_view,name = "place_view"),
    path("reviews/<str:id>",views.print_reviews,name = "place_review"),
    path("bestplaces",views.print_best_places,name = "bestplaces"),
    path("schedule/<str:id>",views.place_schedule,name = "schedule"),
    path("booking",views.place_booking,name = "booking"),
    path('review',views.leave_a_review,name = "review")
]
