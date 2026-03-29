BLOCKED = [
"/course-materials",
"/node/",
"/photo-gallery",
"/taxonomy",
"/privacy",
"/terms",
"/disclaimer",
"/404",
"/forbidden",
"/cdn-cgi/"
]


def valid_url(url):

    if any(b in url for b in BLOCKED):
        return False

    image_exts = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp')
    lower_url = url.lower().split('?')[0]
    if lower_url.endswith(image_exts):
        return False

    return True