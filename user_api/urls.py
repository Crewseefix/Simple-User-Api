from django.contrib import admin
from django.urls import path
from user_api import views

urlpatterns = [
    path('user/', views.UserListAndCreate.as_view()),
    path('user/<int:id>/', views.UserDetailsAndUpdate.as_view()),
    path('user/updates/', views.MultipleUsersUpdate.as_view()),
    path('user/createdeleteandupdate/', views.MultipleUsersCreateUpdateAndDelete.as_view())
]