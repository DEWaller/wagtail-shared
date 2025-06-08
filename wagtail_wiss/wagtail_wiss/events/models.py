from django.db import models
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel

class EventPage(Page):
    date = models.DateField()
    location = models.CharField(max_length=255)

    content_panels = Page.content_panels + [
        FieldPanel("date"),
        FieldPanel("location"),
    ]
