# Python Standard Library Imports
import random
import time

# HTK Imports
from htk.lib.fullcontact.api import (
    FullContactAPIV2,
    FullContactAPIV3,
)
from htk.utils import (
    chunks,
    htk_setting,
)
from htk.utils.emails import is_bad_email


def get_full_contact_api_v3_key():
    """Retrieves a FullContact API key
    """
    api_keys = htk_setting('HTK_FULLCONTACT_API_V3_KEYS')
    api_key = random.choice(api_keys)
    return api_key


def get_full_contact_api_v3():
    api_key = get_full_contact_api_v3_key()
    api = FullContactAPIV3(api_key)
    return api


def get_full_contact_api_v2_key():
    """Retrieves a FullContact API key
    """
    api_keys = htk_setting('HTK_FULLCONTACT_API_V2_KEYS')
    api_key = random.choice(api_keys)
    return api_key


def get_full_contact_api_v2():
    api_key = get_full_contact_api_v2_key()
    api = FullContactAPIV2(api_key)
    return api


def find_person_by_email(email):
    """Retrieve a person object by `email`
    """
    if is_bad_email(email):
        person = None
    else:
        api = get_full_contact_api_v3()
        person = api.get_person(email)
    return person


def find_valid_emails(emails):
    """Returns a subset of `emails` that are valid
    """
    api = get_full_contact_api_v2()
    all_valid_emails = []
    for chunk in chunks(emails, 20):
        persons = api.get_persons(chunk)
        valid_emails = list(persons.keys())
        all_valid_emails += valid_emails
        time.sleep(1)
    return all_valid_emails
