from django.urls import path
from . import views

app_name = 'lease'

urlpatterns = [
    path('', views.home, name='home'),
    
    # Employee
    path('request/', views.request_lease, name='request_lease'),
    path('my-requests/', views.my_requests, name='my_requests'),
    path('s3-data/', views.s3_data, name='s3_data'),
    path('s3-write/', views.s3_write, name='s3_write'),

    # Admin
    path('pending/', views.pending_requests, name='pending_requests'),
    path('approved/', views.approved_requests, name='approved_requests'),
    path('rejected/', views.rejected_requests, name='rejected_requests'),
    path('approve/<int:lease_id>/', views.approve_lease, name='approve_lease'),
    
    path('download/<str:obj_name>/', views.download_file, name='download_file'),
    path('delete/<str:obj_name>/', views.delete_file, name='delete_file'),
    path('my-requests/', views.my_requests, name='my_requests'),
    
]
