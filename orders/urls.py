from django.urls import path

from . import views

urlpatterns = [
    path('api/otp/send/', views.otp_send),
    path('api/otp/verify/', views.otp_verify),
    path('api/logout/', views.logout_view),
    path('api/staff/login/', views.staff_login_api),
    path('api/profile/', views.profile_save),
    path('api/profile/photo/', views.profile_photo),
    path('api/orders/', views.order_create),
    path('api/my/orders/', views.my_orders),
    path('api/order/<str:number>/', views.order_detail),
    path('api/pay/start/', views.pay_start),
    path('pay/mock/<str:authority>/', views.pay_mock, name='pay_mock'),
    path('pay/callback/', views.pay_callback, name='pay_callback'),
    path('order/<str:number>/invoice.pdf', views.invoice_pdf, name='invoice_pdf'),
    path('worker/', views.worker_home, name='worker_home'),
    path('worker/login/', views.worker_login, name='worker_login'),
    path('worker/logout/', views.worker_logout, name='worker_logout'),
    path('worker/collect/<int:pk>/', views.worker_collect, name='worker_collect'),
    path('worker/undo/<int:pk>/', views.worker_undo, name='worker_undo'),
    path('worker/count/', views.worker_count, name='worker_count'),
    path('driver/', views.driver_home, name='driver_home'),
    path('driver/login/', views.driver_login, name='driver_login'),
    path('driver/logout/', views.driver_logout, name='driver_logout'),
    path('driver/take/<int:pk>/', views.driver_take, name='driver_take'),
    path('driver/deliver/<int:pk>/', views.driver_deliver, name='driver_deliver'),
    path('driver/return/<int:pk>/', views.driver_return, name='driver_return'),
    path('driver/count/', views.driver_count, name='driver_count'),
]
