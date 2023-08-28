from pretix_email_allow_images.signals import markdown_compile_email_allow_imgs


def test_markdown_img():
    source = "![my image](https://example.org/my-image.jpg)"
    html = markdown_compile_email_allow_imgs(source)
    assert html == '<p><img alt="my image" src="https://example.org/my-image.jpg"></p>'
