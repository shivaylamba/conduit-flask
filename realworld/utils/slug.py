import re

def create_slug(title):
    # Convert the title to lowercase and replace spaces with dashes
    slug = title.lower().replace(" ", "-")
    # Remove any characters that are not alphanumeric or dashes
    slug = re.sub(r"[^\w-]", "", slug)
    return slug