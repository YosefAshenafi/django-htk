# Python Standard Library Imports
import subprocess

# Django Imports
from django.db import models

# HTK Imports
from htk.apps.i18n.utils.choices import get_language_code_choices
from htk.models import HtkBaseModel
from htk.utils import (
    htk_setting,
    resolve_model_dynamically,
)


class AbstractLocalizableString(HtkBaseModel):
    """A localizable string is a string that can be localized to a different language.

    It contains metadata about the string, but has no string representations itself.
    """

    key = models.CharField(max_length=128, unique=True)
    context = models.CharField(max_length=128, blank=True)
    description = models.CharField(max_length=256, blank=True)

    class Meta:
        abstract = True
        verbose_name = 'Localizable String'
        ordering = ('key',)

    def __str__(self):
        value = self.key
        return value

    def json_encode(self, include_key=True):
        value = {}
        if include_key:
            value.update(
                {
                    'key': self.key,
                }
            )

        value.update(
            {
                'translations': {
                    translation.language_code: translation.value
                    for translation in self.translations.order_by(
                        'language_code'
                    )
                },
            }
        )
        return value

    def key_without_namespaces(self, namespaces=None):
        if namespaces is None:
            key = self.key
        else:
            key = self.key
            for namespace in namespaces:
                if key.startswith(f'{namespace}.'):
                    key = key.removeprefix(f'{namespace}.')
                    break

        return key

    def add_translation(self, language_code, value, update=False):
        """Adds a translation for this `LocalizableString`

        - `language_code` is the ISO 639-1 language code combined with the ISO 3166-2 country code.
        - `value` is the localized translation
        - `update` when `True` updates an existing translation even if one already exists for the `language_code`;
           otherwise, only adds a new translation
        """
        LocalizedString = resolve_model_dynamically(
            htk_setting('HTK_LOCALIZED_STRING_MODEL')
        )
        localized_string, was_created = LocalizedString.objects.get_or_create(
            localizable_string=self,
            language_code=language_code,
        )
        if was_created or update:
            localized_string.value = value
            localized_string.save()

        return localized_string

    def is_instrumented(self):
        """Determines whether this localizable string is actually instrumented in the codebase.

        Checks against `HTK_ADMINTOOLS_LOCALIZATION_USAGE_CHECKS`

        This helps to determine if there are any orphaned translations.

        Returns:
        - `True` if it is instrumented
        - `False` if no instrumentations in the codebase are detected
        """
        is_instrumented = False  # guilty until proven innocent

        l10n_usage_checks = htk_setting(
            'HTK_ADMINTOOLS_LOCALIZATION_USAGE_CHECKS'
        )
        for l10n_usage_check in l10n_usage_checks:
            result = subprocess.run(
                [
                    'grep',
                    '-R',  # recursive
                    self.key_without_namespaces(
                        namespaces=l10n_usage_check.namespaces
                    ),
                    l10n_usage_check.directory,
                ],
                capture_output=True,
            )

            is_instrumented = len(result.stdout) > 0
            if is_instrumented:
                break

        return is_instrumented


class AbstractLocalizedString(HtkBaseModel):
    """A localized string is one that is associated with a localizable string, and has already been translated to a local language.

    The `language_code` is the ISO 639-1 language code combined with the ISO 3166-2 country code.

    See:
    - https://www.iso.org/iso-639-language-codes.html
    - https://en.wikipedia.org/wiki/ISO_639
    - https://en.wikipedia.org/wiki/ISO_639-1
    - https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
    - https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes

    Examples:
    - en-US - US English
    - en-UK - British English
    - zh-TW - Chinese Traditional (Taiwan)
    - zh-CN - Chinese Simplified (Mainland China)

    """

    localizable_string = models.ForeignKey(
        htk_setting('HTK_LOCALIZABLE_STRING_MODEL'),
        on_delete=models.CASCADE,
        related_name='translations',
    )
    language_code = models.CharField(
        max_length=5,
        choices=get_language_code_choices(),
        db_index=True,
    )  # '<ISO 639-1>-<ISO 3166-2>'
    value = models.TextField(max_length=512, blank=True)

    class Meta:
        abstract = True
        verbose_name = 'Localized String'
        ordering = (
            'localizable_string__key',
            'language_code',
        )
        unique_together = (
            (
                'localizable_string',
                'language_code',
            ),
        )

    def __str__(self):
        value = '{} - {}'.format(self.key, self.language_code)
        return value

    @property
    def key(self):
        return self.localizable_string.key

    def key_without_namespaces(self, namespaces=None):
        return self.localizable_string.key_without_namespaces(
            namespaces=namespaces
        )
