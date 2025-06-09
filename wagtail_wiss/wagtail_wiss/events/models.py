from django.db import models
from django.db.models import Q
from django.db import transaction
from django.conf import settings

from datetime import date
from dateutil.rrule import rrule

from wagtail.models import TranslatableMixin, Page, Locale
from wagtail.admin.panels import FieldPanel
from wagtail.search import index
from wagtail_localize.fields import TranslatableField
from wagtail.fields import RichTextField

from modelcluster.models import ClusterableModel, ParentalKey

from PIL import Image as PilImage
import pytesseract
import requests
from io import BytesIO


class EventsCategory(TranslatableMixin, models.Model):
    """
    EventsCategory is a model representing a category for events, supporting translations.

    Attributes:
        name (str): The name of the event category. This field is translatable and allows a maximum length of 255 characters.
                    It cannot be blank but can be null.

        translatable_fields (list): A list of fields that support translations. In this case, it includes the "name" field.

    Methods:
        __str__(): Returns the string representation of the event category, which is the value of the "name" field.

    Meta:
        verbose_name (str): A human-readable singular name for the model, "Events Category".
        verbose_name_plural (str): A human-readable plural name for the model, "Events categories".
    """

    name = models.CharField(max_length=255, blank=False, null=True)
    

    translatable_fields = [
        TranslatableField("name"),
    ]

    def __str__(self):
        return self.name

    class Meta(TranslatableMixin.Meta):
        verbose_name = "Events Category"
        verbose_name_plural = "Events categories"


# Create your models here.
class EventArea(TranslatableMixin, models.Model):
    """
    EventArea is a model representing an area associated with events. It supports
    translation for its fields, allowing multilingual content.

    Attributes:
        name (str): The name of the event area. This field is required.
        description (str, optional): A detailed description of the event area. This field is optional.
        translatable_fields (list): Specifies the fields that are translatable, including 'name' and 'description'.

    Methods:
        __str__(): Returns the string representation of the event area, which is its name.

    Meta:
        verbose_name (str): The singular name for the model in the admin interface.
        verbose_name_plural (str): The plural name for the model in the admin interface.
        ordering (list): Specifies the default ordering of the model instances by the 'name' field.
    """

    name = models.CharField(max_length=255, blank=False)

    description = models.TextField(
        blank=True, null=True
    )  # Optional field for more content

    # Make the 'name' and 'description' translatable
    translatable_fields = [
        TranslatableField("name"),
        TranslatableField("description"),
    ]

    # Ensure it is indexed for searching
    search_fields = [
        index.SearchField("name", partial_match=True),  # Enables partial matching
    ]

    def __str__(self):
        return self.name

    class Meta(TranslatableMixin.Meta):
        verbose_name = "Event area"
        verbose_name_plural = "Event areas"
        ordering = ["name"]


