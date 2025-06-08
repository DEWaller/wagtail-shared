from django.db import models

from wagtail.models import Page



from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PublishingPanel,
)

class HomePage(Page):
    template = "home/home_page.html"
    
    exclude_from_sitemap = models.BooleanField(default=False)
    
    intro = models.TextField(blank=True)

    
    content_panels = (
        Page.content_panels
        + [
            FieldPanel("exclude_from_sitemap"),
            FieldPanel("intro"),
        ]
    )
    
class DefaultPage(Page):
    template = "home/default_page.html"
    
    exclude_from_sitemap = models.BooleanField(default=False)
    
    intro = models.TextField(blank=True)

    
    content_panels = (
        Page.content_panels
        + [
            FieldPanel("exclude_from_sitemap"),
            FieldPanel("intro"),
        ]
    )