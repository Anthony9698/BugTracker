from django import forms
from django.contrib.auth.forms import UserCreationForm
from profiles.models import UserProfile, Project, Ticket, Comment, TicketAuditTrail
from crispy_forms.helper import FormHelper
from django.contrib.auth import authenticate
from django.db.models.query import RawQuerySet
from profiles.utils import send_ticket_assignment_email, send_ticket_reassignment_email, \
    send_ticket_updated_email 



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
        widgets = {
            'description': forms.Textarea(attrs={'rows':4, 'cols':15})
        }


class TicketForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(TicketForm, self).__init__(*args, **kwargs)
        self.fields['project'].queryset = Project.objects.filter(users__id=user.id)
        self.initial_title = self.instance.title
        self.initial_description = self.instance.description
        self.initial_classification = self.instance.classification
        self.initial_priority = self.instance.priority
        self.initial_status = self.instance.status
        self.user = user

        try:
            self.initial_project = self.instance.project
        except Project.DoesNotExist:
            self.initial_project = None

        if self.initial_project is not None:
            self.fields['status'] = forms.CharField(widget=forms.Select(
                choices=(
                    ('Waiting for support', 'Waiting for support'),
                    ('Waiting for customer', 'Waiting for customer'),
                    ('Resolved', 'Resolved'),
                    ('On hold', 'On hold'),
                    ('New', 'New'))))
        else:
            self.fields['status'].widget = forms.HiddenInput()

    classification = forms.CharField(widget=forms.Select(
        choices=(
            ('Error report', 'Error report'),
            ('Feature request', 'Feature request'),
            ('Service request', 'Service request'),
            ('Other', 'Other'))))

    priority = forms.CharField(widget=forms.Select(
        choices=(
            ('Low', 'Low'),
            ('Medium', 'Medium'),
            ('High', 'High'),
            ('Critical', 'Critical'))))

    def save(self, commit=True):
        ticket_instance = super(TicketForm, self).save(commit=True)
        if self.initial_project is None:
            TicketAuditTrail.objects.create(
                user=self.user,
                ticket=self.instance,
                entry_message="Title: " + self.instance.title + "\n" + "Project: " + str(self.instance.project) + "\n" \
                              "Description: " + self.instance.description + "\n" + "Priority: " + self.instance.priority)
        elif self.has_changed():
            for change in self.changed_data:
                if change == 'title':
                    TicketAuditTrail.objects.create(
                        user=self.user,
                        ticket=self.instance,
                        entry_message="Title changed from " + "\"" + self.initial_title + "\"" + " to " + "\"" + self.instance.title + "\"")
                
                elif change == 'description':
                    TicketAuditTrail.objects.create(
                        user=self.user,
                        ticket=self.instance,
                        entry_message="Description changed from " + "\"" + self.initial_description + "\"" + ' to ' + "\"" + self.instance.description + "\"")

                elif change == 'project':
                    TicketAuditTrail.objects.create(
                        user=self.user,
                        ticket=self.instance,
                        entry_message="Project changed from " + "\"" + str(self.initial_project) + "\"" + ' to ' + "\"" + str(self.instance.project) + "\""
                    )

                elif change == 'classification':
                    TicketAuditTrail.objects.create(
                        user=self.user,
                        ticket=self.instance,
                        entry_message="Type changed from " + "\"" + str(self.initial_classification) + "\"" + ' to ' + "\"" + str(self.instance.classification) + "\""
                    )

                elif change == 'priority':
                    TicketAuditTrail.objects.create(
                        user=self.user,
                        ticket=self.instance,
                        entry_message="Priority changed from " + "\"" + self.initial_priority + "\"" + ' to ' + "\"" + self.instance.priority + "\""
                    )

                elif change == 'status':
                    TicketAuditTrail.objects.create(
                        user=self.user,
                        ticket=self.instance,
                        entry_message="Status changed from " + "\"" + str(self.initial_status) + "\"" + ' to ' + "\"" + self.instance.status + "\""
                    )

        if commit:
            if self.user is not ticket_instance.assigned_user and ticket_instance.assigned_user is not None:
                send_ticket_updated_email(self.user, ticket_instance)

            ticket_instance.save()
        return ticket_instance
                

    class Meta:
        model = Ticket
        fields = ['title', 'description', 'project', 'classification', 'priority', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows':4, 'cols':15})
        }


class UserRolesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserRolesForm, self).__init__(*args, **kwargs)
        self.fields['roles'].label = ""
        
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
    def __init__(self, user, ticket, *args, **kwargs):
        super(AssignTicketUserForm, self).__init__(*args, **kwargs)
        project = Project.objects.get(pk=ticket.project.id)
        self.fields['assigned_user'].queryset = project.users.filter(roles__contains="Developer")
        self.fields['assigned_user'].required = False
        self.user = user
        self.initial_assignment = self.instance.assigned_user

    def save(self, commit=True):
        ticket = super(AssignTicketUserForm, self).save(commit=True)
        
        if self.has_changed() and self.initial_assignment is not None:
            TicketAuditTrail.objects.create(
                user=self.user,
                ticket=self.instance,
                entry_message="Ticket assignment changed from " + "\"" + str(self.initial_assignment) \
                            + "\"" + " to " + "\"" + str(self.instance.assigned_user) + "\""
            )
            send_ticket_reassignment_email(self.user, self.initial_assignment, ticket)

        else:
            send_ticket_assignment_email(self.user, ticket)
        
        if commit:
            ticket.save()
        return ticket

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


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'email']
        