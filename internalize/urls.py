"""internalize URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
import debug_toolbar
from django.contrib import admin
from django.urls import path, include
from django_registration.backends.activation.views import RegistrationView

from cis.forms import UserForm
from cis.views import homepage

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cis/', include('cis.urls')),
    path('', homepage, name='homepage'),
    path('accounts/register/',
         RegistrationView.as_view(
             form_class=UserForm
         ),
         name='django_registration_register',
         ),
    path('accounts/', include('django_registration.backends.activation.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('__debug__/', include(debug_toolbar.urls)),
]
