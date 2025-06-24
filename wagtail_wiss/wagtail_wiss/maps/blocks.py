from wagtail import blocks
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail.models import Locale

from maps.models import  MapPolygon

class PolygonsBlock(blocks.StructBlock):
    
    map_polygon_collection = blocks.ListBlock(
        SnippetChooserBlock(MapPolygon, required=False), required=False
    )
    
    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        request = context.get("request")
        current_locale = Locale.get_active()

        # Grab selected polygon snippets from block value
        selected_polygons = [
            p for p in value.get("map_polygon_collection", []) if p is not None
        ]

        # Translate to current locale
        translation_keys = [p.translation_key for p in selected_polygons]
        translated_polygons = MapPolygon.objects.filter(
            translation_key__in=translation_keys,
            locale=current_locale
        ).prefetch_related("polygon_items")

        geojson_map_items = []

        for polygon in translated_polygons:
            for item in polygon.polygon_items.all():
                if item.geojson_document_file:
                    geojson_map_items.append({
                        "title": item.linked_page.title if item.linked_page else item.geojson_document_file.title or polygon.title,
                        "description": item.description or polygon.description,
                        "geojson_url": item.geojson_document_file.url,
                        "link": item.link_url or (
                            item.linked_page.url if item.linked_page else ""
                        ),
                        "colour": item.polygon_colour,       # ← just cast to string
                    })
         
        if getattr(current_locale, "language_code", None) == "cy":
            context["view_more"] = "Gweld mwy"
        else:
            context["view_more"] = "View more"
            
            
        context["geojson_map_items"] = geojson_map_items
        
        return context

    
    class Meta:
        icon = "image"
        label = "Polygon map block"
        template = "blocks/polygons_block.html"
    
# class MapPolygonPageBlock(blocks.StreamBlock):
#     polygon_collection = PolygonsBlock(
#         required=False,
#         help_text="Select the polygon collection to display on the map.",
#     )
