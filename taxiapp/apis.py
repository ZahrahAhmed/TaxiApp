from django.http import JsonResponse
from .models import Restaurant, Meal, Order, OrderDetails, Driver
from .serializers import RestaurantSerializer, MealSerializer, OrderSerializer
from django.utils import timezone
import json
from datetime import timedelta
from oauth2_provider.models import AccessToken
from django.views.decorators.csrf import csrf_exempt

def customer_get_restaurants(request):
    restaurants = RestaurantSerializer(
        Restaurant.objects.all().order_by("-id"),
        many = True,
        context = {"request": request}
    ).data

    return JsonResponse({"restaurants": restaurants})

def customer_get_meals(request, restaurant_id):
    meals = MealSerializer(
        Meal.objects.filter(restaurant_id = restaurant_id).order_by("-id"),
        many = True,
        context = {"request": request},
    ).data

    return JsonResponse({"meals": meals})

@csrf_exempt
def customer_add_order(request):
    if request.method == "POST":
        access_token = AccessToken.objects.get(token = request.POST.get("access_token"),  expires__gt = timezone.now())

        customer = access_token.user.customer

        # Check whether customer has any order that is not delivered
        if Order.objects.filter(customer = customer).exclude(status = Order.DELIVERED):
            return JsonResponse({"status": "failed", "error": "Your last order must be completed."})

        # Check Address
        if not request.POST["address"]:
            return JsonResponse({"status": "failed", "error": "Address is required."})

        # Get Order Details
        order_details = json.loads(request.POST["order_details"])

        order_total = 0
        for meal in order_details:
            order_total += Meal.objects.get(id = meal["meal_id"]).price * meal["quantity"]
            if len(order_details) > 0:
                order = Order.objects.create(
                    customer = customer,
                    restaurant_id = request.POST["restaurant_id"],
                    total = order_total,
                    status = Order.COOKING,
                    address = request.POST["address"],
                )

                for meal in order_details:
                    OrderDetails.objects.create(
                        order = order,
                        meal_id = meal["meal_id"],
                        quantity = meal["quantity"],
                        sub_total = Meal.objects.get(id = meal["meal_id"]).price * meal["quantity"],
                    )
                return JsonResponse({"status": "success"})

def customer_get_latest_order(request):
    access_token = AccessToken.objects.get(token = request.GET.get("access_token"),  expires__gt = timezone.now())
    customer = access_token.user.customer
    order = OrderSerializer(Order.objects.filter(customer = customer).last()).data

    return JsonResponse({"order": order})

def customer_driver_location(request):
    access_token = AccessToken.objects.get(token = request.GET.get("access_token"),
        expires__gt = timezone.now())

    customer = access_token.user.customer

    #Get drivers location realted to this customer current order
    current_order = Order.objects.filter(customer = customer, status = Order.ONTHEWAY).last()
    location = current_order.driver.location

    return JsonResponse({"location": location})



def restaurant_order_notification(request, lrt):
    notification = Order.objects.filter(restaurant = request.user.restaurant, created_at__gt = lrt).count()
    return JsonResponse({"notification": notification})

def driver_get_ready_orders(request):
    orders = OrderSerializer(
        Order.objects.filter(status = Order.READY, driver = None).order_by("-id"),
        many = True
    ).data
    return JsonResponse({"orders": orders})

@csrf_exempt
def driver_pick_orders(request):
    if request.method == "POST":
        access_token = AccessToken.objects.get(token = request.POST.get("access_token"),  expires__gt = timezone.now())
        driver = access_token.user.driver

        if Order.objects.filter(driver = driver).exclude(status= Order.ONTHEWAY):
            return JsonResponse({"status": "failed", "error": "You can only pick one order at the same time"})

        try:
            order = Order.objects.get(
                id = request.POST["order_id"],
                driver = None,
                status = Order.READY
            )
            order.driver = driver
            order.status = Order.ONTHEWAY
            order.picked_at = timezone.now()
            order.save()

            return JsonResponse({"status": "success"})

        except Order.DoesNotExist:
            return JsonResponse({"status": "failed", "error": "This order has been picked up by another driver"})

    return JsonResponse({})

def driver_get_latest_orders(request):
    access_token = AccessToken.objects.get(token = request.GET.get("access_token"),  expires__gt = timezone.now())

    driver = access_token.user.driver
    order = OrderSerializer(
        Order.objects.filter(driver= driver).order_by("picked_at").last()
    ).data

    return JsonResponse({"order":order})

@csrf_exempt
def driver_complete_orders(request):
    access_token = AccessToken.objects.get(token = request.POST.get("access_token"),  expires__gt = timezone.now())
    driver = access_token.user.driver
    order = Order.objects.get(id= request.POST['order_id'], driver= driver)
    order.status = Order.DELIVERED
    order.save()

    return JsonResponse({"status": "success"})

def driver_get_revenue(request):
    access_token = AccessToken.objects.get(token = request.GET.get("access_token"),  expires__gt = timezone.now())

    driver = access_token.user.driver

    revenue = {}
    today = timezone.now()
    current_weekdays = [today + timedelta(days = i) for i in range(0 - today.weekday(), 7 - today.weekday())]

    for day in current_weekdays:
        orders = Order.objects.filter(
            driver= driver,
            status = Order.DELIVERED,
            created_at__year = day.year,
            created_at__month = day.month,
            created_at__day = day.day

        )

        revenue[day.strftime("%a")] = sum(order.total for order in orders)

    return JsonResponse({"revenue": revenue})

@csrf_exempt
def driver_update_location(request):
    if request.method == "POST":

        access_token = AccessToken.objects.get(token = request.POST.get("access_token"),
            expires__gt = timezone.now())

        driver = access_token.user.driver

        #SET location string => database
        driver.location = request.POST["location"]
        driver.save()

        return JsonResponse({"status": "success"})
