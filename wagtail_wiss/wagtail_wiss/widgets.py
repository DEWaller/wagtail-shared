from django.forms import TextInput

class CaptionWithOCRWidget(TextInput):
    template_name = "widgets/caption_with_ocr.html"

    class Media:
        js = ["js/caption_ocr.js"]  # this will do the image processing
