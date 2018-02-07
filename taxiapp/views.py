from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserForm, RestaurantForm, UserFormForEdit, MealForm, UserLogin
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Meal, Order, Driver
from django.contrib import messages
from datetime import timedelta, datetime
from django.db.models import Sum, Count, Case, When

def home(request):
    return render(request, 'home.html', {})

@login_required(login_url='/restaurant/login/')
def restaurant_home(request):
    return render(request, 'restaurant.html', {})
@login_required(login_url='/restaurant/login/')
def restaurant_account(request):
    form = UserFormForEdit(instance = request.user)
    restaurant_form = RestaurantForm(instance = request.user.restaurant)

    if request.method == "POST":
        form = UserFormForEdit(request.POST, instance = request.user)
        restaurant_form = RestaurantForm(request.POST, request.FILES, instance = request.user.restaurant)

        if form.is_valid() and restaurant_form.is_valid():
            form.save()
            restaurant_form.save()

    return render(request, 'resaccount.html', {
        "form": form,
        "restaurant_form": restaurant_form
    })

@login_required(login_url='/restaurant/login/')
def restaurant_meal(request):
    meals = Meal.objects.filter(restaurant = request.user.restaurant).order_by("-id")
    return render(request, 'meal.html', {"meals": meals})

@login_required(login_url='/restaurant/login/')
def add_meal(request):
    form = MealForm()

    if request.method == "POST":
        form = MealForm(request.POST, request.FILES)

        if form.is_valid():
            meal = form.save(commit=False)
            meal.restaurant = request.user.restaurant
            meal.save()
            return redirect(restaurant_meal)

    return render(request, 'addmeal.html', {
        "form": form
    })

@login_required(login_url='/restaurant/login/')
def edit_meal(request, meal_id):
    form = MealForm(instance = Meal.objects.get(id = meal_id))

    if request.method == "POST":
        form = MealForm(request.POST, request.FILES, instance = Meal.objects.get(id = meal_id))

        if form.is_valid():
            form.save()
            return redirect(restaurant_meal)

    return render(request, 'editmeal.html', {
        "form": form
    })


@login_required(login_url='/restaurant/login/')
def restaurant_order(request):
    if request.method == "POST":
        order = Order.objects.get(id = request.POST['id'], restaurant= request.user.restaurant)
        if order.status == Order.COOKING:
            order.status = Order.READY
            order.save()

    orders = Order.objects.filter(restaurant = request.user.restaurant).order_by("-id")
    return render(request, 'order.html', {"orders": orders,})

@login_required(login_url='/restaurant/login/')
def restaurant_report(request):
    revenue = []
    orders = []

    today = datetime.now()
    current_weekdays = [today + timedelta(days = i) for i in range(0 - today.weekday(), 7 - today.weekday())]

    for day in current_weekdays:
        deliveredorders = Order.objects.filter(
            restaurant= request.user.restaurant,
            status = Order.DELIVERED,
            created_at__year = day.year,
            created_at__month = day.month,
            created_at__day = day.day

        )
        revenue.append(sum(order.total for order in deliveredorders))
        orders.append(deliveredorders.count())

    top3meals = Meal.objects.filter(restaurant= request.user.restaurant).annotate(total_order= Sum('orderdetails__quantity')).order_by("-total_order")[:3]
    meal = {
        "labels": [meal.name for meal in top3meals],
        "data": [meal.total_order or 0 for meal in top3meals],
    }
    top3drivers = Driver.objects.annotate(
        total_order = Count(
            Case(
                When(order__restaurant = request.user.restaurant, then = 1)
            )
        )
    ).order_by("-total_order")[:3]
    driver = {
        "labels": [driver.user.get_full_name() for driver in top3drivers],
        "data": [driver.total_order for driver in top3drivers],
    }
    return render(request, 'report.html', {
        "revenue": revenue,
        "orders": orders,
        "meal": meal,
        "driver": driver,
    })

def restaurant_signup(request):
    form = UserForm()
    restaurant_form = RestaurantForm()

    if request.method == "POST":
        form = UserForm(request.POST)
        restaurant_form = RestaurantForm(request.POST, request.FILES)

        if form.is_valid() and restaurant_form.is_valid():
            new_user = User.objects.create_user(**form.cleaned_data)
            new_restaurant = restaurant_form.save(commit=False)
            new_restaurant.user = new_user
            new_restaurant.save()

            login(request, authenticate(
                username = form.cleaned_data["username"],
                password = form.cleaned_data["password"]
            ))

            return redirect(restaurant_home)

    return render(request, "res_signup.html", {
        "form": form,
        "restaurant_form": restaurant_form
    })

def restaurant_login(request):
	form = UserLogin()
	context = {"form": form, }
	if request.method=="POST":
		form = UserLogin(request.POST)
		if form.is_valid():
			username = form.cleaned_data['username']
			password = form.cleaned_data['password']

			auth = authenticate(username=username, password=password)

			if auth is not None:
				login(request, auth)
				return redirect("restaurant_home")
			else:
				messages.warning(request, 'Incorrect UserName/Password combination.')
				return redirect("login")
		else:
			messages.warning(request, form.errors)
			return redirect("login")

	return render(request,"res_login.html", context)

def restaurant_logout(request):
	logout(request)
	return redirect("home")
