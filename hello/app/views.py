from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.db.utils import IntegrityError, OperationalError
from django.conf import settings


def home(request):
    context = {}
    return render(request, 'home.html', context)


def signup(request):
    """Handle user signup. On POST create the user, log them in and redirect to signedhome.

    Uses the submitted email as the Django `username` for simplicity.
    """
    context = {}
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')

        if not (name and email and password):
            context['error'] = 'Please fill all fields.'
            return render(request, 'signup.html', context)

        try:
            # username used as email to avoid adding a custom user model now
            user = User.objects.create_user(username=email, email=email, password=password, first_name=name)
        except IntegrityError:
            context['error'] = 'A user with that email already exists.'
            return render(request, 'signup.html', context)
        except OperationalError as e:
            # Surface DB errors during development to help debugging
            if getattr(settings, 'DEBUG', False):
                context['error'] = f'Database error: {e}'
            else:
                context['error'] = 'Database error. Please contact the administrator.'
            return render(request, 'signup.html', context)
        except Exception as e:
            # Include exception text in DEBUG to aid diagnosis
            if getattr(settings, 'DEBUG', False):
                context['error'] = f'Could not create user. {e}'
            else:
                context['error'] = 'Could not create user. Please try again.'
            return render(request, 'signup.html', context)

        # authenticate and log the user in
        user = authenticate(request, username=email, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('signedhome')
        else:
            context['error'] = 'Signup succeeded but automatic login failed. Please log in.'
            return render(request, 'signup.html', context)

    return render(request, 'signup.html', context)


def login(request):
    """Handle user login. On success redirect to signedhome."""
    context = {}
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('signedhome')
        else:
            context['error'] = 'Invalid email or password.'
            return render(request, 'login.html', context)

    return render(request, 'login.html', context)


def newblog(request):
    context = {}
    return render(request, 'newblog.html', context)


def blog(request):
    context = {}
    return render(request, 'blog.html', context)


def signedhome(request):
    context = {}
    return render(request, 'signedhome.html', context)


def design(request):
    context = {}
    return render(request, 'user/design.html', context)


def logout_view(request):
    """Log the user out (POST from header form) and redirect to home."""
    if request.method == 'POST':
        auth_logout(request)
    return redirect('home')




  