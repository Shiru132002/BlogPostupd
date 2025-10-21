from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),  
    path('newblog/', views.newblog, name='newblog'),
    path('blog/', views.blog, name='blog'),
    path('signedhome/', views.signedhome, name='signedhome'),
    path('design/', views.design, name='design'),
    path('logout/', views.logout_view, name='logout'),
]
