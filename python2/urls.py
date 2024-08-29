from django.urls import path

from plan import api

app_name = "plan"

urlpatterns = [
    path("", api.ProgramAPIView.as_view(), name="program-list"),
    path("<uuid:pk>/", api.ProgramDetailAPIView.as_view(),
         name="program-detail"),
]
