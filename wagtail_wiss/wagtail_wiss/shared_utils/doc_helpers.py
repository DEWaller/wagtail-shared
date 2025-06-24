import os

def get_file_marker_html(filename):
    """
    Generates HTML markup to display a file type label based on the file extension,
    including accessibility support.

    Adds support for:
        - PDF, Word, Excel, PowerPoint
        - Common image types: JPG, PNG, GIF, etc.

    Returns a label like: (PDF) visually, with screen-reader-only text.
    """
    ext = os.path.splitext(filename)[1].lower()

    labels = {
        ".pdf": "PDF",
        ".doc": "Word",
        ".docx": "Word",
        ".xls": "Excel",
        ".xlsx": "Excel",
        ".ppt": "PowerPoint",
        ".pptx": "PowerPoint",
        ".jpg": "Image",
        ".jpeg": "Image",
        ".png": "Image",
        ".gif": "Image",
        ".webp": "Image",
        ".svg": "Image",
    }

    label = labels.get(ext)
    if not label:
        return ""

   
    visible = f'<span class="small"> ({label})</span>'
    sr_only = f'<span class="sr-only">, {label} file</span>'
    return visible + sr_only
