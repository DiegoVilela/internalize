from django.urls import path
from . import views

app_name = 'cis'

urlpatterns = [
    path('', views.HomePageView.as_view(), name='homepage'),
    path('cis/<status>/', views.CIListView.as_view(), name='ci_list'),
    path('ci/create/', views.CICreateView.as_view(), name='ci_create'),
    path('ci/upload/', views.ci_upload, name='ci_upload'),
    path('ci/<int:pk>', views.CIDetailView.as_view(), name='ci_detail'),
    path('ci/pack/send/', views.send_ci_pack, name='ci_pack_send'),
    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('client/<int:pk>', views.ClientDetailView.as_view(), name='client_detail'),
    path('manufacturer/<int:pk>', views.ManufacturerDetailView.as_view(), name='manufacturer_detail'),
    path('appliances/', views.ApplianceListView.as_view(), name='appliance_list'),
    path('appliance/create/', views.ApplianceCreateView.as_view(), name='appliance_create'),
    path('appliance/<int:pk>', views.ApplianceUpdateView.as_view(), name='appliance_update'),
]
