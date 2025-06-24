import os

from django.db import models
from django.conf import settings

from wagtail.models import Site, TranslatableMixin, Orderable
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.snippets.models import register_snippet

from wagtail_color_panel.fields import ColorField
from wagtail_color_panel.edit_handlers import NativeColorPanel

from modelcluster.models import ClusterableModel, ParentalKey


# def geojson_upload_path(instance, filename):
#     return os.path.join(
#         "project_polygons",
#         instance.site.hostname if instance.site else "default",
#         filename,
#     )


class MapPolygon(TranslatableMixin, ClusterableModel):
    title = models.CharField(max_length=255, blank=True, null=True)
    description = RichTextField(blank=True)

    site = models.ForeignKey(
        Site,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="project_polygons",
    )

    class Meta:
        verbose_name = "Map polygon"
        verbose_name_plural = "Map polygons"
        constraints = [
            models.UniqueConstraint(
                fields=["translation_key", "locale"],
                name="unique_translation_key_locale_maps_mappolygon",
            )
        ]

    def __str__(self):
        return self.title


class MapPolygonItem(Orderable):
    """
    Represents an individual polygon item associated with a MapPolygon.

    Each MapPolygonItem links to a GeoJSON document (uploaded via Wagtail Documents) that should contain a single polygon. 
    It allows for optional override of the polygon's title and description, and supports linking to an external URL or a Wagtail page.

    Fields:
        polygon (ParentalKey): Reference to the parent MapPolygon.
        title (CharField): Optional title to override the document name.
        description (RichTextField): Optional rich text description for the polygon.
        link_url (URLField): Optional external URL associated with the polygon.
        linked_page (ForeignKey): Optional link to a Wagtail page.
        geojson_document_file (ForeignKey): Reference to the uploaded GeoJSON document file containing the polygon geometry.

    Panels:
        - geojson_document_file: Upload/select the GeoJSON file.
        - description, linked_page, link_url: Additional metadata fields grouped together.

    Meta:
        verbose_name: Human-readable singular name for the model.
        verbose_name_plural: Human-readable plural name for the model.
    """
    polygon = ParentalKey(
        "MapPolygon", related_name="polygon_items", on_delete=models.CASCADE
    )
    polygon_colour =ColorField(blank=True, null=True, help_text="Overrides the polygon colour.")

    title = models.CharField(max_length=255, blank=True, null=True, help_text="Overrides the document name as the title.")
    description = RichTextField(
        blank=True,
    )
    link_url = models.URLField(null=True, blank=True)
    linked_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    # GeoJSON file uploaded via Wagtail Documents
    geojson_document_file = models.ForeignKey(
        settings.WAGTAILDOCS_DOCUMENT_MODEL,
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Note: Polygon files should only contain a single polygon, if more than one polygon exists in the file they will share the same title and description is used.",
    )

    panels = [
        MultiFieldPanel([
            FieldPanel("geojson_document_file"),
            NativeColorPanel("polygon_colour"),
        ],),
        #FieldPanel("title"),
        MultiFieldPanel([
            FieldPanel("description"),
            FieldPanel("linked_page"),
            FieldPanel("link_url"),
        ],)
    ]

    class Meta:
        # ordering = ["sort_order"]
        verbose_name = "Map polygon item"
        verbose_name_plural = "Map polygon items"
