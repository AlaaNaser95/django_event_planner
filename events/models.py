from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date
from django.utils import timezone

class Event(models.Model):
	title=models.CharField(max_length=120)
	description=models.TextField()
	location=models.TextField()
	image=models.ImageField(null=True)
	date=models.DateField()
	time=models.TimeField()
	seats=models.PositiveIntegerField()
	creator= models.ForeignKey(User, default=1, on_delete=models.CASCADE)

	def __str__(self):
		return self.title

class Book(models.Model):
	booker= models.ForeignKey(User, default=1, on_delete=models.CASCADE)
	event= models.ForeignKey(Event, default=1, on_delete=models.CASCADE)
	tickets=models.PositiveIntegerField(default=1)


class Follow(models.Model):
	follower= models.ForeignKey(User, default=1, on_delete=models.CASCADE, related_name='follower')
	followed= models.ForeignKey(User, default=2, on_delete=models.CASCADE, related_name='followed')

