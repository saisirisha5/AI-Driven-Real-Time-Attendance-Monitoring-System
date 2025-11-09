from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('view_attendance/', views.view_attendance, name='view_attendance'),
    path('add_face/', views.add_face, name='add_face'),
    path('student/<str:name>/', views.student_detail, name='student_detail'),  # New route
]
