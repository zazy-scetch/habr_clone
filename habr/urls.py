from ckeditor_uploader.views import upload
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path, include

urlpatterns = [
    path("", include("apps.articles.urls", namespace="articles")),
    path("account/", include("apps.account.urls", namespace="account")),
    path("auth/", include("apps.authorization.urls", namespace="auth")),
    path("admin/", admin.site.urls, name="admin"),
    path("comments/", include("apps.comments.urls", namespace="comments")),
    path("ckeditor/", include("ckeditor_uploader.urls")),
    path("upload/", login_required(upload), name="ckeditor_upload"),
    path('oauth/', include("social_django.urls", namespace="social")),
    path("moderator/", include("apps.moderator.urls", namespace="moderator")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
