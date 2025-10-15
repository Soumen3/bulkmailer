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
  path('contacts/', views.contacts_list_view, name='contacts_list'),
  path('contact/<int:contact_id>/delete/', views.delete_contact_view, name='delete_contact'),
  path('group/create/', views.create_group_view, name='create_group'),
  path('groups/', views.groups_list_view, name='groups_list'),
  path('group/<int:group_id>/', views.group_detail_view, name='group_detail'),
  path('group/<int:group_id>/delete/', views.delete_group_view, name='delete_group'),
  path('group/<int:group_id>/remove/<int:contact_id>/', views.remove_contact_from_group, name='remove_contact_from_group'),
  path('template/create/', views.create_template_view, name='create_template'),
  path('templates/', views.templates_list_view, name='templates_list'),
  path('template/<int:template_id>/', views.template_detail_view, name='template_detail'),
  path('campaign/<int:campaign_id>/send/', views.send_campaign_view, name='send_campaign'),
]
