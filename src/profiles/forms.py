from django import forms
from django.contrib.auth.forms import UserCreationForm
from profiles.models import UserProfile, Project, Ticket, Comment
from crispy_forms.helper import FormHelper
from django.contrib.auth import authenticate
from django.db.models.query import RawQuerySet


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=64)
    last_name = forms.CharField(max_length=64)
    email = forms.EmailField(max_length=64, help_text='Required. Add a valid email address.')

    class Meta:
        model = UserProfile
        fields = ["first_name", "last_name", "email", "password1", "password2"]


class LoginForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = UserProfile
        fields = ['email', 'password']

    def clean(self):
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']
        if not authenticate(email=email, password=password):
            raise forms.ValidationError("Invalid email or password.")


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description']


class TicketForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(TicketForm, self).__init__(*args, **kwargs)
        self.fields['project'].queryset = Project.objects.filter(users__id=user.id)
    priority = forms.CharField(widget=forms.Select(
        choices=(
            ('Low', 'Low'),
            ('Medium', 'Medium'),
            ('High', 'High'),
            ('Critical', 'Critical'))))
    status = forms.CharField(widget=forms.Select(
        choices=(
            ('Waiting for support', 'Waiting for support'),
            ('Waiting for customer', 'Waiting for customer'),
            ('Resolved', 'Resolved'),
            ('On hold', 'On hold'),
            ('New', 'New'))))

    class Meta:
        model = Ticket
        fields = ['title', 'description', 'project', 'priority', 'status']


class UserRolesForm(forms.ModelForm):
    roles = forms.MultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple,
        choices=(
            ('Submitter', 'Submitter'),
            ('Developer', 'Developer'),
            ('Project Manager', 'Project Manager'),
            ('Admin', 'Admin')))

    class Meta:
        model = UserProfile
        fields = ['roles',]
        

class AddProjectUsersForm(forms.Form):
    def __init__(self, project_users, *args, **kwargs):
        super(AddProjectUsersForm, self).__init__(*args, **kwargs)
        self.fields['assigned'] = forms.ModelMultipleChoiceField(queryset=project_users)
        self.fields['assigned'].label = "Assigned Users"
        self.fields['assigned'].required = False


class RemoveProjectUsersForm(forms.Form):
    def __init__(self, all_users, *args, **kwargs):
        super(RemoveProjectUsersForm, self).__init__(*args, **kwargs)
        self.fields['all_users'] = forms.ModelMultipleChoiceField(queryset=all_users)
        self.fields['all_users'].label = "Users to Add"
        self.fields['all_users'].required = False


class AssignTicketUserForm(forms.ModelForm):
    def __init__(self, ticket, *args, **kwargs):
        super(AssignTicketUserForm, self).__init__(*args, **kwargs)
        project = Project.objects.get(pk=ticket.project.id)
        self.fields['assigned_user'].queryset = project.users.filter(roles__contains="Developer")
        self.fields['assigned_user'].required = False

    class Meta:
        model = Ticket
        fields = ['assigned_user',]


class CommentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['description'].widget.attrs['rows'] = 4
        self.fields['description'].widget.attrs['cols'] = 15

    class Meta:
        model = Comment
        fields = ['description',]