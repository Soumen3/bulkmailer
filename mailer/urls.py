from django.urls import path 
from . import views

urlpatterns=[
  path('', views.home, name='home'),
  path('signup/', views.signup_view, name='signup'),
  path('login/', views.login_view, name='login'),
  path('logout/', views.logout_view, name='logout'),
  path('dashboard/', views.dashboard_view, name='dashboard'),
  path('campaign/create/', views.create_campaign_view, name='create_campaign'),
  path('contacts/import/', views.import_contacts_view, name='import_contacts'),
  path('group/create/', views.create_group_view, name='create_group'),
  path('campaign/<int:campaign_id>/send/', views.send_campaign_view, name='send_campaign'),
]
