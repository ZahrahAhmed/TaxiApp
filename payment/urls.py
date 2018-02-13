from . import views
from django.urls import path
app_name='payment'

urlpatterns = [
    path('pay/<int:order_id>/', views.pay, name='pay'),
    path('unsuccessful_payment/', views.unsuccessful_payment, name='unsuccessful_payment'),
    ]
