# Register your receivers here
import bleach
import markdown
from bleach.linkifier import DEFAULT_CALLBACKS
from css_inline import css_inline
from django.db.models import Count
from django.dispatch import receiver
from django.template.loader import get_template
from django.utils.translation import get_language, gettext_lazy as _
from itertools import groupby
from pretix import settings
from pretix.base.email import BaseHTMLMailRenderer
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


class TemplateBasedMailRendererWithImgs(BaseHTMLMailRenderer):
    @property
    def template_name(self):
        raise NotImplementedError()

    def render(
        self, plain_body: str, plain_signature: str, subject: str, order, position
    ) -> str:
        body_md = markdown_compile_email_allow_imgs(plain_body)
        htmlctx = {
            "site": settings.PRETIX_INSTANCE_NAME,
            "site_url": settings.SITE_URL,
            "body": body_md,
            "subject": str(subject),
            "color": settings.PRETIX_PRIMARY_COLOR,
            "rtl": get_language() in settings.LANGUAGES_RTL
            or get_language().split("-")[0] in settings.LANGUAGES_RTL,
        }
        if self.organizer:
            htmlctx["organizer"] = self.organizer

        if self.event:
            htmlctx["event"] = self.event
            htmlctx["color"] = self.event.settings.primary_color

        if plain_signature:
            signature_md = plain_signature.replace("\n", "<br>\n")
            signature_md = markdown_compile_email_allow_imgs(signature_md)
            htmlctx["signature"] = signature_md

        if order:
            htmlctx["order"] = order
            positions = list(
                order.positions.select_related(
                    "item", "variation", "subevent", "addon_to"
                ).annotate(has_addons=Count("addons"))
            )
            htmlctx["cart"] = [
                (k, list(v))
                for k, v in groupby(
                    sorted(
                        positions,
                        key=lambda op: (
                            (
                                op.addon_to.positionid
                                if op.addon_to_id
                                else op.positionid
                            ),
                            op.positionid,
                        ),
                    ),
                    key=lambda op: (
                        op.item,
                        op.variation,
                        op.subevent,
                        op.attendee_name,
                        op.addon_to_id,
                        (op.pk if op.has_addons else None),
                    ),
                )
            ]

        if position:
            htmlctx["position"] = position
            htmlctx["ev"] = position.subevent or self.event

        tpl = get_template(self.template_name)
        body_html = tpl.render(htmlctx)

        inliner = css_inline.CSSInliner(remove_style_tags=True)
        body_html = inliner.inline(body_html)

        return body_html


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
