from apps.moderator.models import Moderator, BannedUser
import datetime


def check_is_staff(request):
    """
    Проверить является ли пользователь модератором.
    """
    is_staff = Moderator.objects.filter(staff=request.user.pk).exists()
    return {
        'is_staff': is_staff,
    }


def check_is_banned(request):
    """
    Проверить является ли пользователь забаненным.
    """
    remaining_days = None
    is_banned = False
    banned_user = None
    banned_user_query = BannedUser.objects.filter(offender=request.user.pk, is_active=True)
    if banned_user_query:
        is_banned = True
        banned_user = banned_user_query[0]
        if not banned_user.is_forever:
            num_days = banned_user.num_days
            date_ban = banned_user.date_ban
            end_date = date_ban + datetime.timedelta(days=num_days)
            current_date = datetime.date.today()
            remaining_days = (end_date - current_date).days
            if remaining_days <= 0:
                banned_user.is_active = False
                banned_user.save()
                banned_user.unset_ban_email()
    return {
        'is_banned': is_banned,
        'banned_user': banned_user,
        'remaining_days': remaining_days,
    }

