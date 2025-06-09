from django.urls import path
from .views import run_ocr_on_image

urlpatterns = [
    path('run-ocr/', run_ocr_on_image, name='run_ocr'),
]
