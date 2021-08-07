from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# Task class to hold the details of all to-do items of a particular user
class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    complete = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)  # Date created on
    
    def __str__(self):
        return self.title
    
    class Meta:
        order_with_respect_to='user'
        #ordering = ['complete']