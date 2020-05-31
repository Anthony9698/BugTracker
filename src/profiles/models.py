from django.db import models
from django.utils.timezone import now


class User(models.Model):
    email = models.CharField(max_length=255, null=False, unique=True)
    join_date = models.DateTimeField(default=now, editable=False)
    last_login = models.DateTimeField(default=now, editable=False)
    password = models.CharField(max_length=64, null=False)


class Project(models.Model):
    title = models.CharField(max_length=64, null=False)
    description = models.TextField()
    date_added = models.DateField(default=now, editable=False)
    users = models.ManyToManyField(User)


class Ticket(models.Model):
    title = models.CharField(max_length=64, null=False)
    description = models.TextField(default="")
    project_id = models.ForeignKey(Project, default=None, on_delete=models.PROTECT)
    priority = models.CharField(max_length=64, null=False)

