# Register your receivers here
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from pretix.base.email import TemplateBasedMailRenderer
from pretix.base.signals import register_html_mail_renderers
from pretix.base.templatetags.rich_text import (
    ALLOWED_ATTRIBUTES,
    ALLOWED_TAGS,
    markdown_compile_email,
)


class TemplateBasedMailRendererWithImgs(TemplateBasedMailRenderer):
    def compile_markdown(self, plaintext):
        return markdown_compile_email(
            source=plaintext,
            allowed_tags=ALLOWED_TAGS | {"img"},
            allowed_attributes=dict(ALLOWED_ATTRIBUTES, img=["src", "alt", "title"]),
        )


class ClassicMailRendererWithImgs(TemplateBasedMailRendererWithImgs):
    verbose_name = _("Default (images allowed)")
    identifier = "classic_with_imgs"
    thumbnail_filename = "pretixbase/email/thumb.png"
    template_name = "pretixbase/email/plainwrapper.html"


class UnembellishedMailRendererWithImgs(TemplateBasedMailRendererWithImgs):
    verbose_name = _("Simple with logo (images allowed)")
    identifier = "simple_logo_with_imgs"
    thumbnail_filename = "pretixbase/email/thumb_simple_logo.png"
    template_name = "pretixbase/email/simple_logo.html"


@receiver(
    register_html_mail_renderers,
    dispatch_uid="pretix_email_allow_images_email_renderers",
)
def base_renderers_with_imgs(sender, **kwargs):
    return [ClassicMailRendererWithImgs, UnembellishedMailRendererWithImgs]
