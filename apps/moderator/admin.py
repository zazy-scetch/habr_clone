from django.contrib import admin
from .models import Moderator, BannedUser, ComplainToComment, VerifyArticle

admin.site.register(Moderator)
admin.site.register(BannedUser)
admin.site.register(ComplainToComment)
admin.site.register(VerifyArticle)

