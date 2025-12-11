from django.urls import path
from .views import (
    CustomTokenObtainPairView, SerialRecoveryView, 
    TemporaryCreationView, FinalActivationView, 
    ReactivationView, RechargeByCodeView, WalletStatusView
)

urlpatterns = [
    # المصادقة والتفعيل
    path('auth/temporary-create/', TemporaryCreationView.as_view(), name='temporary_create'),
    path('auth/final-activate/', FinalActivationView.as_view(), name='final_activate'),
    path('auth/reactivate/', ReactivationView.as_view(), name='reactivate'),
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='auth_login'),
    path('auth/recover-serial/', SerialRecoveryView.as_view(), name='recover_serial'),
    
    # المحفظة
    path('wallet/recharge-by-code/', RechargeByCodeView.as_view(), name='recharge_by_code'),
    path('wallet/status/', WalletStatusView.as_view(), name='wallet_status'),
]