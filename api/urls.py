from django.contrib import admin
from django.urls import path
from api import views

urlpatterns = [
    path('login',views.signin,name="Login"),
    path('register',views.signup,name="Register new user"),
    path('activate/<str:aadhar_no>',views.activate,name="Activate the aadhar card"),
    path('<str:aadhar_no>', views.each,name="List all the user's details"),
    path('', views.index,name="List all the users details"),
    path('<str:aadhar_no>/add', views.add_contact,name="Add user's contact info details"),
    path('<str:aadhar_no>/address/<int:obj_id>',views.address_view,name="User address"),
    path('<str:aadhar_no>/qualification/<int:obj_id>',views.qualification_view,name="User qualification"),
    path('<str:aadhar_no>/bank/<int:obj_id>',views.bank_view,name="User bank"),
    path('<str:aadhar_no>/experience/<int:obj_id>',views.experience_view,name="User experience"),
    path('<str:aadhar_no>/address',views.address_view,name="User address"),
    path('<str:aadhar_no>/qualification',views.qualification_view,name="User qualification"),
    path('<str:aadhar_no>/bank',views.bank_view,name="User bank"),
    path('<str:aadhar_no>/experience',views.experience_view,name="User experience"),

]
