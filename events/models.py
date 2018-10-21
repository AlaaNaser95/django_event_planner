from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Event(models.Model):
	title=models.CharField(max_length=120)
	description=models.TextField()
	location=models.TextField()
	date=models.DateField(default='2005-12-01')
	time=models.TimeField(default='12:10:20')
	seats=models.PositiveIntegerField()
	creator= models.ForeignKey(User, default=1, on_delete=models.CASCADE)

	def __str__(self):
		return self.title