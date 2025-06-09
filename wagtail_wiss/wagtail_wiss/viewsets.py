from django.utils.translation import gettext as _

from wagtail.snippets.views.snippets import SnippetViewSet
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel

from .snippets.models import Category, Menu, Gallery, NewsItem, VideoHeader


class CategoryViewSet(SnippetViewSet):
    model = Category
    list_display = ["name", "locale"]
    search_fields = ["name"]
    panels = [
        FieldPanel("name"),
    ]
    ordering = ["name"]


class MenuViewSet(SnippetViewSet):
    model = Menu
    panels = [
        FieldPanel("name"),
        InlinePanel("menu_items", label="Menu Items"),
    ]


class GalleryViewSet(SnippetViewSet):
    model = Gallery
    panels = [
        FieldPanel("title"),
        FieldPanel("number_of_columns"),
        FieldPanel("caption_option"),
        InlinePanel("gallery_items", label="Gallery items", max_num=6),
    ]
    search_fields = ["title"]
    ordering = ["title"]

    class Meta:
        verbose_name = "Gallery item"


class NewsItemViewSet(SnippetViewSet):
    model = NewsItem
    panels = [
        FieldPanel("title"),
        FieldPanel("category"),  # Allow assigning a category
        FieldPanel("expiry_date"),  # Allow setting an expiry date
        FieldPanel("body"),
    ]
    icon = "doc-full"  # Choose a relevant Wagtail icon
    menu_label = "News item"
    menu_order = 200
    add_to_admin_menu = False
    list_display = ["title", "category", "expiry_date", "published_at", "locale"]
    search_fields = ["title", "body"]
    ordering = ["published_at", "title"]
    list_filter = ["title"]

    def __str__(self):
        return self.title


class VideoHeaderViewSet(SnippetViewSet):
    model = VideoHeader
    panels = [
        FieldPanel("title"),
        FieldPanel("text"),
        FieldPanel("video"),  # Allow setting a video
        FieldPanel("video_poster"),  # Allow setting a video poster
        MultiFieldPanel(
            [
                FieldPanel("controls"),
                FieldPanel("autoplay"),
                FieldPanel("muted"),
                FieldPanel("loop"),
            ]
        ),
    ]
    search_fields = ["title"]
    ordering = ["title"]

    list_display = ["title", "video", "video_poster", "locale"]
    list_filter = ["title", "locale"]
