from django.core import mail
import os
from profiles.models import Project, Ticket


def get_user_tickets(request, user_roles):
    user_projects = Project.objects.filter(users__id=request.user.id)
    user_tickets = Ticket.objects.none()

    if 'Submitter' in user_roles:
        user_tickets = Ticket.objects.filter(owner__id=request.user.id) | user_tickets
    
    if 'Developer' in user_roles:
        user_tickets = Ticket.objects.filter(assigned_user__id=request.user.id) | user_tickets

    if 'Project Manager' in user_roles:
        user_tickets = Ticket.objects.filter(project__in=user_projects) | user_tickets

    if 'Admin' in user_roles or request.user.is_admin:
        user_tickets = Ticket.objects.all()

    return user_tickets.order_by('-last_modified_date')


def send_ticket_assignment_email(user, ticket):
    with mail.get_connection() as connection:
                mail.EmailMessage(
                    "New Ticket Assignment",
                    "Hello, this message is to inform you that your project manager " + str(user)
                        + " has assigned you the following ticket: " + str(ticket.title)
                        + "\n\nThank you for using our site!" + "\n\nThe Bug Tracker team.",
                    os.environ.get('EMAIL_HOST'),
                    [ticket.assigned_user.email],
                    connection=connection,
                ).send()


def send_ticket_reassignment_email(old_user, new_user, ticket):
    with mail.get_connection() as connection:
                mail.EmailMessage(
                    "Ticket Reassignment",
                    "Hello, this message is to inform you that your project manager " + str(old_user)
                        + " has reassigned your ticket: " + str(ticket.title) + " to " + str(new_user)
                        + "\n\nThank you for using our site!" + "\n\nThe Bug Tracker team.",
                    os.environ.get('EMAIL_HOST'),
                    [ticket.assigned_user.email],
                    connection=connection,
                ).send()
    send_ticket_assignment_email(new_user, ticket)
