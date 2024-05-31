def validate_not_url(url):
    return isinstance(url, str) and not url.startswith(("http:", "https:"))


def validate_image(image):
    if not validate_not_url(image):
        raise ValueError("image must be a base64 encoded image")


def validate_audio(audio):
    if not validate_not_url(audio):
        raise ValueError("audio must be a base64 encoded audio")
