from django.urls import path
from . import views

urlpatterns = [
    path('', views.write_db),
    path('cart/', views.CartGenericApiView.as_view()),
    path('cart_delete/<int:pk>/', views.CartDestroyGenericView.as_view()),
]