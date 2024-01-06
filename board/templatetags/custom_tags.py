from django import template
import os
from urllib.parse import unquote

register = template.Library()

@register.filter
def get_file_name(file_path):
    return unquote(os.path.basename(file_path))