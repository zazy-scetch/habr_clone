from apps.articles.models import Hub


def get_all_hubs(request):
    """
    Returns all hubs as dict
    """
    hubs_menu = []
    hubs = Hub.objects.all()
    for itm in hubs:
        itm_menu = {"id": itm.id, "hub": itm.hub}
        hubs_menu.append(itm_menu)
    return {
        "hubs_menu": hubs_menu,
    }
