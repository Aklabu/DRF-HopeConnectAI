from django.urls import path
from .views import AlertListView, AlertDetailView

app_name = 'alerts'

urlpatterns = [
    path('', AlertListView.as_view(), name='alert-list'),
    path('<uuid:alert_id>/', AlertDetailView.as_view(), name='alert-detail'),
]