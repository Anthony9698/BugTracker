from django import forms
from django.contrib.auth.forms import UserCreationForm
from api.models import UserProfile, Project, Ticket
from crispy_forms.helper import FormHelper
from django.contrib.auth import authenticate
from django.db.models.query import RawQuerySet


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=60, help_text='Required. Add a valid email address.')

    class Meta:
        model = UserProfile
        fields = ("email", "password1", "password2")


class LoginForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = UserProfile
        fields = ('email', 'password')

    def clean(self):
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']
        if not authenticate(email=email, password=password):
            raise forms.ValidationError("Invalid email or password.")


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('title', 'description')


class TicketForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user_id = kwargs.pop("user_id")
        super(TicketForm, self).__init__(*args, **kwargs)
        self.fields['project_id'].queryset = Project.objects.filter(users__id=self.user_id)

    priorities = (
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    )

    project_id = forms.ModelChoiceField(queryset=None)
    priority = forms.CharField(widget=forms.Select(choices=priorities))
    class Meta:
        model = Ticket
        fields = ('title', 'description', 'project_id', 'priority')


    

