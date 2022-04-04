from curses import resetty
from unittest import result
from django.shortcuts import render, redirect
from django.db import connection
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import login as auth_login
from .forms import NewUserForm
from django.contrib.auth.forms import AuthenticationForm #add this
from django.urls import reverse
import datetime 

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
                status = 'Successfully Create a New Account!'
                context['status'] = status 
                return render(request,"add.html",context)   
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

def login_request(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username == 'admin' and password == 'alibaba123':
            return HttpResponseRedirect(reverse("mainpage"))
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT user_id,password FROM users WHERE user_id =%s AND password =%s",
                           [username,password])
            information = cursor.fetchone()
            
            if information is None:
                messages.error(request,"Invalid username or password.")
            
            # user already signed up 
            else:
                user_id = information[0]
                password = information[1]
                messages.info(request, f"You are now logged in as {user_id}.")
                return HttpResponseRedirect(reverse("places"))

    form = AuthenticationForm()
    return render(request=request, template_name="login.html", context={"login_form":form})



def register_view(request):
    context = {}
    status = ''
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get("email")
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        if password != password2:
            status = 'Password mismatch'
            context['status'] = status
            return render(request,"template.html",context)
            
        elif len(password) < 8:
            status = "Password should be at least 8 characters"
            context['status'] = status
            return render(request,"template.html",context)
        
        else:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE user_id = %s",[username])
                information1 = cursor.fetchone()
                if information1 is not None: 
                    # sombody has used up the username 
                    status = "User already exists!"
                    context['status'] = status
                    return render(request,"template.html",context)
                else:
                    cursor.execute("SELECT * FROM users WHERE email = %s",[email])
                    information2 = cursor.fetchone()
                    
                    if information2 is not None:
                        # sombody has used this email 
                        status = "Email has already been taken!"
                        context['status'] = status
                        return render(request,"template.html",context)
                    else:
                        # successfully create a new user 
                        cursor.execute("INSERT INTO users VALUES(%s,%s,%s)",[username,email,password])
                        return HttpResponseRedirect(reverse("login"))
    else:
        return render(request,"template.html",context)
    


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

def place_schedule(request,id):
    # find booking schedule for a specific place 
    with connection.cursor() as cursor:
        query = """SELECT u.email AS rentee_email,b.start_date,b.end_date
        FROM place p,bookings b,users u
        WHERE p.address = b.place_id AND b.user_id = u.user_id AND 
        p.address = %s"""
        cursor.execute(query, [id])
        booking = cursor.fetchall()
    
    result_dict = {'records':booking}
    
    return render(request,'schedule.html',result_dict)



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
        query = """
        SELECT p.address,p.city_id,p.country_id,ROUND(AVG(r.rating),2) AS average_rating 
        FROM place p,bookings b,reviews r
        WHERE p.address = b.place_id AND b.booking_id = r.booking_id 
        GROUP BY p.address,p.city_id,p.country_id
        HAVING AVG(r.rating) >= ALL(
            SELECT AVG(r1.rating)
            FROM place p1,bookings b1,reviews r1 
            WHERE p1.address = b1.place_id AND b1.booking_id = r1.booking_id AND 
            p.city_id = p1.city_id AND p.country_id = p1.country_id 
            GROUP BY p1.address)
        ORDER BY average_rating DESC
        """
        cursor.execute(query)
        best_places = cursor.fetchall()

    
    
    result_dict = {'records':best_places}
    return render(request,'Bestplaces.html',result_dict)



