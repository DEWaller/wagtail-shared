import pytesseract
from wagtail.images import get_image_model
from PIL import Image as PilImage
import requests
from io import BytesIO
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required

@csrf_exempt
@staff_member_required
def run_ocr_on_image(request):
    if request.method == 'GET':
        return JsonResponse({'error': 'GET method not allowed'}, status=405)
    if request.method == 'POST':
        image_id = request.POST.get('image_id')
        print(image_id)
        if not image_id:
            return JsonResponse({'error': 'Missing image_id'}, status=400)

        try:
            ImageModel = get_image_model()
            img_obj = ImageModel.objects.get(id=image_id)
            image_url = img_obj.file.url

            response = requests.get(image_url)
            pil_image = PilImage.open(BytesIO(response.content)).convert('L')
            text = pytesseract.image_to_string(pil_image, lang='cym')

            return JsonResponse({'text': text})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
