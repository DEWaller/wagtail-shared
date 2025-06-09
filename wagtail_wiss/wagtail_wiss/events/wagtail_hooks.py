
from wagtail.snippets.models import register_snippet

from .viewsets import (
    EventsCategoryViewSet,
    EventAreaViewSet,
    EventViewSet,
)

register_snippet(EventsCategoryViewSet)
register_snippet(EventAreaViewSet)
register_snippet(EventViewSet)


from wagtail import hooks
from django.utils.safestring import mark_safe

@hooks.register('insert_editor_js')
def add_manual_ocr_button_script():
    return mark_safe("""
        <script src="https://cdn.jsdelivr.net/npm/js-cookie@3.0.1/dist/js.cookie.min.js"></script>
        <script>
        
        function autoResizeTextarea(el) {
            // Reset height so scrollHeight is calculated from scratch
            el.style.height = 'auto';
            // Then set it to match the content
            el.style.height = el.scrollHeight + 'px';
        }
        
        document.addEventListener('DOMContentLoaded', function () {
            const chooser = document.querySelector('#id_image-chooser');
            const ocrField = document.querySelector('[name="ocr_text"]');

            if (chooser && ocrField && !document.getElementById('run-ocr-button')) {
                const btn = document.createElement('button');
                btn.textContent = 'Run OCR';
                btn.id = 'run-ocr-button';
                btn.type = 'button';
                btn.className = 'button';
                btn.style.marginTop = '1rem';
                chooser.appendChild(btn);

                btn.addEventListener('click', function () {
                    const imageIdInput = document.querySelector('input[name=image]');
                    const imageId = imageIdInput ? imageIdInput.value : null;
                    
                    console.log(imageIdInput)
                    console.log(imageId)


                    if (!imageId) {
                        alert('Please select an image first.');
                        return;
                    }

                    btn.disabled = true;
                    btn.textContent = 'Running OCR...';

                    fetch("/admin/events/run-ocr/", {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'X-CSRFToken': Cookies.get('csrftoken')
                        },
                        body: 'image_id=' + encodeURIComponent(imageId)
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.text) {
                            let text = data.text;

                            // 1) Temporarily protect double-newlines
                            const placeholder = '___DOUBLE_NL___';
                            text = text.replace(/\\n\\n/g, placeholder);

                            // 2) Replace all remaining single newlines with a space
                            text = text.replace(/\\n/g, ' ');

                            // 3) Restore the double-newlines
                            text = text.replace(new RegExp(placeholder, 'g'), '\\n\\n');

                            ocrField.value = text;
                        } else {
                            alert(data.error || 'OCR failed.');
                        }
                        
                        autoResizeTextarea(ocrField);
                    })
                    .catch(error => {
                        console.error('OCR error:', error);
                        alert('OCR failed.');
                    })
                    .finally(() => {
                        btn.disabled = false;
                        btn.textContent = 'Run OCR';
                    });
                });
            }
        });
        </script>
    """)

from django.urls import path
from .views import run_ocr_on_image

@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        path('events/run-ocr/', run_ocr_on_image, name='run_ocr'),
    ]