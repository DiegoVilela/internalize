from django.urls import path
from . import views
from django.views.generic import RedirectView

app_name = 'cis'

urlpatterns = [
    path('', views.HomePageView.as_view(), name='homepage'),
    path('cis/<status>/', views.CIListView.as_view(), name='ci_list'),
    path('ci/upload/', views.ci_upload, name='ci_upload'),
    path('ci/<int:pk>', views.CIDetailView.as_view(), name='ci_detail'),
    path('ci/pack/send/', views.send_ci_pack, name='ci_pack_send'),
    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('client/<int:pk>', views.ClientDetailView.as_view(), name='client_detail'),
    path('manufacturer/<int:pk>', views.ManufacturerDetailView.as_view(), name='manufacturer_detail'),
]
