from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.timezone import now
from multiselectfield import MultiSelectField
from django.utils.timezone import get_current_timezone
from datetime import datetime


class MyProfileManager(BaseUserManager):
    # these fields are required when creating a new user/superuser
    def create_user(self, email, password=None):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email = self.normalize_email(email),
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(
            email = self.normalize_email(email),
            password = password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.is_admin = True
        user.save(using=self._db)


class UserProfile(AbstractBaseUser):
    choices = (('Submitter', 'Submitter'),
               ('Developer', 'Developer'),
               ('Project Manager', 'Project Manager'),
               ('Admin', 'Admin'))

    first_name = models.CharField(max_length=64, null=False, default="First Name")
    last_name = models.CharField(max_length=64, null=False, default="Last Name")
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    roles = MultiSelectField(choices=choices, default='Submitter')

    USERNAME_FIELD = 'email'

    objects = MyProfileManager()

    def __str__(self):
        return self.first_name + ' ' + self.last_name

    # users can do stuff if they are admin
    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True


class Attachment(models.Model):
    uploader = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, default=None)
    content = models.FileField(null=True, blank=True)
    date_uploaded = models.DateField(default=now, editable=False)

    
class Project(models.Model):
    title = models.CharField(max_length=64, null=False)
    description = models.TextField()
    date_added = models.DateField(default=now, editable=False)
    archived = models.BooleanField(default=False)
    users = models.ManyToManyField(UserProfile)

    def __str__(self):
        return self.title
        

class Ticket(models.Model):
    owner = models.ForeignKey(UserProfile, on_delete=models.PROTECT, null=True, default=None, related_name='owner')
    assigned_user = models.ForeignKey(UserProfile, on_delete=models.PROTECT, null=True, default=None, related_name='assigned_user')
    attachment = models.ForeignKey(Attachment, on_delete=models.PROTECT, null=True)
    title = models.CharField(max_length=64, null=False)
    description = models.TextField(default="")       
    project = models.ForeignKey(Project, default=None, on_delete=models.PROTECT)
    priority = models.CharField(max_length=64, null=False)
    status = models.CharField(max_length=64, null=False, default='New')
    classification = models.CharField(max_length=64, null=False, default=None)
    date_created = models.DateTimeField(default=now, editable=False)
    last_modified_date = models.DateTimeField(auto_now=True)


class Comment(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, null=False, default=None)
    description = models.TextField(default="")
    date_posted = models.DateTimeField(default=now, editable=False)
    last_modified_date = models.DateTimeField(auto_now=True)

    __original_description = None

    def __init__(self, *args, **kwargs):
        super(Comment, self).__init__(*args, **kwargs)
        self.__original_description = self.description

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        # description changed, do something here
        if self.description != self.__original_description:
            self.last_modified_date = datetime.now(tz=get_current_timezone())

        super(Comment, self).save(force_insert, force_update, *args, **kwargs)
        self.__original_description = self.description


class TicketAuditTrail(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, default=None)
    ticket = models.ForeignKey(Ticket, on_delete=models.SET_NULL, null=True, default=None)
    date_added = models.DateTimeField(default=now, editable=False)
    entry_message = models.TextField(default="")