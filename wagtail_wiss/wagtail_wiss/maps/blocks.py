from wagtail.blocks import StructBlock, CharBlock

class MapBlock(StructBlock):
    location_name = CharBlock(required=True)
    latitude = CharBlock(required=True)
    longitude = CharBlock(required=True)

    class Meta:
        icon = "site"
        label = "Map"
        template = "wagtail_wiss/maps/map_block.html"
