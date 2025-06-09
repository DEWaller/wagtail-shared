# from django import forms
# from wagtail.models import Site
# from .models import Event

# class EventForm(forms.ModelForm):
#     class Meta:
#         model = Event
#         fields = '__all__'

#     def __init__(self, *args, **kwargs):
#         request = kwargs.pop('request', None)
#         super().__init__(*args, **kwargs)
        
#         print("EventForm __init__")

#         if request and not self.instance.pk:
#             current_site = Site.find_for_request(request)
#             if current_site:
#                 self.fields['site'].initial = current_site.pk
