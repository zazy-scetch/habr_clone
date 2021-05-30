from django.urls import path

import apps.moderator.views as moderator

app_name = "moderator"

urlpatterns = [
    path("complaints/", moderator.complaints, name="complaints"),
    path("review_articles/", moderator.review_articles, name='review_articles'),
    path("banned_users/", moderator.banned_users, name='banned_users'),
    path("add_user_ban/<int:pk>/", moderator.add_user_ban, name='add_user_ban'),
    path("remove_user_ban/<int:pk>/", moderator.remove_user_ban, name='remove_user_ban'),
    path("allow_publishing/<int:pk>/", moderator.allow_publishing, name='allow_publishing'),
    path("reject_publishing/<int:pk>/", moderator.reject_publishing, name='reject_publishing'),
    path("return_article/<int:pk>/", moderator.return_article, name='return_article'),
    path("complain_to_article/<int:pk>/", moderator.complain_to_article, name='complain_to_article'),
    path("complain_to_comment/<int:pk>/<int:pk_article>/", moderator.complain_to_comment, name='complain_to_comment'),
    path("send_complain_to_article/<int:pk>/", moderator.send_complain_to_article, name='send_complain_to_article'),
    path("send_complain_to_comment/<int:pk>/<int:pk_article>/", moderator.send_complain_to_comment, name='send_complain_to_comment'),
    path("ban_article/<int:pk>/", moderator.ban_article, name='ban_article'),
    path("no_ban_article/<int:pk>/", moderator.no_ban_article, name='no_ban_article'),
    path("ban_comment/<int:pk>/", moderator.ban_comment, name='ban_comment'),
    path("send_ban_comment/<int:pk>/", moderator.send_ban_comment, name='send_ban_comment'),
    path("no_ban_comment/<int:pk>/", moderator.no_ban_comment, name='no_ban_comment'),
]