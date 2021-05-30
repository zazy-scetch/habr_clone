from django.urls import path

import apps.articles.views as main_page

app_name = "articles"

urlpatterns = [
    path("", main_page.main_page, name="main_page"),
    path("all/", main_page.main_page, name="all_hubs"),
    path("<int:page>/", main_page.main_page, name="articles_page"),
    path("article/<int:pk>/", main_page.article, name="article"),
    path("hub/<int:pk>/", main_page.hub, name="hub"),
    path("hub/<int:pk>/<int:page>", main_page.hub, name="articles_hub_pag"),
    path("ajax/change_rate/", main_page.change_article_rate, name="ajax_change_rate"),
    path("ajax/rate_author/", main_page.like_dislike_author_ajax, name="ajax_rate_author"),
    path("author/<int:pk>/", main_page.show_author_profile, name="author_profile"),
    path('search/<int:page>/', main_page.search_articles, name='search_articles'),
    path("sorted_articles/<int:page>/", main_page.post_list, name='sorted_articles'),
    path("sorted_articles/<int:pk>/<int:page>/", main_page.post_list, name='sorted_articles_hub'),
    path("sorted_articles_user/<int:user_pk>/<int:page>/", main_page.post_list_user, name='sorted_articles_user'),
    path("sorted_articles_search/<int:page>/", main_page.post_list_search, name='sorted_articles_search'),
    path("notifications/viewed/all/", main_page.mark_all_as_viewed, name='all_viewed'),
    path("notifications/viewed/<str:target>/<int:pk>/", main_page.target_mark_as_viewed, name='target_viewed'),
]