def place_booking(request):
    context = {}
    status = ''
    if request.method == "POST":
        
        username = request.POST.get("username")
        password = request.POST.get("password")
        address = request.POST.get("place")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        with connection.cursor() as cursor:
            # check if user or password invalid 
            cursor.execute("SELECT user_id FROM users WHERE user_id =%s",[username])
            user_id = cursor.fetchone()
            cursor.execute("SELECT password FROM users WHERE user_id =%s",[password])
            real_password = cursor.fetchone()
            
            # check if place exists 
            cursor.execute("SELECT address FROM place WHERE address =%s",[address])
            place = cursor.fetchone()
            
            # check if  end date >= start date
            start = start_date.split("-")
            end = end_date.split("-")
            d1 = datetime.date(int(start[0]),int(start[1]),int(start[2]))
            d2 = datetime.date(int(end[0]),int(end[1]),int(end[2]))
            
            # check if there are clashes 
            # just need to check if start date in between another start and end 
            # end date in between start and end date 
            cursor.execute("SELECT start_date,end_date FROM bookings WHERE place_id=%s",[address])
            schedule = cursor.fetchall()
            
            if user_id is None or real_password is None: 
                status = "Invalid Username or Password!"
            
            elif d1 > d2: 
                status = "Start Date cannot be later then End Date!"
            
            elif place is None:
                status = "Place does not Exists!"
            
            else:
                for booking in schedule:
                    # convert to datetime format and make comparison between
                    
                    b1 = booking[0]
                    b2 = booking[1]
                    
                    
                    if (b1 <= d1 and d1 <= b2) or (b1 <= d2 and d2 <= b2):
                        status = "Clash in booking!"
                        break 
                    else:
                        continue 
            
            
            if status == "":
                # insert new booking into booking table 
                # create booking id 
                cursor.execute("SELECT booking_id FROM bookings ORDER BY booking_id DESC LIMIT 1")
                booking_id = cursor.fetchone() 
                booking_id = booking_id[0]
                temp = str(int(booking_id) + 1) 
                cursor.execute("INSERT INTO bookings VALUES(%s, %s, %s,%s,%s)",[temp,username,address,start_date,end_date])
                status = "Booking is successful!"
                context['status'] = status 
                return render(request, "booking.html", context)
            
            else:
                context['status'] = status 
                return render(request,"booking.html",context)
        
    else:
        # no booking was made (refresh page again)
        context['status'] = status 
        return render(request,"booking.html",context)

def leave_a_review(request):
    id = request.POST.get('booking_id')
    rating = request.POST.get('rating')
    review = request.POST.get('review')
    context = {}
    status = ""
    
    if request.method == "POST":
        with connection.cursor() as cursor:
            cursor.execute("SELECT booking_id FROM bookings WHERE booking_id =%s",[id])
            book = cursor.fetchone()
        
            if book is None:
                status = 'Booking does not exist!'
            else:
            # check if user has already made a review 
                cursor.execute("SELECT booking_id FROM reviews WHERE booking_id = %s",[id])
                critic = cursor.fetchone()
            
                if critic is not None:
                # already made booking_id
                    status = 'You already have reviewed this place!'
                else:
                # INSERT INTO review table 
                    cursor.execute("INSERT INTO reviews VALUES(%s,%s,%s)",[id,rating,review])
                    status = "You successfully reviewed this place! Thank you for your time!"
                    context['status'] = status 
                    return render(request,'review.html',context)
        
        context['status'] = status 
        return render(request, 'review.html',context)
    else:
        context['status'] = status 
        return render(request, 'review.html',context)
    

def host_index(request):
    # Delete host index
    if request.POST:
        if request.POST['action'] == 'delete':
            with connection.cursor() as cursor:
                cursor.execute('DELETE FROM hosts WHERE host_id =%s',[request.POST['id']])
    
    ## Use raw query to get all objects in the database 
    with connection.cursor() as cursor:
        query = """SELECT t.host_id,u.email,SUM(t.revenue) AS total_revenue
        FROM 
        (SELECT h.host_id,p.address,p.city_id,p.country_id,SUM(p.price_per_night * (b.end_date-b.start_date+1)) 
        AS revenue
        FROM hosts h,place p,bookings b
        WHERE h.host_id = p.host_id AND p.address = b.place_id
        GROUP BY h.host_id,p.address,p.city_id,p.country_id
        UNION
        SELECT h.host_id,p.address,p.city_id,p.country_id,0 AS revenue 
        FROM hosts h,place p
        WHERE h.host_id = p.host_id AND p.address 
        NOT IN (SELECT p.address FROM bookings b,place p WHERE b.place_id = p.address)
        ORDER BY revenue DESC) AS t,users u 
        WHERE u.user_id = t.host_id
        GROUP BY t.host_id,u.email
        ORDER BY total_revenue DESC
        """
        cursor.execute(query)
        host = cursor.fetchall()
    
    result_dict ={'records':host}
    
    return render(request,'hosts.html',result_dict)