class Event(TranslatableMixin, ClusterableModel):
    """
    Event Model
    This model represents an event with various attributes such as title, description, location,
    categories, and associated metadata. It supports translation and clustering features.

    Attributes:
        title (CharField): The title of the event.
        description (RichTextField): A rich text description of the event (optional).
        location (CharField): The location of the event (optional).
        geolocation (CharField): Geolocation data for the event (optional).
        slug (SlugField): A unique URL-friendly identifier for the event.
        categories (ManyToManyField): Categories associated with the event.
        image (ForeignKey): An optional image associated with the event.
        areas (ManyToManyField): Areas associated with the event.
        legacy_html (TextField): Legacy HTML content for the event (optional).
        archive (BooleanField): Indicates whether the event is archived.
        address (CharField): The address of the event (optional).
        zoom (SmallIntegerField): Zoom level for map display (optional).
        page_link (ForeignKey): A link to a related page (optional).
        use_page_title (BooleanField): Whether to append the linked page's title to the link text.
        url_link (URLField): An external URL link for the event (optional).
        search_fields (list): Fields to include in search indexing.

    Methods:
        __str__(): Returns the string representation of the event (its title).
        display_categories(): Returns a comma-separated string of associated category names.
        refresh_event_date_instances(): Refreshes the `EventDateInstance` table with unique dates
            generated from associated `EventDate` objects.
        save(*args, **kwargs): Overrides the save method to refresh event date instances after saving.
        get_filtered_events(categories=None, start_date=None, end_date=None, areas=None):
            Retrieves events filtered by categories, date range, and areas.
        ordered_areas(): Returns the areas associated with the event, ordered by name.

    Meta:
        verbose_name (str): Human-readable name for the model ("Event").
        verbose_name_plural (str): Human-readable plural name for the model ("Events").
    """

    title = models.CharField(max_length=255)
    
    description = RichTextField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    geolocation = models.CharField(max_length=250, blank=True, null=True)
    slug = models.SlugField(
        max_length=80,
        unique=False,
        default="",
        help_text="URL slug, try to keep it short",
    )
    categories = models.ManyToManyField(
        EventsCategory, related_name="events_categories", blank=True
    )
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    ocr_text = models.TextField(
        blank=True,
        verbose_name="OCR text",
        help_text="Text extracted from the image using OCR, it has limitations. This is not used for anything yet.",
    )
    areas = models.ManyToManyField(EventArea, related_name="events_areas", blank=True)
    legacy_html = models.TextField(blank=True, null=True)  #
    archive = models.BooleanField(default=False)  # New field to archive items
    address = models.CharField(max_length=250, blank=True, null=True)
    zoom = models.SmallIntegerField(blank=True, null=True)
    page_link = models.ForeignKey(
        Page, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    use_page_title = models.BooleanField(
        default=False,
        help_text="Append the title of the linked page to the link text.",
    )
    url_link = models.URLField(blank=True, null=True)

    search_fields = [
        index.SearchField("title"),
        index.SearchField("description"),
    ]

    def __str__(self):
        return self.title

    def display_categories(self):
        return ", ".join([category.name for category in self.categories.all()])

    display_categories.short_description = "categories"

    def refresh_event_date_instances(self):
        """
        Refresh the `EventDateInstance` table with all unique generated dates.
        """
        # Clear all existing instances for this event
        self.date_instances.all().delete()

        # Generate new instances from EventDate
        all_dates = []
        for event_date in self.event_dates.all():
            dates = event_date.generate_dates()
            all_dates.extend(dates)

        # Use a set to remove duplicates
        unique_dates = set(all_dates)

        # Bulk create EventDateInstance rows
        instances = [EventDateInstance(event=self, date=d) for d in unique_dates]
        EventDateInstance.objects.bulk_create(instances)

    def save(self, *args, **kwargs):
        """
        Override save to refresh event date instances after saving.
        """
        # super().save(*args, **kwargs)
        transaction.on_commit(lambda: self.refresh_event_date_instances())

        #  # Perform OCR only if there's an image and no existing OCR text
        # if self.image and not self.ocr_text:
        #     try:
        #         # Download image from Wagtail image URL
        #         image_url = self.image.file.url
        #         response = requests.get(image_url)
        #         img = PilImage.open(BytesIO(response.content)).convert('L')  # grayscale

        #         # Run pytesseract with Welsh
        #         self.ocr_text = pytesseract.image_to_string(img, lang='cym')
        #     except Exception as e:
        #         self.ocr_text = f"OCR failed: {e}"

        super().save(*args, **kwargs)

    def get_lat_lon(self):
        if not self.geolocation or not self.geolocation.startswith("SRID=4326;POINT("):
            return None, None
        try:
            point_str = self.geolocation.split("POINT(")[-1].rstrip(")")
            lon_str, lat_str = point_str.split()
            return float(lat_str), float(lon_str)
        except ValueError:
            return None, None

    @staticmethod
    def parse_geolocation_string(geo_str):
        if not geo_str or not geo_str.startswith("SRID=4326;POINT("):
            return None, None
        try:
            # Extract "POINT(lon lat)"
            point_str = geo_str.split("POINT(")[-1].rstrip(")")
            lon_str, lat_str = point_str.split()
            return float(lat_str), float(lon_str)
        except ValueError:
            return None, None

    @staticmethod
    def get_filtered_events(
        categories=None, start_date=None, end_date=None, areas=None
    ):
        """
        Retrieve events filtered by the given categories, date range, and areas.
        """
        # Prefetch related fields for optimization
        events = Event.objects.prefetch_related("categories", "areas", "date_instances")

        current_locale = Locale.get_active()

        events = events.filter(
            archive=False, locale=current_locale
        )  # Ensure to filter by locale

        # Filter by categories (if provided)
        if categories:
            events = events.filter(categories__in=categories).distinct()

        # Filter by date range (if provided)
        if start_date or end_date:
            date_filter = Q()
            if start_date:
                date_filter &= Q(date_instances__date__gte=start_date)
            if end_date:
                date_filter &= Q(date_instances__date__lte=end_date)
            events = events.filter(date_filter).distinct()

        # if start_date or end_date:
        #     date_filter = {}
        #     if start_date:
        #         date_filter["date_instances__date__gte"] = start_date
        #     if end_date:
        #         date_filter["date_instances__date__lte"] = end_date

        #     events = events.filter(**date_filter).distinct()
        # # Filter by areas (if provided)

        if areas:
            area_keys = areas.values_list("translation_key", flat=True)
            events = events.filter(areas__translation_key__in=area_keys).distinct()

        return events

    def ordered_areas(self):
        return self.areas.order_by("name")

    class Meta(TranslatableMixin.Meta):
        verbose_name = "Event"
        verbose_name_plural = "Events"


class EventDate(models.Model):
    """
    EventDate is a Django model representing a recurring event's date details.

    Attributes:
        DAILY (int): Constant representing daily frequency.
        WEEKLY (int): Constant representing weekly frequency.
        MONTHLY (int): Constant representing monthly frequency.
        YEARLY (int): Constant representing yearly frequency.
        FREQUENCY_CHOICES (list): List of tuples defining frequency choices for the recurrence.
        event (ParentalKey): Foreign key linking to the parent Event model.
        start_date (DateField): The start date of the recurrence.
        end_date (DateField): The optional end date of the recurrence.
        frequency (IntegerField): The frequency of recurrence, chosen from FREQUENCY_CHOICES.
        interval (PositiveIntegerField): The interval for the recurrence (e.g., every 1 week).
        panels (list): List of Wagtail admin panels for managing the model fields.

    Methods:
        generate_dates():
            Generates a list of dates based on the recurrence rule.
            Handles cases where start_date or end_date is missing or invalid.
            Returns:
                list: A list of datetime.date objects representing the recurrence dates.

        __str__():
            Returns a string representation of the EventDate instance, including the event,
            start date, end date, and frequency.

    Meta:
        verbose_name (str): Human-readable name for the model ("Event date").
        verbose_name_plural (str): Human-readable plural name for the model ("Event dates").
    """

    # 🔹 Define frequency constants at the class level

    DAILY = 3
    WEEKLY = 2
    MONTHLY = 1
    YEARLY = 0

    FREQUENCY_CHOICES = [
        (DAILY, "Daily"),
        (WEEKLY, "Weekly"),
        (MONTHLY, "Monthly"),
        (YEARLY, "Yearly"),
    ]

    event = ParentalKey("Event", on_delete=models.CASCADE, related_name="event_dates")
    start_date = models.DateField(
        help_text="Start date of the recurrence.", default=date.today
    )
    end_date = models.DateField(
        null=True, blank=True, help_text="End date of the recurrence."
    )
    frequency = models.IntegerField(
        choices=FREQUENCY_CHOICES, default=DAILY, help_text="Frequency of recurrence."
    )
    interval = models.PositiveIntegerField(
        default=1, help_text="Interval for the recurrence (e.g., every 1 week)."
    )

    panels = [
        FieldPanel("start_date"),
        FieldPanel("end_date"),
        FieldPanel("frequency"),
        FieldPanel("interval"),
    ]

    def generate_dates(self):
        """
        Generate dates based on the recurrence rule.
        Handles missing or invalid start/end dates gracefully.
        """
        if not self.start_date:
            return []  # No start date; return an empty list

        if not self.end_date:
            return [self.start_date]  # No end date; return only the start_date

        if self.end_date < self.start_date:
            return [self.start_date]  # Invalid range; fallback to start_date

        # Generate recurrence dates
        rule = rrule(
            freq=self.frequency,
            dtstart=self.start_date,
            until=self.end_date,
            interval=self.interval,
        )

        dates = list(rule)
        # print(f"Frequency: {self.frequency}")
        # print(f"Interval: {self.interval}")
        # print(f"Start Date: {self.start_date}")
        # print(f"End Date: {self.end_date}")
        for date in dates:
            print(f"Generated date: {date}")  # Debugging output
        return dates
        # return list(rule)

    def __str__(self):
        return f"{self.event} - {self.start_date} to {self.end_date} (Freq: {self.get_frequency_display()})"

    class Meta:
        verbose_name = "Event date"
        verbose_name_plural = "Event dates"


class EventDateInstance(models.Model):
    """
    EventDateInstance represents a specific date associated with an event.

    Attributes:
        event (ForeignKey): A reference to the associated Event object. If the Event
            is deleted, all related EventDateInstance objects are also deleted.
        date (DateField): The specific date for the event instance.

    Meta:
        indexes: Adds a database index on the 'date' field to optimize queries
            filtering by date.
        unique_together: Ensures that there cannot be duplicate entries for the
            same event and date combination.
        ordering: Specifies that instances are ordered by the 'date' field by default.

    Methods:
        __str__: Returns a string representation of the EventDateInstance in the
            format "<event title> - <date>".
    """

    event = models.ForeignKey(
        "Event", on_delete=models.CASCADE, related_name="date_instances"
    )
    date = models.DateField()

    class Meta:
        indexes = [
            models.Index(fields=["date"]),  # Optimize search by date
        ]
        unique_together = (
            "event",
            "date",
        )  # Prevent duplicate entries for the same event
        ordering = ["date"]

    def __str__(self):
        return f"{self.event.title} - {self.date}"


# class Menu(ClusterableModel):
#     """
#     Represents a flat menu that can be used to organise and display navigation items.

#     Attributes:
#         name (str): The name of the menu, limited to 255 characters.

#     Meta:
#         verbose_name (str): A human-readable singular name for the model ("Flat Menu").
#         verbose_name_plural (str): A human-readable plural name for the model ("Flat Menus").

#     Methods:
#         __str__(): Returns the name of the menu as its string representation.
#     """

#     name = models.CharField(max_length=255)

#     class Meta:
#         verbose_name = "Flat Menu"
#         verbose_name_plural = "Flat Menus"

#     def __str__(self):
#         return self.name


### Labels -  administered by the Django admin interface
class Label(models.Model):
    """
    Represents a translatable label with a key-value pair associated with a specific locale.

    Attributes:
        key (str): The unique identifier for the label within a specific locale.
        value (str): The text or value associated with the key.
        locale (Locale): A foreign key linking the label to a specific locale.

    Meta:
        unique_together (tuple): Ensures that the combination of `key` and `locale` is unique.
        verbose_name (str): The singular name for the model in the admin interface.
        verbose_name_plural (str): The plural name for the model in the admin interface.

    Methods:
        __str__(): Returns a string representation of the label in the format "key (locale)".
    """

    key = models.CharField(max_length=100)
    value = models.CharField(max_length=255)
    locale = models.ForeignKey(Locale, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("key", "locale")
        verbose_name = "Label"
        verbose_name_plural = "Labels"

    def __str__(self):
        return f"{self.key} ({self.locale})"
