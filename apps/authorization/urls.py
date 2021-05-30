from django.urls import path

import apps.authorization.views as auth

app_name = "auth"

urlpatterns = [
    path("login/", auth.login, name="login"),
    path("register/", auth.register, name="register"),
    path("logout/", auth.logout, name="logout"),
    path("forgive/", auth.forgive, name="forgive"),
    path("verify/<email>/<activation_key>/", auth.verify, name='verify'),
    path("send/<pk>/", auth.send_repeat_email, name='send'),
]
