from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.db.utils import IntegrityError, OperationalError
from django.conf import settings
from django.contrib import messages
from .models import UserProfile


def home(request):
    context = {
        'user': request.user
    }
    return render(request, 'home.html', context)


def signup(request):
    """Handle user signup. On POST create the user, log them in and redirect to signedhome.

    Uses the submitted email as the Django `username` for simplicity.
    """
    context = {
        'user': request.user
    }
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
    context = {
        'user': request.user
    }
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


@login_required(login_url='login')
def newblog(request):
    context = {
        'user': request.user
    }
    return render(request, 'newblog.html', context)


def blog(request):
    context = {
        'user': request.user
    }
    # If user is authenticated, show the authenticated blog template
    if request.user.is_authenticated:
        return render(request, 'blog.html', context)
    else:
        # If user is not authenticated, show the public blog template
        return render(request, 'public_blog.html', context)


def signedhome(request):
    context = {
        'user': request.user
    }
    return render(request, 'signedhome.html', context)


def design(request):
    context = {
        'user': request.user
    }
    return render(request, 'user/design.html', context)


def logout_view(request):
    """Log the user out (POST from header form) and redirect to home."""
    if request.method == 'POST':
        auth_logout(request)
    return redirect('home')


@login_required
def profile_view(request):
    """Display user profile"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    context = {
        'user': request.user,
        'profile': profile,
    }
    return render(request, 'profile.html', context)


@login_required
def edit_profile(request):
    """Edit user profile"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        # Update user basic info
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        
        if first_name:
            request.user.first_name = first_name
        if last_name:
            request.user.last_name = last_name
        if email and email != request.user.email:
            # Check if email is already taken by another user
            if User.objects.filter(email=email).exclude(id=request.user.id).exists():
                messages.error(request, 'This email is already taken by another user.')
            else:
                request.user.email = email
                request.user.username = email  # Update username to match email
        
        request.user.save()
        
        # Update profile info
        profile.bio = request.POST.get('bio', '').strip()
        profile.achievements = request.POST.get('achievements', '').strip()
        
        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        
        profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    context = {
        'user': request.user,
        'profile': profile,
    }
    return render(request, 'edit_profile.html', context)