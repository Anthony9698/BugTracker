from django.db import models

# Create your models here.
class Project(models.Model):
    title = models.CharField(max_length=100, null=False)
    date_added = models.DateField()

class Ticket(models.Model):
    title = models.CharField(max_length=100, null=False)
    description = models.TextField(default="")
    project_id = models.ForeignKey(Project, default=None, on_delete=models.PROTECT)
    priority = models.CharField(max_length=50, null=False)
