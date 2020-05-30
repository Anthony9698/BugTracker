from django.db import models

# Create your models here.
class Ticket(models.Model):
    title = models.CharField(max_length=100, null=False)
    description = models.TextField(default="")
    project_id = models.BigIntegerField(),
    priority = models.CharField(max_length=50)


class Project(models.Model):
    title = models.CharField(max_length=100, null=False)
    date_added = models.DateField()