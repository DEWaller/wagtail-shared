from bs4 import BeautifulSoup

from django.utils.safestring import mark_safe

from wagtail.blocks import RichTextBlock
from wagtail.documents import get_document_model

from .doc_helpers import get_file_marker_html

IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.webp')

class AccessibleRichTextBlock(RichTextBlock):
    """
    A custom RichTextBlock that enhances accessibility by appending markers to links
    based on their target files or URLs.

    This block overrides the `render` method to process the rendered HTML and add
    additional markers to anchor (`<a>`) tags. If the link points to a document in
    the system, it appends a marker based on the document's filename. If the document
    does not exist, it appends a marker based on the cleaned URL.

    Methods:
        render(value, context=None):
            Renders the block's content as HTML, processes anchor tags to append
            accessibility markers, and returns the modified HTML.

    Dependencies:
        - BeautifulSoup: Used for parsing and modifying the HTML content.
        - get_document_model: Retrieves the document model for querying documents.
        - get_file_marker_html: Generates the HTML snippet for the file marker.
        - mark_safe: Marks the modified HTML as safe for rendering.

    Example:
        This block can be used in a Wagtail StreamField to provide enhanced
        accessibility for rich text content with links.
    """

    # def render(self, value, context=None):
    #     html = super().render(value, context)
    #     soup = BeautifulSoup(html, "html.parser")

    #     Document = get_document_model()

    #     for a in soup.find_all("a", href=True):
    #         href = a["href"]

    #         marker_html = ""
    #         try:
    #             doc = Document.objects.get(file=href)
    #             marker_html = get_file_marker_html(doc.filename)
    #         except Document.DoesNotExist:
    #             clean_href = href.split("?")[0].split("#")[0]
    #             marker_html = get_file_marker_html(clean_href)

    #         if marker_html and marker_html not in str(a):
    #             # Append the whole HTML snippet to the link
    #             marker_soup = BeautifulSoup(marker_html, "html.parser")
    #             for item in marker_soup.contents:
    #                 a.append(item)

    #     return mark_safe(str(soup))
    
    def render(self, value, context=None):
        html = super().render(value, context)
        soup = BeautifulSoup(html, "html.parser")

        Document = get_document_model()

        for a in soup.find_all("a", href=True):
            href = a["href"]

            marker_html = ""
            try:
                doc = Document.objects.get(file=href)
                marker_html = get_file_marker_html(doc.filename)

                # 👉 If it's an image document, set target="_blank"
                #if doc.filename.lower().endswith(IMAGE_EXTENSIONS):
                a["target"] = "_blank"
                a["rel"] = "noopener"
            except Document.DoesNotExist:
                clean_href = href.split("?")[0].split("#")[0]
                marker_html = get_file_marker_html(clean_href)

                # Optional: if URL ends with image ext, do the same
                #if clean_href.lower().endswith(IMAGE_EXTENSIONS):
                a["target"] = "_blank"
                a["rel"] = "noopener"

            if marker_html and marker_html not in str(a):
                marker_soup = BeautifulSoup(marker_html, "html.parser")
                for item in marker_soup.contents:
                    a.append(item)

        return mark_safe(str(soup))


class ParagraphBlock(AccessibleRichTextBlock):
    """
    A custom block for creating rich text paragraphs with accessibility features.

    This block extends the AccessibleRichTextBlock to provide additional
    functionality for managing rich text content in a Wagtail StreamField.

    Attributes:
        Meta (class):
            - label (str): The display name for the block in the Wagtail editor.
            - icon (str): The icon used to represent the block in the Wagtail editor.
            - template (str): (Commented out) The path to the template used for rendering the block.
    """


    class Meta:
        label = "Paragraph"
        icon = "doc-full"
