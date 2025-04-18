from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page is the default route
    path('products/', views.product_view, name='product_view'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('edit-product/', views.save_product_changes, name='save_product_changes'),
    path('owner/', views.owner_view, name='owner_view'),
    path('add-product/', views.add_product, name='add_product'),
    path('adjust-quantity/', views.adjust_quantity, name='adjust_quantity'),
    path('sell-product/', views.sell_product, name='sell_product'),
]

handler404 = 'freshmart.views.custom_404_view'
handler500 = 'freshmart.views.custom_500_view'
