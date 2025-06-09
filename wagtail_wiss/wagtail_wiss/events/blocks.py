import math
import re

from math import radians, cos, sin, asin, sqrt

from dateutil.parser import parse as parse_date
from pagination.utils import paginate

from shared_utils.accessibility import ParagraphBlock

from wagtail import blocks
from wagtail.models import Locale
from wagtail.snippets.blocks import SnippetChooserBlock

from .models import Event, EventArea, EventsCategory, Label

def haversine(lat1, lon1, lat2, lon2):
        # Convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        r = 3956  # Radius of Earth in miles. Use 6371 for km
        rk =6371
        m=math.ceil(c*r)
        km=math.ceil(c*rk)
        return m, km  # return both miles and km

class EventsBlock(blocks.StructBlock):
    ### From Event snippets
    categories = blocks.ListBlock(
        SnippetChooserBlock(EventsCategory, required=False), required=False
    )

    @staticmethod
    def parse_wkt_point(wkt):
        """
        Extracts lat/lng from 'SRID=4326;POINT(lng lat)' format.
        Returns a tuple (lat, lng) or None if invalid.
        """
        match = re.search(r"POINT\(([-\d.]+) ([-\d.]+)\)", wkt)
        if match:
            lng = float(match.group(1))
            lat = float(match.group(2))
            return lat, lng
        return None
    
    

    def get_selected_categories(self, value):
        """
        Extract selected categories from the block's value.
        """
        # Ensure the categories field exists and filter out None values
        return [
            category for category in value.get("categories", []) if category is not None
        ]

    def get_context(self, value, parent_context=None):
        # from home.models import EventPage  # Lazy import here

        context = super().get_context(value, parent_context)
        request = context.get("request")
        current_locale = Locale.get_active()

        if not request:
            raise ValueError("Request object is missing in the context.")

        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        start_date = parse_date(start_date).date() if start_date else None
        end_date = parse_date(end_date).date() if end_date else None

        area_ids = [int(a) for a in request.GET.getlist("areas") if a.isdigit()]

        if area_ids:
            selected_areas = EventArea.objects.filter(id__in=area_ids)

            selected_translation_keys = selected_areas.values_list(
                "translation_key", flat=True
            )

            translated_areas = EventArea.objects.filter(
                translation_key__in=selected_translation_keys,
                locale_id=current_locale.id,
            )

        else:
            translated_areas = []

        selected_categories = self.get_selected_categories(value)

        # Use EventsPage method instead of Event
        filtered_events = Event.get_filtered_events(
            categories=selected_categories,
            start_date=start_date,
            end_date=end_date,
            areas=translated_areas,
        )

        filtered_events = filtered_events.order_by("date_instances")

        paginated_events = paginate(request, filtered_events, per_page=10)

        map_events = []

        for event in paginated_events:
            lat, lon = event.get_lat_lon()
            #if lat and lon:
                #distance = haversine(53.1771078,-4.0486885, lat, lon)
                #print(distance)
            
            coords = (
                self.parse_wkt_point(event.geolocation) if event.geolocation else None
            )
            if coords:
                lat, lng = coords
                event.map_lat = lat
                event.map_lng = lng
                map_events.append(
                    {
                        "title": event.title,
                        "description": (
                            str(event.description) if event.description else ""
                        ),
                        "url": event.url_link if event.url_link else "",
                        "lat": float(lat),
                        "lng": float(lng),
                    }
                )

        context["map_events"] = map_events
        context["events"] = paginated_events
        context["start_date"] = start_date
        context["end_date"] = end_date
        context["categories"] = selected_categories
        context["areas"] = EventArea.objects.filter(locale_id=current_locale.id)
        context["selected_areas"] = translated_areas

        # Fetch all labels for this locale
        labels_qs = Label.objects.filter(locale=current_locale)
        labels_dict = {label.key: label.value for label in labels_qs}

        context["labels"] = labels_dict

        return context

    class Meta:
        icon = "image"
        label = "Events block"
        template = "blocks/events.html"


class EventsPageBlock(blocks.StreamBlock):

    paragraph = ParagraphBlock(
        features=[
            "bold",
            "italic",
            "h3",
            "h4",
            "ol",
            "ul",
            "link",
            "document-link",
            "image",
            "blockquote",
            "text_centre",
        ]
    )

    events = EventsBlock()
