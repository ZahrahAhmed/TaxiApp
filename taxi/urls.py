from django.conf.urls import include
from django.urls import path
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings
from taxiapp import views, apis

urlpatterns = [
    path('api/social/', include('rest_framework_social_oauth2.urls')),

    path('admin/', admin.site.urls),
    path('home/', views.home, name='home'),

    # Restaurant
    path('restaurant/login/', views.restaurant_login, name="login"),
    path('restaurant/logout/', views.restaurant_logout, name="logout"),
    path('restaurant/signup/', views.restaurant_signup, name="signup"),

    path('restaurant/home/', views.restaurant_home, name="restaurant_home"),

    path('restaurant/account/', views.restaurant_account, name="restaurant_account"),
    path('restaurant/meal/', views.restaurant_meal, name="restaurant_meal"),
    path('restaurant/meal/add/', views.add_meal, name="add_meal"),
    path('restaurant/meal/edit/<int:meal_id>/', views.edit_meal, name="edit_meal"),
    path('restaurant/order/', views.restaurant_order, name="restaurant_order"),

    path('api/restaurant/order/notification/<str:lrt>/', apis.restaurant_order_notification),

    path('restaurant/report/', views.restaurant_report, name="restaurant_report"),

    # APIs for CUSTOMERS
    path('api/customer/restaurants/', apis.customer_get_restaurants),
    path('api/customer/meals/<int:restaurant_id>/', apis.customer_get_meals),
    path('api/customer/order/add/', apis.customer_add_order),
    path('api/customer/order/latest/', apis.customer_get_latest_order),
    path('api/customer/driver/location/', apis.customer_driver_location),

     #APIs for Drivers
    path('api/driver/orders/ready/', apis.driver_get_ready_orders),
    path('api/driver/order/pick/', apis.driver_pick_orders),
    path('api/driver/order/latest/', apis.driver_get_latest_orders),
    path('api/driver/order/complete/', apis.driver_complete_orders),
    path('api/driver/order/revenue/', apis.driver_get_revenue),
    path('api/driver/location/update/', apis.driver_update_location),
]
if settings.DEBUG:
    urlpatterns+=static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
