from django import template

from utils.utils import format_npr_amount


register = template.Library()
register.filter('npr_amount', format_npr_amount)
