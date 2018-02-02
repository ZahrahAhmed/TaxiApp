from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserForm, RestaurantForm, UserFormForEdit, MealForm, UserLogin
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Meal
from django.contrib import messages

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
    return render(request, 'order.html', {})

@login_required(login_url='/restaurant/login/')
def restaurant_report(request):
    return render(request, 'report.html', {})

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
