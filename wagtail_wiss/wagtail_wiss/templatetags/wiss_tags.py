from django import template
from django.utils.safestring import mark_safe
from django.template.loader import get_template

from wagtail_wiss.snippets.models import Menu, MenuItem

register = template.Library()

@register.filter
def linebreak_span(value):
    # Handle None or empty values gracefully
    if not value:
        return ""
    
    if '|' in value:
        parts = value.split('|', 1)
        return mark_safe(f'<div class="index-0">{parts[0]}</div><div class="index-1">{parts[1]}</div>')
    return value


@register.simple_tag(takes_context=True)
def menu(context, menu_name, template='tags/menus/menu.html', css_class='', aria_label=''):
    try:
        menu = Menu.objects.get(name=menu_name)
        
        # Fetch and order menu items
        menu_items = menu.menu_items.filter(
            Q(page__show_in_menus=True) | Q(page__isnull=True)
        ).order_by('sort_order')  # Use sort_order for proper ordering

        # For each menu item, add child pages if `show_children` is True
        for item in menu_items:
            item.child_pages = item.get_child_pages()

    except Menu.DoesNotExist:
        menu_items = MenuItem.objects.none()
    
    request = context.get('request')  # Safely get the request object
    context.update({
        'menu_items': menu_items,
        'class': css_class,
        'aria_label': aria_label,
        'request_path': request.path,
    })
    return get_template(template).render(context.flatten())