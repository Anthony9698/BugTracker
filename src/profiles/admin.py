from django.contrib import admin
from .models import Project, Ticket, UserProfile, Comment, TicketAuditTrail

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Project)
admin.site.register(Ticket)
admin.site.register(Comment)
admin.site.register(TicketAuditTrail)