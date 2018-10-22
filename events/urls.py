from django.urls import path
from .views import *

urlpatterns = [
	path('', home, name='home'),
    path('signup/', Signup.as_view(), name='signup'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('create/', create, name='create-event'),
    path('detail/<int:event_id>/', detail, name='event-detail'),
    path('update/<int:event_id>/', update, name='update-event'),
    path('events/', upcommingList , name='events'),
    
]