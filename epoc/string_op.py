import string 

_allowed_characters = string.ascii_letters + string.digits + '_'

def sanitize_label(text):
    return ''.join([c for c in text if c in _allowed_characters])
