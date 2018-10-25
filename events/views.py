from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views import View
from .forms import *
from django.contrib import messages
from django.http import JsonResponse
import datetime 
from itertools import chain
from django.utils import timezone
from django.http import Http404
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
import requests

def home(request):
    return render(request, 'home.html')

class Signup(View):
    form_class = UserSignup
    template_name = 'signup.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(user.password)
            user.save()
            messages.success(request, "You have successfully signed up.")
            login(request, user)
            return redirect("home")
        messages.warning(request, form.errors)
        return redirect("signup")


class Login(View):
    form_class = UserLogin
    template_name = 'login.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            auth_user = authenticate(username=username, password=password)
            if auth_user is not None:
                login(request, auth_user)
                messages.success(request, "Welcome Back!")
                return redirect('dashboard')
            messages.warning(request, "Wrong email/password combination. Please try again.")
            return redirect("login")
        messages.warning(request, form.errors)
        return redirect("login")


class Logout(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, "You have successfully logged out.")
        return redirect("login")

def dashboard(request):
    if request.user.is_anonymous:
        return redirect('login')
    created_events=Event.objects.filter(creator=request.user)
    previous_books=Book.objects.filter(booker=request.user, event__date__lte=datetime.datetime.today()).exclude( event__date=datetime.date.today(), event__time__gte=datetime.datetime.now())
    upcoming_books=Book.objects.filter(booker=request.user, event__date__gte=datetime.datetime.today()).exclude( event__date=datetime.date.today(), event__time__lt=datetime.datetime.now())
    # previous_books=chain(previous_books, Book.objects.filter(booker=request.user, event__date=datetime.date.today(), event__time__lt=datetime.datetime.now()))
    previous_events = {previous_book.event for previous_book in previous_books}
    # upcoming_events = {upcoming_book.event for upcoming_book in upcoming_books}
    # tickets=sum(upcoming_books.values_list('tickets', flat=True))

    # previous_events = previous_events.values_list("event",falt=True).distinct()
    # upcoming_events = {upcoming_book.event for upcoming_book in upcoming_books}

    # previous_events={previous_book.event for previous_book in Book.objects.filter(booker=request.user, event__date__lte=timezone.now(), event__time__lte=timezone.now())}
    # upcoming_books=Book.objects.filter(booker=request.user, event__date__gte=timezone.now(), event__time__gte=timezone.now())
    
    
    context={
        'created_events':created_events,
        'previous_events':previous_events,
        'upcoming_events': upcoming_books,
        
    }

    return render(request, "dashboard.html",context)

def create(request):
    if request.user.is_anonymous:
        return redirect('login')
    followers=[follow.follower.email for follow in Follow.objects.filter(followed=request.user)]
    form=EventForm()
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event=form.save(commit=False)
            event.creator=request.user
            event.save()
            sendemail(request.user,followers)
            messages.success(request, "Successfully Created!")
            return redirect('dashboard')
        print (form.errors)

    context={
        "form":form
    }
    return render(request, "create.html", context )


def detail(request, event_id):
    if request.user.is_anonymous:
        return redirect('login')
    event = Event.objects.get(id=event_id)
    # student=classroom.student_set.all().order_by('name','-exam_grade')
    bookings=Book.objects.filter(event=event)
    print(timezone.now())
    print(event.date > timezone.now().date())
    print(event.date == timezone.now().date())
    print(event.time >= timezone.now().time())
    comming= (event.date > timezone.now().date() ) or (event.date == timezone.now().date() and event.time >= timezone.now().time()) 
    form=BookForm()
    if request.method == 'POST':
        form=BookForm(request.POST)
        if form.is_valid():
            if event.seats == 0:
                messages.warning(request, "Full!!!!")
            elif int(request.POST.get('tickets')) > event.seats:
                messages.warning(request, "No enough seats available")
            else:
                book=form.save(commit=False)
                book.booker=request.user
                book.event=event
                book.save()#############could have error
                event.seats=event.seats - int(request.POST.get('tickets'))
                event.save()
                bookemail(book)
                messages.success(request, "Successfully booked!")
                return redirect('events')
            # messages.success(request, "Successfully booked!")
    context = {
        "event": event,  
        "form":form ,
        "bookings": bookings,
        "comming":comming,
        }
    return render(request, 'detail.html', context)





def update(request, event_id):
    event = Event.objects.get(id=event_id)
    if request.user.is_anonymous:
        return redirect('login')
    if request.user!= event.creator:
        return render(request, 'no-access.html')
    form = EventForm(instance=event)
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES,instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Successfully Edited!")

            return redirect('dashboard')
        print (form.errors)
    
    context = {
        "form":form,
        "event": event,   
        }
    return render(request, 'update.html', context)


def updateProfile(request):
    if request.user.is_anonymous:
        return redirect('login')
    form = UserSignup(instance=request.user)
    if request.method == "POST":
        form = UserSignup(request.POST,instance=request.user)
        if form.is_valid():
            user=form.save(commit=False)
            user.set_password(user.password)
            user.save()
            # login(request.user)
            messages.success(request, "Successfully Updated!")
            return redirect('dashboard')
        print (form.errors)
    
    context = {
        "form":form,   
        }
    return render(request, 'update-profile.html', context)

