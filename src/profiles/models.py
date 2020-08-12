from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.timezone import now
from multiselectfield import MultiSelectField
from django.utils.timezone import get_current_timezone
from datetime import datetime

# defining what I want to happen when a new user/superuser is created
# class MyProfileManager(BaseUserManager):
#     # these fields are required when creating a new user/superuser
#     def create_user(self, email, username, password=None):
#         if not email:
#             raise ValueError("Users must have an email address")
#         if not username:
#             raise ValueError("Users must have a username")

#         user = self.model(
#             email = self.normalize_email(email),
#             username=username,
#         )
#         user.set_password(password)
#         user.save(using=self._db)
#         return user


#     def create_superuser(self, email, username, password):
#         user = self.create_user(
#             email = self.normalize_email(email),
#             password = password,
#             username=username,
#         )
#         user.is_admin = True
#         user.is_staff = True
#         user.is_superuser = True
#         user.is_admin = True
#         user.save(using=self._db)


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
    #username = models.CharField(max_length=30, unique=True)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    roles = MultiSelectField(choices=choices, default='Submitter')

    USERNAME_FIELD = 'email'
    #REQUIRED_FIELDS = ['username']

    objects = MyProfileManager()

    def __str__(self):
        return self.first_name + ' ' + self.last_name

    # users can do stuff if they are admin
    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    
class Project(models.Model):
    title = models.CharField(max_length=64, null=False)
    description = models.TextField()
    date_added = models.DateField(default=now, editable=False)
    archived = models.BooleanField(default=False)
    users = models.ManyToManyField(UserProfile)

    def __str__(self):
        return self.title
        

class Ticket(models.Model):
    # owner = models.ForeignKey(UserProfile, on_delete=models.PROTECT, null=True, related_name='owner')
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE, default=None)
    assigned_user = models.OneToOneField(UserProfile, on_delete=models.PROTECT, null=True, related_name='assigned_user')
    title = models.CharField(max_length=64, null=False)
    description = models.TextField(default="")       
    project = models.ForeignKey(Project, default=None, on_delete=models.PROTECT)
    priority = models.CharField(max_length=64, null=False)
    status = models.CharField(max_length=64, null=False, default=None)
    date_created = models.DateTimeField(default=now, editable=False)
    last_modified_date = models.DateTimeField(auto_now=True)

    __original_assigned_user = None
    __original_title = None
    __original_description = None
    __original_project = None
    __original_priority = None
    __original_status = None
    __new_ticket = False

    def detect_changes(self, *args, **kwargs):
        if self.assigned_user != self.__original_assigned_user and self.__original_assigned_user != "":
            TicketAuditTrail.objects.create(ticket=self, entry_message="Ticket assignment changed from " + "\"" + self.__original_assigned_user + "\"" + " to " + "\"" + self.assigned_user + "\"")

        if self.title != self.__original_title and self.__original_title != "":
            TicketAuditTrail.objects.create(ticket=self, entry_message="Title changed from " + "\"" + self.__original_title + "\"" + " to " + "\"" + self.title + "\"")

        if self.description != self.__original_description and self.__original_description != "":
            TicketAuditTrail.objects.create(ticket=self, entry_message="Description changed from " + "\"" + self.__original_description + "\"" + ' to ' + "\"" + self.description + "\"")

        if self.project != self.__original_project and self.__original_project is not None:
            TicketAuditTrail.objects.create(ticket=self, entry_message="Project changed from " + "\"" + self.__original_project + "\"" + ' to ' + "\"" + self.project + "\"")

        if self.priority != self.__original_priority and self.__original_priority != "":
            TicketAuditTrail.objects.create(ticket=self, entry_message="Priority changed from " + "\"" + self.__original_priority + "\"" + ' to ' + "\"" + self.priority + "\"")

        if self.status != self.__original_status and self.__original_status is not None:
            TicketAuditTrail.objects.create(ticket=self, entry_message="Status changed from " + "\"" + self.__original_status + "\"" + ' to ' + "\"" + self.status + "\"")


    def __init__(self, *args, **kwargs):
        super(Ticket, self).__init__(*args, **kwargs)
        self.__original_assigned_user = self.assigned_user
        self.__original_title = self.title
        self.__original_description = self.description
        self.__original_priority = self.priority
        self.__original_status = self.status
   
    def save(self, *args, **kwargs):
        if self.id is not None:
            self.detect_changes()
        else:
            self.__new_ticket = True
        super(Ticket, self).save(*args, **kwargs)

        if self.__new_ticket:
            TicketAuditTrail.objects.create(ticket=self, entry_message="Created by " + str(self.owner) + "\nTitle: " \
                                         + self.title + "\nProject: " + str(self.project) + "\nDescription: " + self.description \
                                         + "\nPriority: " + self.priority)
            self.__new_ticket = False
        self.__original_assigned_user = self.assigned_user
        self.__original_title = self.title
        self.__original_description = self.description
        self.__original_project = self.project
        self.__original_priority = self.priority
        self.__original_status = self.status


class Comment(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, null=True)
    description = models.TextField(default="")
    date_posted = models.DateTimeField(default=now, editable=False)
    last_modified_date = models.DateTimeField(blank=True)

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
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    date_added = models.DateTimeField(default=now, editable=False)
    entry_message = models.TextField(default="")

