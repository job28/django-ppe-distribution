from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from items.views import signup
from items import views as item_views
from django.shortcuts import redirect



urlpatterns = [
    path('admin/', admin.site.urls),
    path('items/', include('items.urls')),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    #path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('accounts/signup/', signup, name='signup'),
    path('about/', item_views.about, name='about'),
    #path('accounts/logout/', include('items.urls')),  # Add this if not already present
    #path('', lambda request: redirect('home'), name='root_redirect'),
    path('', item_views.home, name='home'),  # <-- real home at '/'
    path('payment/success/', item_views.payment_success, name='payment_success'),
    path('payment/cancel/<int:order_id>/', item_views.payment_cancel, name='payment_cancel'),
    path('stripe/webhook/', item_views.stripe_webhook, name='stripe_webhook'),

]
