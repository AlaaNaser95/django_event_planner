from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views import View
from .forms import *
from django.contrib import messages
from django.http import JsonResponse
import datetime 
from itertools import chain
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
    # previous_events=Event.objects.filter(date__lt=datetime.datetime.now())
    # previous_events=chain(previous_events,Event.objects.filter(date=datetime.date.today(), time__lt=datetime.datetime.now()))

    context={
        'created_events':created_events,
        # 'previous_events':previous_events,
    }

    return render(request, "dashboard.html",context)

def create(request):
    if request.user.is_anonymous:
        return redirect('login')
    form=EventForm()
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            event=form.save(commit=False)
            event.creator=request.user
            event.save()
            messages.success(request, "Successfully Created!")
            return redirect('dashboard')
        print (form.errors)

    context={
        "form":form
    }
    return render(request, "create.html", context )


def detail(request, event_id):
    event = Event.objects.get(id=event_id)
    # student=classroom.student_set.all().order_by('name','-exam_grade')
    bookings=Book.objects.filter(event=event)
    form=BookForm()
    if request.method == 'POST':
        form=BookForm(request.POST)
        if form.is_valid():
            book=form.save(commit=False)
            book.booker=request.user
            book.event=event
            form.save()
            messages.success(request, "Successfully booked!")
    context = {
        "event": event,  
        "form":form ,
        "bookings": bookings,
        }
    return render(request, 'detail.html', context)





def update(request, event_id):
    event = Event.objects.get(id=event_id)
    if request.user.is_authenticated and request.user==event.creator:
        form = EventForm(instance=event)
        if request.method == "POST":
            form = EventForm(request.POST,instance=event)
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

def upcommingList(request):
    if request.user.is_authenticated:
        # events=Event.objects.all()
        # events=Event.objects.filter(date__gte=datetime.date.today(), time__gte=datetime.datetime.now())
        events=Event.objects.filter(date__gt=datetime.datetime.now())
        events=chain(events,Event.objects.filter(date=datetime.date.today(), time__gte=datetime.datetime.now()))
        context={
            "events": events,
        }
        return render(request, 'upcommingEvents.html', context)

