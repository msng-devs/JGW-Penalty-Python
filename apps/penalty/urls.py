from . import views

from django.urls import path

urlpatterns = [
    # Create operation
    path("penalty/add/", views.AddPenalty.as_view(), name="add_penalty"),
    # Read, Delete, Update operations for a specific penalty
    path(
        "penalty/<int:penaltyId>/", views.PenaltyDetail.as_view(), name="penalty_detail"
    ),
    # Read, Delete, Update operations for all penalties
    path("penalty/", views.PenaltyList.as_view(), name="penalty_list"),
]
