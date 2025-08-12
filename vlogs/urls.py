from django.urls import path
from .views import VlogListView, VlogDetailView, AboutView


app_name = 'vlogs'

urlpatterns = [
    path('', VlogListView.as_view(), name='index'),
    path('about/', AboutView.as_view(), name='about'),
    path('<slug:slug>/', VlogDetailView.as_view(), name='detail'),
]


