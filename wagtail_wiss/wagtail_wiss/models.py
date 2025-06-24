from django.db import models

from modelcluster.models import ClusterableModel

from wagtail.models import Page
from wagtail.search import index
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.images.models import Image, AbstractImage, AbstractRendition
from wagtail.documents.models import AbstractDocument, Document

from .snippets.models import Gallery
from .blocks import (
    # ContentGridBlockWrapper,
    ParagraphBlock,
    SingleColumnBlock,
    ThreeColumnBlock,
    TwoColumnBlock,
    TwoColumnLeftSidebarBlock,
    TwoColumnRightSidebarBlock,
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

    gallery = models.ForeignKey(
        Gallery, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )

    body = StreamField(
        [
            ("single_column", SingleColumnBlock()),
            ("two_column", TwoColumnBlock()),
            ("three_columns", ThreeColumnBlock()),
            ("paragraph", ParagraphBlock()),
        ],
        null=True,
        blank=True,
    )

    content_panels = (
        Page.content_panels
        + [
            FieldPanel("exclude_from_sitemap"),
            FieldPanel("header_h1"),
            FieldPanel("gallery"),
            FieldPanel("body"),
        ]
        # + FooterOverrideMixin.footer_panels
    )

    def get_sitemap_urls(self, request=None):
        if self.exclude_from_sitemap:
            return []
        return super().get_sitemap_urls(request)

    class Meta:
        abstract = True  # This is an abstract base class for home pages and prevents the creation of a HomePage model in the database.


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

    content_panels = Page.content_panels + [
        FieldPanel("exclude_from_sitemap"),
        FieldPanel("header_h1"),
        FieldPanel("intro"),
    ]

    class Meta:
        abstract = True  # This is an abstract base class for default pages and prevents the creation of a DefaultPage model in the database.





