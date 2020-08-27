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

    if 'Admin' in user_roles:
        user_tickets = Ticket.objects.all()

    return user_tickets.order_by('-last_modified_date')