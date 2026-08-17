from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'app'

urlpatterns = [
    path('', login_required(views.WareListView.as_view()), name='list'),
    path('<int:pk>/update/', login_required(views.WareUpdateView.as_view()), name='update'),
]
