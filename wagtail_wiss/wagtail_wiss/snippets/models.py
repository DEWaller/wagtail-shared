import logging

from django.conf import settings

from django.db import models
from django.db import transaction
from django.utils import timezone
from datetime import datetime, time, timedelta

from wagtail.models import Site, Orderable, TranslatableMixin
from wagtail.admin.panels import FieldPanel
from wagtail.search import index
from wagtail_localize.fields import TranslatableField
from wagtail.fields import RichTextField

from modelcluster.models import ClusterableModel, ParentalKey

logger = logging.getLogger(__name__)


class VideoHeader(TranslatableMixin, models.Model):
    title = models.CharField(max_length=255, blank=False, null=True)

    text = RichTextField(blank=True, null=True)
    video = models.ForeignKey(
        settings.WAGTAILDOCS_DOCUMENT_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Please upload an .mp4 file only.",
    )
    video_poster = models.ForeignKey(
        settings.WAGTAILIMAGES_IMAGE_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Poster image",
    )

    controls = models.BooleanField(
        default=True,
        help_text="If checked, the video will display controls. If unchecked, it will not.",
    )

    autoplay = models.BooleanField(
        default=False,
        help_text="If checked, the video will autoplay. If unchecked, it will not. It's important to note that due to restrictions in some browsers, particularly Chromium-based ones, videos with autoplay may not always start playing upon loading unless they are muted.",
    )

    loop = models.BooleanField(
        default=False,
        help_text="If checked, the video will loop. If unchecked, it will not.",
    )

    muted = models.BooleanField(
        default=False,
        help_text="If checked, the video will be muted. If unchecked, it will not.",
    )

    translateable_fields = ["title", "text"]

    def __str__(self):
        return self.title

    class Meta(TranslatableMixin.Meta):
        verbose_name = "Page banner"
        verbose_name_plural = "Page banners"


class Category(TranslatableMixin, models.Model):
    name = models.CharField(max_length=255, blank=False, null=True)

    translatable_fields = [
        TranslatableField("name"),
    ]

    def __str__(self):
        return self.name

    class Meta(TranslatableMixin.Meta):
        verbose_name = "Category"
        verbose_name_plural = "Categories"


class Menu(ClusterableModel):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Flat Menu"
        verbose_name_plural = "Flat Menus"

    def __str__(self):
        return self.name


class MenuItem(Orderable):
    menu = ParentalKey("Menu", related_name="menu_items")
    name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Display name",
        help_text="This field overrides the page title, if set, but is required for a link url.",
    )
    link_url = models.CharField(max_length=500, blank=True, null=True)
    page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.SET_NULL,
    )
    show_children = models.BooleanField(default=False)

    panels = [
        FieldPanel("name"),
        FieldPanel("link_url"),
        FieldPanel("page"),
        FieldPanel("show_children"),
    ]

    def save(self, *args, **kwargs):
        # Call the original save method to ensure the MenuItem is saved
        super().save(*args, **kwargs)

        # Update show_in_menus on the associated page if a page is linked
        if self.page:
            with transaction.atomic():
                self.page.show_in_menus = True
                self.page.save()

            # If show_children is True, ensure all child pages also show in menus
            if self.show_children:
                child_pages = self.page.get_children().live()  # Fetch live child pages
                child_pages.update(
                    show_in_menus=True
                )  # Set show_in_menus=True for each child page

    def get_child_pages(self):
        """Return child pages if show_children is enabled."""
        if self.show_children and self.page:
            return self.page.get_children().live().filter(show_in_menus=True)
        return []

    def __str__(self):
        return (
            f"{self.menu.name}: {self.name}"
            if self.menu
            else "Menu item not associated with a menu"
        )

    class Meta:  # noqa: D106
        ordering = ["sort_order"]
        verbose_name = "Menu item"
        verbose_name_plural = "Menu items"


class Gallery(index.Indexed, ClusterableModel):
    title = models.CharField(max_length=255)

    number_of_columns = models.PositiveIntegerField(
        default=0,
        choices=[(i, f"{i} column" if i == 1 else f"{i} columns") for i in range(0, 7)],
        help_text="Select the number of columns for the gallery grid. Choose 0 to let images flow freely.",
    )

    caption_option = models.BooleanField(
        default=False,
        help_text="Display caption below each image rather than as an overlay.",
    )

    search_fields = [
        index.AutocompleteField("title"),
        index.SearchField("title"),
    ]

    class Meta:
        verbose_name = "Gallery"
        verbose_name_plural = "Galleries"

    def __str__(self):
        return self.title


class GalleryItem(Orderable):
    gallery = ParentalKey(
        "Gallery", related_name="gallery_items", on_delete=models.CASCADE
    )
    # image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name="+")
    image = models.ForeignKey(
        settings.WAGTAILIMAGES_IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    text = models.CharField(max_length=255, null=True, blank=True)
    link_url = models.URLField(null=True, blank=True)
    linked_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    panels = [
        FieldPanel("image"),
        FieldPanel("text"),
        FieldPanel("linked_page"),
        FieldPanel("link_url"),
    ]

    class Meta:
        ordering = ["sort_order"]
        verbose_name = "Gallery item"
        verbose_name_plural = "Gallery items"


class News(index.Indexed, ClusterableModel):
    title = models.CharField(max_length=255)

    search_fields = [
        index.AutocompleteField("title"),
        index.SearchField("title"),
    ]

    class Meta:
        verbose_name = "News"
        verbose_name_plural = "News"

    def __str__(self):
        return self.title


def default_expiry_date():
    # Get current date + 10 years
    future_date = timezone.now().date() + timedelta(days=10 * 365)

    # Combine future_date with midnight time (00:00:00)
    return timezone.make_aware(datetime.combine(future_date, time.min))


class NewsItem(TranslatableMixin, ClusterableModel):
    title = models.CharField(max_length=255)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="news_items"
    )
    body = RichTextField()
    published_at = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(
        null=True, blank=True, default=default_expiry_date
    )
    archive = models.BooleanField(default=False)  # New field to archive items
    sort_order = models.PositiveIntegerField(default=0, blank=False, null=False)

    panels = [
        FieldPanel("title"),
        FieldPanel("category"),
        FieldPanel("expiry_date"),
        FieldPanel("body"),
        FieldPanel("archive"),
        FieldPanel("sort_order"),  # Add sort order field
    ]

    list_display = ["title", "published_at", "sort_order"]
    search_fields = ["title", "body"]
    ordering = ["sort_order", "-published_at"]

    def __str__(self):
        return self.title
