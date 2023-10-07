from . import views

from django.urls import path

urlpatterns = [
    # Create, Read, Delete, Update operations for all penalties
    path("", views.PenaltyList.as_view(), name="penalty_list"),
    # Read, Delete, Update operations for a specific penalty
    path("<int:penaltyId>/", views.PenaltyDetail.as_view(), name="penalty_detail"),
]
