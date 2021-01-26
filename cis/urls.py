from django.urls import path
from . import views
from django.views.generic import RedirectView

app_name = 'cis'

urlpatterns = [
    path('', RedirectView.as_view(url='/cis/cis/')),
    path('cis/', views.CIListView.as_view(), name='ci_list'),
    path('ci/<int:pk>', views.CIDetailView.as_view(), name='ci_detail'),
    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('client/<int:pk>', views.ClientDetailView.as_view(), name='client_detail'),
]
