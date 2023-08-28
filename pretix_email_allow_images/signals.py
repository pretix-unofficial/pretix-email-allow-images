# Register your receivers here
import bleach
import markdown
from bleach.linkifier import DEFAULT_CALLBACKS
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from pretix.base.email import TemplateBasedMailRenderer
from pretix.base.signals import register_html_mail_renderers
from pretix.base.templatetags.rich_text import (
    ALLOWED_ATTRIBUTES,
    ALLOWED_PROTOCOLS,
    ALLOWED_TAGS,
    EMAIL_RE,
    URL_RE,
    EmailNl2BrExtension,
    LinkifyAndCleanExtension,
    abslink_callback,
    truelink_callback,
)


def markdown_compile_email_allow_imgs(source):
    linker = bleach.Linker(
        url_re=URL_RE,
        email_re=EMAIL_RE,
        callbacks=DEFAULT_CALLBACKS + [truelink_callback, abslink_callback],
        parse_email=True,
    )
    return markdown.markdown(
        source,
        extensions=[
            "markdown.extensions.sane_lists",
            EmailNl2BrExtension(),
            LinkifyAndCleanExtension(
                linker,
                tags=ALLOWED_TAGS + ["img"],
                attributes=dict(ALLOWED_ATTRIBUTES, img=["src", "alt", "title"]),
                protocols=ALLOWED_PROTOCOLS,
                strip=False,
            ),
        ],
    )


class TemplateBasedMailRendererWithImgs(TemplateBasedMailRenderer):
    def compile_markdown(self, plaintext):
        return markdown_compile_email_allow_imgs(plaintext)


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
