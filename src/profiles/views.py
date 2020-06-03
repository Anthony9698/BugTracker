from django.shortcuts import render

# Create your views here.

def login(request):
    context = {}
    template = 'login.html'
    context['template'] = template
    return render(request, template, context)


def register(request):
    context = {}
    template = 'register.html'
    context['template'] = template
    return render(request, template, context)


def dashboard(request):
    context = {}
    template = 'dashboard.html'
    return render(request, template, context)


def tickets(request):
    context = {}
    template = 'tickets.html'
    return render(request, template, context)


def projects(request):
    context = {}
    template = 'projects.html'
    return render(request, template, context)


def new_ticket(request):
    context = {}
    template = 'new_ticket.html'
    return render(request, template, context)
    