def upcommingList(request):
    if request.user.is_anonymous:
        return redirect('login')
        # events=Event.objects.all()
        # events=Event.objects.filter(date__gte=datetime.date.today(), time__gte=datetime.datetime.now())
    events=Event.objects.filter(date__gte=datetime.datetime.now()).exclude(date=datetime.date.today(), time__lt=datetime.datetime.now())
    # events=chain(events,Event.objects.filter(date=datetime.date.today(), time__gte=datetime.datetime.now()))
    query = request.GET.get('q')
    if query:
        events = events.filter(
            Q(title__icontains=query)|
            Q(description__icontains=query)|
            Q(creator__username__icontains=query)
            ).distinct()
    context={
        "events": events,
    }
    return render(request, 'upcommingEvents.html', context)


def profilePage(request,user_id):
    user=User.objects.get(id=user_id)
    events=Event.objects.filter(creator=user)
    following= [follow.followed  for follow in Follow.objects.filter(follower=request.user)]
    context={
        "user":user,
        "events":events,
        "following":following,
    }
    return render(request,"profile.html",context)

def followOrganizer(request,user_id):
    user=User.objects.get(id=user_id)
    if request.user.is_anonymous:
        return redirect('login')
    aFollow, created = Follow.objects.get_or_create(follower=request.user, followed=user)
    if created:
        action = "follow"
    else:
        aFollow.delete()
        action="unfollow"
    
    response = {
        "action": action,
    }
    return JsonResponse(response, safe=False)


def sendemail(user,followers):
    subject = 'New event'
    message = user.username+' have new event'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = followers
    send_mail( subject, message, email_from, recipient_list )

def bookemail(book):
    subject = "Event Booking"
    message = "Event: %s\nTickets:%s\nDate: %s\nTime: %s\nLocation: %s"%(book.event.title, book.tickets, book.event.date, book.event.time, book.event.location)
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [book.booker.email,]
    send_mail( subject, message, email_from, recipient_list )

def cancelBooking(request, book_id):
    book=Book.objects.get(id=book_id)
    # if book.event.time < timezone.now().time: 
    book.delete()
    messages.success(request, "Successfully cancelled!")
    
    # messages.success(request, "Cancelling not available!!")

    return redirect("dashboard")

class TapPayment(View):
    def pay_cart(self, request, user, order):
        return self.pay(**{'customer': user,
                           'qty': '1', 'price': order.total_price(),
                           'isTest': testing_payment,
                           'order_id': order.id})

    def pay(self, *args, **kwargs):
        if not kwargs.get('isTest'):
            client = Client('https://www.gotapnow.com/webservice/PayGatewayService.svc?wsdl')
        else:
            client = Client('http://live.gotapnow.com/webservice/PayGatewayService.svc?wsdl')

        payment_request = client.factory.create('ns0:PayRequestDC')

        customer = kwargs.get('customer')

        # Customer Info
        payment_request.CustomerDC.Email = customer.email
        payment_request.CustomerDC.Mobile = customer.phone_number
        payment_request.CustomerDC.Name = '{} {}'.format(customer.first_name, customer.last_name)

        # Merchant Info
        if not kwargs.get('isTest'):
            payment_request.MerMastDC.MerchantID = tap_merchant_id
            payment_request.MerMastDC.UserName = tap_user
            payment_request.MerMastDC.Password = tap_password
            payment_request.MerMastDC.AutoReturn = 'Y'
            payment_request.MerMastDC.ErrorURL = '{}/paymenterror'.format(website_url())
            payment_request.MerMastDC.ReturnURL = '{}/receipt'.format(website_url())
        else:
            payment_request.MerMastDC.MerchantID = "1014"
            payment_request.MerMastDC.UserName = 'test'
            payment_request.MerMastDC.Password = "4l3S3T5gQvo%3d"
            payment_request.MerMastDC.AutoReturn = 'N'
            payment_request.MerMastDC.ErrorURL = '{}/paymenterror'.format(staging_url())
            payment_request.MerMastDC.ReturnURL = '{}/receipt'.format(staging_url())

        # Product Info
        mapping = {'CurrencyCode': currency_code(), 'Quantity': kwargs.get('qty'),
                   'UnitPrice': kwargs.get('price'),
                   'TotalPrice': float(kwargs.get('qty')) * float(kwargs.get('price')),
                   'UnitName': 'Order {}'.format(kwargs.get('order_id'))}
        product_dc = {k: v for k, v in mapping.iteritems()}
        payment_request.lstProductDC.ProductDC.append(product_dc)

        response = client.service.PaymentRequest(payment_request)
        details = "resmsg: {} status: {}".format(response.ResponseMessage, 'Pending')
        Receipt.objects.get_or_create(reference_id=response.ReferenceID, details=details,
                                      order=Order.objects.get(id=kwargs.get('order_id')),
                                      total_price=(float(kwargs.get('qty')) * float(kwargs.get('price'))))

        paymentUrl = "{}?ref={}".format(response.TapPayURL, response.ReferenceID)
        return redirect(paymentUrl or '/paymenterror')