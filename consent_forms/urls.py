from django.urls import path
from . import views

app_name = "consents"

urlpatterns = [
    path("", views.choose_template, name="choose_template"),
    path("form/<slug:slug>/", views.fill_template, name="fill_template"),
    path("thanks/<int:pk>/", views.thank_you, name="thank_you"),
]
