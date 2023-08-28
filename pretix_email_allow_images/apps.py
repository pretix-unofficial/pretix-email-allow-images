from django.utils.translation import gettext_lazy

from . import __version__

try:
    from pretix.base.plugins import PluginConfig
except ImportError:
    raise RuntimeError("Please use pretix 2.7 or above to run this plugin!")


class PluginApp(PluginConfig):
    default = True
    name = "pretix_email_allow_images"
    verbose_name = "Allow images in emails"

    class PretixPluginMeta:
        name = gettext_lazy("Allow images in emails")
        author = "pretix team"
        description = gettext_lazy(
            "Allow images in organizer-generated email templates"
        )
        visible = True
        version = __version__
        category = "CUSTOMIZATION"
        compatibility = "pretix>=2023.6.0"

    def ready(self):
        from . import signals  # NOQA
