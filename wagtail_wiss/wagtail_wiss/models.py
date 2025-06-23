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
    
    parent_page_types = []  # This means only under root
    sub_page_types = [
        "home.DefaultPage",
    ]
    
    exclude_from_sitemap = models.BooleanField(default=False)
    
    header_h1 = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="You can use | to wrap preceding text in a span element and insert a linebreak. This only applies to this text field.",
    )
    
    intro = models.TextField(blank=True)

    
    content_panels = (
        Page.content_panels
        + [
            FieldPanel("exclude_from_sitemap"),
            FieldPanel("header_h1"),
            FieldPanel("intro"),
        ]
    )
    
    class Meta:
        abstract = True # This is an abstract base class for home pages and prevents the creation of a HomePage model in the database.
    
class DefaultPage(Page):
    template = "home/default_page.html"
    
    parent_page_types = [
        "home.HomePage",
        "home.DefaultPage",
    ]

    
    exclude_from_sitemap = models.BooleanField(default=False)
    
    header_h1 = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="You can use | to wrap preceding text in a span element and insert a linebreak. This only applies to this text field.",
    )
    
    intro = models.TextField(blank=True)

    
    content_panels = (
        Page.content_panels
        + [
            FieldPanel("exclude_from_sitemap"),
            FieldPanel("header_h1"),
            FieldPanel("intro"),
        ]
    )
    
    class Meta:
        abstract = True # This is an abstract base class for default pages and prevents the creation of a DefaultPage model in the database.