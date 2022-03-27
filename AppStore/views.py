from curses import resetty
from unittest import result
from django.shortcuts import render, redirect
from django.db import connection
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth import login as auth_login
from .forms import NewUserForm
from django.contrib.auth.forms import AuthenticationForm #add this


def index(request):
    """Shows the main page"""

    ## Delete customer
    if request.POST:
        if request.POST['action'] == 'delete':
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM users WHERE user_id = %s", [request.POST['id']])

    ## Use raw query to get all objects
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users ORDER BY user_id")
        users = cursor.fetchall()

    result_dict = {'records': users}

    return render(request,'index.html',result_dict)

# Create your views here.
def view(request, id):
    """Shows the main page"""
    
    ## Use raw query to get a user 
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE user_id = %s", [id])
        user = cursor.fetchone()
    result_dict = {'user': user}

    return render(request,'view.html',result_dict)

# Create your views here.
def add(request):
    """Shows the main page"""
    context = {}
    status = ''

    if request.POST:
        ## Check if customerid is already in the table
        with connection.cursor() as cursor:

            cursor.execute("SELECT * FROM users WHERE user_id = %s", [request.POST['user_id']])
            customer = cursor.fetchone()
            ## No customer with same id
            if customer == None:
                ##TODO: date validation
                cursor.execute("INSERT INTO users VALUES (%s, %s, %s)"
                        , [request.POST['user_id'], request.POST['email'], request.POST['password']
                            ])
                return redirect('mainpage')    
            else:
                status = 'USER with ID %s already exists' % (request.POST['user_id'])


    context['status'] = status
 
    return render(request, "add.html", context)

# Create your views here.
def edit(request, id):
    """Shows the main page"""

    # dictionary for initial data with
    # field names as keys
    context ={}

    # fetch the object related to passed id
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE user_id = %s", [id])
        obj = cursor.fetchone()

    status = ''
    # save the data from the form

    if request.POST:
        ##TODO: date validation
        with connection.cursor() as cursor:
            cursor.execute("UPDATE users SET user_id = %s, email = %s, password = %s WHERE user_id = %s"
                    , [request.POST['user_id'], request.POST['email'],
                        request.POST['password'], id ])
            status = 'Users edited successfully!'
            cursor.execute("SELECT * FROM users WHERE user_id = %s", [id])
            obj = cursor.fetchone()


    context["obj"] = obj
    context["status"] = status
 
    return render(request, "edit.html", context)



def login_view(request):
	if request.method == "POST":
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None:
				auth_login(request, user)
				messages.info(request, f"You are now logged in as {username}.")
				return redirect("mainpage")
			else:
				messages.error(request,"Invalid username or password.")
		else:
			messages.error(request,"Invalid username or password.")
	form = AuthenticationForm()
	return render(request=request, template_name="login.html", context={"login_form":form})




def register_request(request):
	if request.method == "POST":
		form = NewUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			auth_login(request, user)
			messages.success(request, "Registration successful." )
			return redirect("mainpage")
		messages.error(request, "Unsuccessful registration. Invalid information.")
	form = NewUserForm()
	return render (request=request, template_name="register.html", context={"register_form":form})

def mainpage(request):
	return render(request=request, template_name='mainpage.html')

def logout_request(request):
	logout(request)
	messages.info(request, "You have successfully logged out.") 
	return redirect("login")


def place_index(request):
    # show the place page 
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM place ORDER BY address")
        places = cursor.fetchall()
    
    result_dict = {'records':places}
    return render(request,'places.html',result_dict)


def place_view(request,id): 
    # find info for a specific place 
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM place WHERE address = %s",[id])
        place = cursor.fetchone()
    
    result_dict = {'place':place}
    return render(request,'place_view.html',result_dict)



def print_reviews(request,id):
    # print all reviews of  a particular place 
    with connection.cursor() as cursor:
        query = """SELECT p.address,r.booking_id,r.review,r.rating 
        FROM bookings b,reviews r,place p 
        WHERE b.booking_id = r.booking_id AND b.place_id = p.address 
        GROUP BY p.address,r.booking_id,r.review,r.rating 
        HAVING p.address = %s
        """
        cursor.execute(query,[id])
        review = cursor.fetchall()
        result_dict = {'records':review}
        return render(request,'review_view.html',result_dict)



def print_best_places(request): 
    # print addresses with highest average rating in each city 
    # if there a city where none of the places are booked 
    # assign null to address and 0 to average_rating 
    with connection.cursor() as cursor:
        query = """SELECT p.address,p.city_id,p.country_id,ROUND(AVG(r.rating),2) AS average_rating 
        FROM place p,bookings b,reviews r 
        WHERE p.address = b.place_id AND b.booking_id = r.booking_id 
        GROUP BY p.address,p.city_id,p.country_id 
        HAVING AVG(r.rating) >= ALL(
            SELECT AVG(r1.rating)
            FROM place p1,bookings b1,reviews r1 
            WHERE p1.address = b1.place_id AND b1.booking_id = r1.booking_id AND 
            p.country_id = p1.country_id 
            GROUP BY p1.address)
        UNION
        SELECT NULL AS address,c.name,c.country,0 AS average_rating
        FROM cities c 
        LEFT JOIN (SELECT p.city_id,p.country_id
        FROM bookings b,place p 
        WHERE b.place_id = p.address) AS temp ON temp.city_id = c.name AND temp.country_id = c.country
        WHERE temp.city_id ISNULL 
        ORDER BY average_rating DESC
        """

        cursor.execute(query)
        best_places = cursor.fetchall()

    
    
    result_dict = {'records':best_places}
    return render(request,'Bestplaces.html',result_dict)

    
