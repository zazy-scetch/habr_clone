import urllib
from datetime import datetime
from urllib.parse import urlunparse, urlencode

import requests
from django.conf import settings


from apps.authorization.models import HabrUserProfile, HabrUser


def save_user_profile(backend, user, response, *args, **kwargs):
    if backend.name == 'vk-oauth2':
        api_url = urlunparse(('https',
                              'api.vk.com',
                              '/method/users.get',
                              None,
                              urlencode(dict(fields=','.join(('first_name', 'last_name', 'career', 'email',
                                                              'sex', 'bdate', 'country', 'city', 'photo_max_orig')),
                                             access_token=response['access_token'],
                                             v='5.92')),
                              None
                              ))
        response = requests.get(api_url)
        if response.status_code != 200:
            return
        data = response.json()['response'][0]
        user.is_confirmed = True
        if data.get('first_name'):
            user.habruserprofile.first_name = data["first_name"]
        if data.get('last_name'):
            user.habruserprofile.last_name = data["last_name"]
        if data.get('career'):
            user.habruserprofile.place_of_work = data['career'][-1]['company']
            user.habruserprofile.specialization = data['career'][-1]['position']
        if data.get('sex'):
            user.habruserprofile.gender = HabrUserProfile.MALE if data['sex'] == 2 else HabrUserProfile.FEMALE
        if data.get('bdate'):
            user.habruserprofile.birth_date = datetime.strptime(data['bdate'], '%d.%m.%Y').date()
        if data.get('country'):
            user.habruserprofile.country = data['country']['title']
        if data.get('city'):
            user.habruserprofile.city = data['city']['title']
        if data.get('photo_max_orig'):
            urllib.request.urlretrieve(data['photo_max_orig'], f'{settings.MEDIA_ROOT}/avatars/{user.pk}.jpg')
            user.habruserprofile.avatar = f'avatars/{user.pk}.jpg'
        user.save()
    elif backend.name == 'google-oauth2':
        user.is_confirmed = True
        if response.get('given_name'):
            user.habruserprofile.first_name = response['given_name']
        if response.get('family_name'):
            user.habruserprofile.last_name = response['family_name']
        if response.get('picture'):
            urllib.request.urlretrieve(response['picture'], f'{settings.MEDIA_ROOT}/avatars/{user.pk}.jpg')
            user.habruserprofile.avatar = f'avatars/{user.pk}.jpg'
        user.save()
    elif backend.name == 'github':
        user.is_confirmed = True
        if response.get('name'):
            user.habruserprofile.first_name = response['name']
        if response.get('avatar_url'):
            urllib.request.urlretrieve(response['avatar_url'], f'{settings.MEDIA_ROOT}/avatars/{user.pk}.jpg')
            user.habruserprofile.avatar = f'avatars/{user.pk}.jpg'
        user.save()
    else:
        return
