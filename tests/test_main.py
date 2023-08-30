import pytest
from datetime import timedelta
from django.utils.timezone import now
from django_scopes import scopes_disabled
from pretix.base.models import Event, Organizer

from pretix_email_allow_images.signals import ClassicMailRendererWithImgs


@pytest.mark.django_db
@scopes_disabled()
def test_markdown_img():
    organizer = Organizer.objects.create(name="Dummy", slug="dummy")
    event = Event.objects.create(
        organizer=organizer,
        name="Dummy",
        slug="dummy",
        date_from=now(),
        date_admission=now() - timedelta(hours=1),
        date_to=now() + timedelta(hours=1),
        testmode=True,
    )
    renderer = ClassicMailRendererWithImgs(event)

    source = "![my image](https://example.org/my-image.jpg)"
    html = renderer.render(
        plain_body=source,
        plain_signature="",
        subject="Hello",
        order=None,
        position=None,
    )

    assert '<img alt="my image" src="https://example.org/my-image.jpg">' in html
