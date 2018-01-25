from django.urls import path
from . import views

app_name = 'taxiapp'

urlpatterns = [
	path('home/', views.home, name="home"),

]
