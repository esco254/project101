"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from core.views import home
from core.views import rooms
from core.views import about
from core.views import contact
from core.views import book
from core.views import payment
from core.views import success
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('rooms/', rooms, name='rooms'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('book/', book, name = 'book'),
    path('payment/', payment, name = 'payment'),
    path('success/', success, name = 'success'),
    
]
