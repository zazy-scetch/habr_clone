from django.urls import path

import apps.account.views as account

app_name = "account"

urlpatterns = [
    path("profile/", account.read_profile, name="read_profile"),
    path("articles/", account.user_articles, name="user_articles"),
    path("add_article/", account.add_article, name="add_article"),
    path("draft_article/<int:pk>/", account.draft_article, name="draft_article"),
    path("verify_article/<int:pk>/", account.verify_article, name="verify_article"),
    path("del_article/<int:pk>/", account.del_article, name="del_article"),
    path("edit_profile/", account.edit_profile, name="edit_profile"),
    path("publications/", account.publications, name="publications"),
    path("publications/<int:page>/", account.publications, name="publications_pag"),
    path("user_articles/", account.user_articles, name="user_articles"),
    path("user_articles/<int:page>/", account.user_articles, name="user_articles_pag"),
    path("draft/", account.draft, name="draft"),
    path("draft/<int:page>", account.draft, name="draft_pag"),
    path("edit_profile/edit_password/", account.edit_password, name="edit_password"),
    path("edit_article/<int:pk>/", account.edit_article, name="edit_article"),
    path("bookmarks/", account.bookmarks_page, name="bookmarks_page"),
    path("bookmarks/<int:page>/", account.bookmarks_page, name="bookmarks_paggination"),
    path("notifications/", account.notifications_page, name="notifications_page"),
    path("my_likes/", account.my_likes, name="my_likes"),
]
