import os
import boto3
from botocore.errorfactory import ClientError
from django.core import mail
from profiles.models import Project, Ticket, Attachment


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


def send_ticket_assignment_email(proj_manager, ticket):
    with mail.get_connection() as connection:
        mail.EmailMessage(
            "New Ticket Assignment",
            "Hello, this message is to inform you that your project manager " + str(proj_manager) + ","
                + " has assigned you the following ticket: " + str(ticket.title) + "."
                + "\n\nThank you for using our site!" + "\n\nThe Bug Tracker team.",
            os.environ.get('EMAIL_HOST'),
            [ticket.assigned_user.email],
            connection=connection,
        ).send()


def send_ticket_reassignment_email(proj_manager, old_user, ticket):
    with mail.get_connection() as connection:
        mail.EmailMessage(
            "Ticket Reassignment",
            "Hello, this message is to inform you that your project manager " + str(proj_manager) + ","
                + " has reassigned your ticket: " + str(ticket.title) + " to " + str(ticket.assigned_user) + "."
                + "\n\nThank you for using our site!" + "\n\nThe Bug Tracker team.",
            os.environ.get('EMAIL_HOST'),
            [old_user.email],
            connection=connection,
        ).send()
    send_ticket_assignment_email(ticket.assigned_user, ticket)


def send_ticket_updated_email(user, ticket):
    with mail.get_connection() as connection:
        mail.EmailMessage(
            "Ticket Info Updated",
            "Hello, this message is to inform you that your assigned ticket " + str(ticket.title) + ","
            + " was recently updated by " + str(user) + ". " + "To view the changes, please refer"
            + " to the ticket's history page."
            + "\n\nThank you for using our site!" + "\n\nThe Bug Tracker team.",
            os.environ.get('EMAIL_HOST'),
            [ticket.assigned_user.email],
            connection=connection,
        ).send()


def send_comment_added_email(user, ticket):
    with mail.get_connection() as connection:
        mail.EmailMessage(
            "Comment Added to Ticket",
            "Hello, this message is to inform you that " + str(user) + " left a comment on your assigned ticket "
            + str(ticket.title) + "." + "\n\nThank you for using our site!" + "\n\nThe Bug Tracker team.",
            os.environ.get('EMAIL_HOST'),
            [ticket.assigned_user.email],
            connection=connection,
        ).send()


def update_ticket_attachments(ticket):
    ticket_attachments = ticket.attachments.all()

    # checking to see which attachments exist in S3 bucket
    # if it doesn't, delete reference in database
    s3 = boto3.client('s3')
    for attachment in ticket_attachments:
        key = 'media/' + attachment.content.name 
        try:
            s3.head_object(Bucket=os.environ.get('AWS_STORAGE_BUCKET_NAME'), Key=key)
        except ClientError:
            # Not found
            ticket.attachments.remove(attachment)
            Attachment.objects.filter(id=attachment.id).delete()
