# Django Imports
from django.conf import settings

# HTK Imports
from htk.apps.accounts.utils.social_utils import get_social_auth_for_user
from htk.lib.yahoo.sports.fantasy.client import YahooFantasySportsAPIClient


def get_yahoo_fantasy_sports_client_for_user(user):
    """Gets a YahooFantasySportsAPIClient instance for `user`
    """
    social = get_social_auth_for_user(user, 'yahoo-oauth')
    if social:
        client = YahooFantasySportsAPIClient(
            app_secret=settings.SOCIAL_AUTH_YAHOO_OAUTH_SECRET,
            app_key=settings.SOCIAL_AUTH_YAHOO_OAUTH_KEY,
            user_social_auth=social
        )
    else:
        client = None
    return client