def host_view(request,id):
    with connection.cursor() as cursor:
        query = """SELECT t.host_id,u.email,SUM(t.revenue) AS total_revenue
        FROM 
        (SELECT h.host_id,p.address,p.city_id,p.country_id,SUM(p.price_per_night * (b.end_date-b.start_date+1)) 
        AS revenue
        FROM hosts h,place p,bookings b
        WHERE h.host_id = p.host_id AND p.address = b.place_id
        GROUP BY h.host_id,p.address,p.city_id,p.country_id
        UNION
        SELECT h.host_id,p.address,p.city_id,p.country_id,0 AS revenue 
        FROM hosts h,place p
        WHERE h.host_id = p.host_id AND p.address 
        NOT IN (SELECT p.address FROM bookings b,place p WHERE b.place_id = p.address)
        ORDER BY revenue DESC) AS t,users u 
        WHERE u.user_id = t.host_id
        GROUP BY t.host_id,u.email
        HAVING t.host_id =%s
        """
        cursor.execute(query,[id])
        host = cursor.fetchone()
        result_dict = {'host':host}
    
    return render(request, 'host_view.html',result_dict) 


def add_hosts(request):
    context = {}
    status = ''
    
    if request.POST:
        with connection.cursor() as cursor:
            user = request.POST.get('user_id')
            cursor.execute("SELECT * FROM users WHERE user_id = %s",[user])
            user_id = cursor.fetchone()
            
            if user_id is None:
                status = 'You can only add hosts from current users'
            else:
                # check if hosts already exists in the database
                cursor.execute("SELECT * FROM hosts WHERE host_id=%s",[user])
                host_id = cursor.fetchone()
                if host_id is not None:
                    status = 'User is already a host!'
                else:
                    status = 'New Host added successfully!'
                    context['status'] = status 
                    # insert into host table  
                    cursor.execute("INSERT INTO hosts VALUES(%s)",[user])
                    return render(request, 'addhost.html',context)
            
            context['status'] = status 
            
            return render(request, 'addhost.html',context)
    
    else:
        return render(request, 'addhost.html',context)


def add_places(request):
    context = {} 
    status = ''
    if request.POST:
        host = request.POST.get('host_id')
        place = request.POST.get('address')
        city = request.POST.get('city')
        country = request.POST.get('country')
        price_per_night = request.POST.get('price')
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM hosts WHERE host_id =%s",[host])
            host_id = cursor.fetchone()
            cursor.execute("SELECT * FROM countries WHERE name=%s",[country])
            country_id = cursor.fetchone()
            cursor.execute("SELECT * FROM cities WHERE name =%s AND country=%s",[city,country])
            city_id = cursor.fetchone()
            cursor.execute("SELECT * FROM place where address=%s",[place])
            place_id = cursor.fetchone()
            if host_id is None:
                # host does not exists 
                status = "Host does not exists!"
            
            elif country_id is None:
                status = "AirBnb is not available in this country!"
                
            elif place_id is not None:
                status = "Place already exists!"
            
            elif city_id is None:
                # AirBnb available in this country but no user in this city 
                # INSERT city into city table before adding address to place due to 
                # Foreign Key 
                cursor.execute("INSERT INTO cities(name,country) VALUES(%s,%s)",[city,country])
                cursor.execute("INSERT INTO place(host_id,address,city_id,price_per_night,country_id) VALUES (%s,%s,%s,%s,%s)",[host,place,city,price_per_night,country])
                status = "New place added into database!"
                context['status'] = status 
                return render(request,"add_place.html",context)
            else:
                cursor.execute("INSERT INTO place(host_id,address,city_id,price_per_night,country_id) VALUES (%s,%s,%s,%s,%s)",[host,place,city,price_per_night,country])
                status = "New place added into database!"
                context['status'] = status 
                
                return render(request,"add_place.html",context)
        
        
        context['status'] = status 
        
        return render(request,"add_place.html",context)
    
    else:
        return render(request,'add_place.html',context)
    

def admin_place_index(request):
    if request.POST:
        # admin can delete places from Airbnb App 
        if request.POST['action'] == 'delete':
            with connection.cursor() as cursor:
                address = request.POST.get('address')
                cursor.execute("DELETE FROM place WHERE address=%s",[request.POST['address']])
        
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM place ORDER BY address")
        places = cursor.fetchall()
        result_dict = {'records':places}
            
    return render(request,'admin_place.html',result_dict)
    