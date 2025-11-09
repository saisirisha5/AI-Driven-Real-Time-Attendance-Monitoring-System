from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('logout/', views.admin_logout, name='admin_logout'),
    path('homepage/', views.homepage, name='homepage'),
    path('view_attendance/', views.view_attendance, name='view_attendance'),
    path('add_face/', views.add_face, name='add_face'),
    path('students/', views.view_students, name='view_students'),
    path('student/<str:name>/', views.student_detail, name='student_detail'), 
    path('students/edit/<str:regd_no>/', views.edit_student, name='edit_student'),
    path('students/delete/<str:regd_no>/', views.delete_student, name='delete_student'),
]
