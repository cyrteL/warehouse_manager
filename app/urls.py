from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'app'

urlpatterns = [
    path('', login_required(views.WareListView.as_view()), name='list'),
    path('<int:pk>/update/', login_required(views.WareUpdateView.as_view()), name='update'),
    path('upload/', views.WareExcelUploadView.as_view(), name='upload'),
path('get-rooms-by-housing/<int:housing_id>/', views.get_rooms_by_housing, name='get_rooms_by_housing'),
    path('get-locations-by-room/<int:room_id>/', views.get_locations_by_room, name='get_locations_by_room')
]
