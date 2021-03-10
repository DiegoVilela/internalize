from django.urls import path
from . import views

app_name = 'cis'

urlpatterns = [
    path('cis/<status>/', views.CIListView.as_view(), name='ci_list'),
    path('ci/create/', views.CICreateView.as_view(), name='ci_create'),
    path('ci/upload/', views.ci_upload, name='ci_upload'),
    path('ci/<int:pk>', views.CIDetailView.as_view(), name='ci_detail'),
    path('ci/pack/send/', views.send_ci_pack, name='ci_pack_send'),
    path('sites/', views.manage_client_sites, name='manage_client_sites'),
    path('site/create/', views.SiteCreateView.as_view(), name='site_create'),
    path('site/<int:pk>', views.SiteUpdateView.as_view(), name='site_update'),
    path('manufacturer/<int:pk>', views.ManufacturerDetailView.as_view(), name='manufacturer_detail'),
    path('appliances/', views.ApplianceListView.as_view(), name='appliance_list'),
    path('appliance/create/', views.ApplianceCreateView.as_view(), name='appliance_create'),
    path('appliance/<int:pk>', views.ApplianceUpdateView.as_view(), name='appliance_update'),
]
