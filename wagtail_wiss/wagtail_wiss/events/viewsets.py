from django.forms.widgets import (
    CheckboxSelectMultiple,
)  # Only for instantiation

from django import forms
from django.db import transaction
from django.utils.translation import gettext as _

from wagtail.models import Site
from wagtail.snippets.views.snippets import SnippetViewSet
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtailgeowidget import geocoders
from wagtailgeowidget.panels import GeoAddressPanel, LeafletPanel

from core.utils.sites import filter_for_request_site

#from .forms import EventAdminForm
from .models import EventsCategory, EventArea, Event


class EventsCategoryViewSet(SnippetViewSet):
    """
    EventsCategoryViewSet is a viewset for managing the EventsCategory model snippets.

    Attributes:
        model (Model): The model associated with this viewset, which is EventsCategory.
        list_display (list): Fields to display in the list view, including "name" and "locale".
        search_fields (list): Fields that can be searched, including "name".
        panels (list): UI panels for editing the model, including a FieldPanel for "name".
        ordering (list): Default ordering for the queryset, sorted by "name".
    """
    model = EventsCategory
    list_display = ["name", "locale"]
    search_fields = ["name"]
    panels = [
        FieldPanel("name"),
    ]
    ordering = ["name"]
    
    # ------------------------------------------------------------------ #
    # 1.  LISTING – hide configs that are not for this site
    # ------------------------------------------------------------------ #
    
    def get_queryset(self, request):
        qs = super().get_queryset(request) or self.model._default_manager.all()
        return filter_for_request_site(qs, request)


class EventAreaViewSet(SnippetViewSet):
    """
    EventAreaViewSet is a viewset for managing EventArea snippets in the Wagtail admin interface.

    Attributes:
        model (Model): The model associated with this viewset, which is `EventArea`.
        list_display (list): A list of fields to display in the list view of the admin interface.
        search_fields (list): A list of fields that can be searched in the admin interface.
        panels (list): A list of FieldPanel objects defining the fields to display in the edit interface.
    """
    model = EventArea
    list_display = ["name", "description", "locale"]
    search_fields = ["name", "description"]
    # ordering = ["name"]
    panels = [
        FieldPanel("name"),
        FieldPanel("description"),
    ]
    
    # ------------------------------------------------------------------ #
    # 1.  LISTING – hide configs that are not for this site
    # ------------------------------------------------------------------ #
    
    def get_queryset(self, request):
        qs = super().get_queryset(request) or self.model._default_manager.all()
        return filter_for_request_site(qs, request)


class EventViewSet(SnippetViewSet):
    """
    EventViewSet is a custom viewset for managing Event snippets in a Wagtail project.
    Attributes:
        model (Model): The model associated with this viewset, which is `Event`.
        list_display (list): Fields to display in the list view, including "title", "display_categories", and "locale".
        panels (list): Configuration for the Wagtail admin interface, including field panels, inline panels, and multi-field panels.
        search_fields (list): Fields to include in the search functionality, such as "title", "slug", and "description".
        ordering (list): Default ordering for the list view, based on the "title" field.
        list_filter (list): Fields to include in the filter functionality, such as "title", "slug", "categories", "areas", and "location".
    Methods:
        display_event_dates(obj):
            Retrieves and formats all event dates for the given event from the EventDateInstance table.
            Args:
                obj (Event): The event instance.
            Returns:
                str: A comma-separated string of formatted event dates.
        after_save(instance):
            Ensures the EventDateInstance table is updated after saving the event and related objects.
            Args:
                instance (Event): The event instance being saved.
        get_form_class(for_update=False):
            Customises the form class for the viewset, filtering the "categories" and "areas" fields based on the locale of the instance.
            Args:
                for_update (bool): Indicates whether the form is for updating an existing instance.
            Returns:
                class: A dynamically created form class with filtered querysets for "categories" and "areas".
    """
    model = Event
    list_display = ["title", "display_categories", "locale"]

    def display_event_dates(self, obj):
        """
        Display all event dates for the event from the EventDateInstance table.
        """
        # Retrieve all dates from EventDateInstance for this event
        dates = obj.date_instances.values_list("date", flat=True)
        return ", ".join(date.strftime("%Y-%m-%d") for date in dates)

    display_event_dates.short_description = "Event Dates"

    def after_save(self, instance):
        """
        Ensure EventDateInstance table updates after the event and related objects are saved.
        """
        transaction.on_commit(lambda: instance.refresh_event_date_instances())
        super().after_save(instance)

    panels = [
        FieldPanel("slug"),
        FieldPanel("title"),
        FieldPanel("description"),
        FieldPanel("image"),
        FieldPanel("ocr_text"),
        InlinePanel("event_dates", label=_("Event date")),  # InlinePanel for EventDate
        MultiFieldPanel(
            [
                GeoAddressPanel("address", geocoder=geocoders.NOMINATIM),
                LeafletPanel("geolocation", address_field="address", zoom_field="zoom"),
            ],
            heading="Geo details",
        ),
        MultiFieldPanel(
            [
                FieldPanel("page_link"),
                FieldPanel("use_page_title"),
                FieldPanel(
                    "url_link",
                    widget=forms.TextInput(
                        attrs={"placeholder": "https://example.com"}
                    ),
                ),
            ],
            heading="Links",
        ),
        FieldPanel("location"),
        FieldPanel("categories", widget=CheckboxSelectMultiple),

        FieldPanel("areas", widget=CheckboxSelectMultiple),
    ]
    search_fields = ["title", "slug", "description"]
    ordering = ["title"]
    list_filter = [
        "title",
        "slug",
        "categories",
        "areas",
        "location",
    ]
    
    # ------------------------------------------------------------------ #
    # 1.  LISTING – hide configs that are not for this site
    # ------------------------------------------------------------------ #
    def get_queryset(self, request):
        qs = super().get_queryset(request) or self.model._default_manager.all()
        return filter_for_request_site(qs, request)
    
    
    def get_form_class(self, for_update=False):
        # Let Wagtail build the form automatically, but then we hook in
        form_class = super().get_form_class(for_update)

        class FilteredForm(form_class):
            def __init__(self2, *args, **kwargs):
                super().__init__(*args, **kwargs)
                instance = self2.instance
                if instance and instance.locale_id:
                    self2.fields['categories'].queryset = EventsCategory.objects.filter(locale=instance.locale)
                    self2.fields['areas'].queryset = EventArea.objects.filter(locale=instance.locale)
                    print(f"Filtered form for locale: {instance.locale}")
                else:
                    print("No instance or locale found.")

        return FilteredForm