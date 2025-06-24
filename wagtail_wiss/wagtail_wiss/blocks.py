# from pyparsing import null_debug_action
import os
import re
import uuid
import json
from bs4 import BeautifulSoup
from dateutil.parser import parse as parse_date

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.template import loader, TemplateDoesNotExist
from django.template.loader import select_template
from wagtail import blocks
from modelcluster.models import ClusterableModel

from wagtail_wiss.pagination.utils import paginate

from wagtail_wiss.snippets.models import Category, Gallery, Menu, News, NewsItem

from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.blocks import PageChooserBlock, RichTextBlock
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.documents import get_document_model
from wagtail.embeds.blocks import EmbedBlock
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Locale
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail.templatetags.wagtailcore_tags import richtext
from wagtail.embeds.blocks import EmbedBlock

from .shared_utils.doc_helpers import get_file_marker_html
from .shared_utils.accessibility import ParagraphBlock

from .shared_utils.style_helpers import get_class_choices_from_scss
from .widgets import CaptionWithOCRWidget


new_table_options = {
    "contextMenu": [
        "row_above",
        "row_below",
        "---------",
        "col_left",
        "col_right",
        "---------",
        "remove_row",
        "remove_col",
        "---------",
        "undo",
        "redo",
        "---------",
        "copy",
        "cut",
        "---------",
        "alignment",
    ],
}

RICH_TEXT_FEATURES = [
    "bold",
    "italic",
    "h3",
    "h4",
    "ol",
    "ul",
    "link",
    "document-link",
    "image",
    "blockquote",
    "text_centre",
    "superscript",
    "subscript",
    "hr",
]


### Accordion block
class AccordianItemBlock(blocks.StructBlock):
    """
    AccordianItemBlock is a custom Wagtail StructBlock that represents an individual
    accordion item. It consists of a title and a body, where the body can contain
    various types of content.

    Attributes:
        title (TextBlock): A text field for the title of the accordion item.
        body (StreamBlock): A stream of content blocks that make up the body of the
            accordion item. It supports the following block types:
            - heading (CharBlock): A simple text heading with a "title" CSS class.
            - paragraph (RichTextBlock): A rich text field with features such as
              bold, italic, headings (h3, h4), ordered and unordered lists, links,
              document links, images, and blockquotes.
            - embed (EmbedBlock): An embedded media block with a maximum width of
              800 pixels and a maximum height of 400 pixels.
    """

    title = blocks.TextBlock(label="Accordion item title")
    body = blocks.StreamBlock(
        [
            ("heading", blocks.CharBlock(form_classname="title")),
            (
                "paragraph",
                ParagraphBlock(
                    features=[
                        "bold",
                        "italic",
                        "h3",
                        "h4",
                        "ol",
                        "ul",
                        "link",
                        "document-link",
                        "image",
                        "blockquote",
                    ]
                ),
            ),
            ("embed", EmbedBlock(max_width=800, max_height=400)),
        ],
        required=False,
        label="Accordion item body",
    )


class AccordianBlock(blocks.StructBlock):
    """
    A custom Wagtail StructBlock that represents an accordion block.

    This block contains a list of accordion items, each defined by the
    `AccordianItemBlock`. It also generates a unique identifier for each
    instance of the block to ensure uniqueness in the rendered HTML.

    Attributes:
        accordian_items (blocks.ListBlock): A list of `AccordianItemBlock`
            instances representing the items within the accordion.

    Meta:
        template (str): The path to the template used to render the block.
        icon (str): The icon used to represent the block in the Wagtail admin.
        label (str): The display name of the block in the Wagtail admin.

    Methods:
        get_context(value, parent_context=None):
            Extends the block's context by adding a unique identifier (`id`)
            to ensure each block instance can be uniquely identified in the
            rendered HTML.
    """

    # heading = blocks.TextBlock(max_length=100, blank=True, null=True, required=False)
    accordian_items = blocks.ListBlock(AccordianItemBlock())

    class Meta:
        template = "blocks/accordion.html"
        icon = "collapse-down"
        label = "Accordion block"

    # For a truly unique identifier, you can generate a random UUID in Python and pass it to the template.
    # Update your block definition to include a unique ID in the context:
    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        context["id"] = str(uuid.uuid4())  # Unique ID for each block
        return context


### End Accordion block


class StyledRichTextBlock(blocks.StructBlock):
    """
    A custom Wagtail StructBlock that combines a RichTextBlock with an optional CSS class
    for styling. This block allows users to select a predefined CSS class and input rich
    text content.

    Attributes:
        css_class (blocks.ChoiceBlock): A dropdown for selecting an optional CSS class
            from a list of choices derived from a SCSS file. This allows for applying
            specific styles to the block.
        content (blocks.RichTextBlock): A rich text editor block that supports a predefined
            set of features specified by `RICH_TEXT_FEATURES`.

    Meta:
        icon (str): The icon used to represent this block in the Wagtail admin interface.
        label (str): The display name of the block in the Wagtail admin interface.
        template (str): The path to the template used to render this block.
    """

    css_class = blocks.ChoiceBlock(
        choices=get_class_choices_from_scss(
            os.path.join(
                settings.BASE_DIR,
                "home",
                "static",
                "css",
                "components",
                "_accessible-colour-palette.scss",
            )
        ),
        required=False,
        label="CSS class",
        help_text="Select an optional CSS style for this block.",
    )

    content = blocks.RichTextBlock(features=RICH_TEXT_FEATURES)

    class Meta:
        icon = "doc-full"
        label = "Styled paragraph"
        template = "blocks/styled_richtext_block.html"


# class ContentGridBlock(ClusterableModel):
#     title = models.CharField(max_length=255)

#     class Meta:
#         verbose_name_plural = "Text & grid blocks"

#     def __str__(self):
#         return self.title


# class ContentGridBlockWrapper(blocks.StructBlock):
#     """
#     A wrapper block that allows selecting a Content Grid Block snippet.

#     Attributes:
#         content_grid (SnippetChooserBlock): A chooser block for selecting a
#             Content Grid Block snippet. The target model is "home.ContentGridBlock".
#             This field is optional and includes a help text for guidance.

#     Meta:
#         icon (str): The icon used to represent this block in the Wagtail admin interface.
#         label (str): The display name for this block in the Wagtail admin interface.
#     """

#     content_grid = SnippetChooserBlock(
#         target_model="blocks.ContentGridBlock",
#         required=False,
#         help_text="Select a Content Grid Block",
#     )

#     class Meta:
#         icon = "placeholder"
#         label = "Content Grid block"


class HeadingBlock(blocks.CharBlock):
    """
    A custom Wagtail streamfield block that represents a heading.

    This block allows users to add a heading to their content. It uses a
    CharBlock to accept a single line of text input. The block is rendered
    using the specified template.

    Attributes:
        Meta (class): Contains metadata for the block, including:
            - label: The display name of the block in the Wagtail editor.
            - icon: The icon used to represent the block in the editor.
            - template: The path to the template used to render the block.
    """

    class Meta:
        label = "Heading"
        icon = "title"
        template = "blocks/heading.html"


class CarouselBlock(blocks.StructBlock):
    """
    A custom Wagtail StructBlock that represents a carousel component.

    This block is designed to handle a collection of images or other content
    to be displayed in a carousel format. It includes metadata for rendering
    and display in the Wagtail admin interface.

    Attributes:
        Meta (class): Contains metadata for the block, including:
            - label: The display name for the block in the Wagtail admin.
            - icon: The icon used to represent the block in the admin interface.
            - template: The path to the template used to render the block.
    """

    # Assume this block is more complex and contains a list of images, etc.
    class Meta:
        label = "Carousel"
        icon = "image"
        template = "blocks/carousel.html"


class CallToActionBlock(blocks.StructBlock):
    """
    A Wagtail StructBlock that represents a "Call to Action" block, allowing users
    to create a link with customizable text, an optional internal page link, and/or
    an external URL. Additionally, users can choose to append the title of the
    linked page to the link text.

    Attributes:
        text (CharBlock): The text to display for the call to action. This field is required.
        page (PageChooserBlock): An optional internal page link.
        use_page_title (BooleanBlock): A boolean flag to determine whether to append
            the title of the linked page to the link text. Defaults to False.
        url (URLBlock): An optional external URL.

    Meta:
        label (str): The display name for the block in the Wagtail editor.
        icon (str): The icon to represent the block in the Wagtail editor.
        template (str): The template used to render the block.
    """

    text = blocks.CharBlock(required=True)
    page = PageChooserBlock(required=False)  # Internal link
    use_page_title = blocks.BooleanBlock(
        required=False,
        default=False,
        help_text="Append the title of the linked page to the link text.",
    )
    url = blocks.URLBlock(required=False)

    class Meta:
        label = "Call to Action"
        icon = "link"
        template = "blocks/call_to_action.html"


class HeaderImageBlock(blocks.StructBlock):
    """
    A custom Wagtail StructBlock for adding a header image with an optional caption.

    Attributes:
        image (ImageChooserBlock): A required image field that allows users to select an image.
        caption (CharBlock): An optional text field for adding a caption to the image, with a maximum length of 250 characters.

    Meta:
        icon (str): The icon used to represent this block in the Wagtail admin interface.
        label (str): The display name of the block in the Wagtail admin interface.
        form_classname (str): Additional CSS class for styling the block in the admin interface.
        template (str): The path to the template used to render this block.
    """

    image = ImageChooserBlock(required=True)
    caption = blocks.CharBlock(required=False, max_length=250)
    link = blocks.URLBlock(
        required=False,
        help_text="Optional link for the image. If provided, the image will be clickable.",
    )
    page_link = PageChooserBlock(
        required=False,
        help_text="Optional internal link for the image. If provided, the image will be clickable.",
    )

    class Meta:
        icon = "image"
        label = "Header Image"
        form_classname = "image_with_caption_block struct-block"
        template = "blocks/header_image.html"


class OCRCaptionBlock(blocks.CharBlock):
    """
    A custom Wagtail StreamField block that extends `blocks.CharBlock` to provide
    a caption input field with OCR (Optical Character Recognition) functionality.

    This block overrides the `get_form_class` method to customize the widget used
    for the form field. The widget is set to `CaptionWithOCRWidget` with additional
    CSS class attributes for styling.

    Attributes:
        None

    Methods:
        get_form_class():
            Returns a customized form class with the widget set to `CaptionWithOCRWidget`.
    """

    def get_form_class(self):
        form_class = super().get_form_class()
        form_class.widget = CaptionWithOCRWidget(attrs={"class": "caption-field"})
        return form_class


class ImageWithCaptionBlock(blocks.StructBlock):
    """
    A custom Wagtail StructBlock that represents an image with an optional caption.

    Attributes:
        image (ImageChooserBlock): A required block for selecting an image.
        caption (CharBlock): An optional block for adding a caption to the image,
            with a maximum length of 250 characters.

    Meta:
        icon (str): The icon to represent this block in the Wagtail admin interface.
        label (str): The display name of the block in the Wagtail admin interface.
        form_classname (str): The CSS class name applied to the block's form in the admin interface.
        template (str): The path to the template used to render this block.
    """

    image = ImageChooserBlock(required=True)
    caption = blocks.CharBlock(required=False, max_length=250)

    class Meta:
        icon = "image"
        label = "Image with caption"
        form_classname = "image_with_caption_block struct-block"
        template = "blocks/image_with_caption.html"


class ImageGridBlock(blocks.StructBlock):
    """
    A custom Wagtail StructBlock that represents a grid of images, where each image
    can include an optional caption. This block allows users to add between 1 and
    12 images, each defined by the ImageWithCaptionBlock.

    Attributes:
        images (blocks.ListBlock): A list of ImageWithCaptionBlock instances, with
            a minimum of 1 and a maximum of 12 images.

    Meta:
        template (str): The path to the template used to render this block.
        icon (str): The icon used to represent this block in the Wagtail admin.
        label (str): The display name for this block in the Wagtail admin.
    """

    images = blocks.ListBlock(ImageWithCaptionBlock(), min_num=1, max_num=12)

    class Meta:
        template = "blocks/image_grid.html"
        icon = "placeholder"
        label = "Image Grid"


class GalleryChooserBlock(SnippetChooserBlock):
    """
    A custom block for selecting a Gallery snippet using Wagtail's SnippetChooserBlock.

    This block allows users to choose a Gallery snippet from the admin interface
    and is initialized with the Gallery model.

    Attributes:
        args: Positional arguments passed to the parent SnippetChooserBlock.
        kwargs: Keyword arguments passed to the parent SnippetChooserBlock.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(Gallery, *args, **kwargs)


class MenuChooserBlock(SnippetChooserBlock):
    """
    A custom block for selecting a Menu snippet in Wagtail's StreamField.

    This block extends the SnippetChooserBlock to allow users to choose
    a Menu snippet from the admin interface.

    Attributes:
        *args: Variable length argument list passed to the parent class.
        **kwargs: Arbitrary keyword arguments passed to the parent class.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(Menu, *args, **kwargs)


class NewsChooserBlock(SnippetChooserBlock):
    """
    A custom block that allows users to select a News snippet using the SnippetChooserBlock.

    This block is specifically designed to work with the `News` model, enabling
    content editors to choose from existing News snippets in the Wagtail admin interface.

    Args:
        *args: Variable length argument list passed to the parent class.
        **kwargs: Arbitrary keyword arguments passed to the parent class.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(News, *args, **kwargs)


class GalleryGridBlock(blocks.StructBlock):
    """
    A custom Wagtail StructBlock for creating a gallery grid.
    Attributes:
        gallery (GalleryChooserBlock): A block to choose a gallery snippet, optional.
        heading (blocks.CharBlock): An optional heading for the grid.
        description (blocks.TextBlock): An optional description of the grid.
    Meta:
        icon (str): The icon to use in the Wagtail admin interface.
        label (str): The label to display in the Wagtail admin interface.
        template (str): The template to render the block.
    """

    gallery = GalleryChooserBlock(required=False)
    heading = blocks.CharBlock(
        required=False, help_text="Optional heading for the grid."
    )

    description = blocks.TextBlock(
        required=False, help_text="Optional description of the grid."
    )

    class Meta:
        icon = "image"
        label = "Image grid using Snippet Gallery"
        template = "blocks/gallery_grid.html"


class SiteMapBlock(blocks.StructBlock):
    """
    StreamField block that renders an automatic two-column site map.
    """

    class Meta:  # «Default» template – safe fall-back
        template = "blocks/sitemap/sitemap_block.html"
        icon = "site"
        label = "Site map"

    
    def get_context(self, value, parent_context=None):
        """
        Extend the context for rendering a StreamField block by adding homepage sections.

        This method retrieves the homepage's live and public child pages, excluding the current page
        and any pages marked with `exclude_from_sitemap=True`. The resulting sections are split into
        two lists (`sections_left` and `sections_right`) and added to the context for template rendering.

        Args:
            value: The value of the block.
            parent_context (dict, optional): The parent context, which may contain the current page.

        Returns:
            dict: The updated context dictionary with `sections_left` and `sections_right` if applicable.
        """
        ctx = super().get_context(value, parent_context)

        # parent_context may be None (e.g. in admin “chooser” rendering)
        if not parent_context:
            return ctx

        page = parent_context.get("page")          # ← this one survives the merge
        if page is None:                           # still None when rendered outside a page
            return ctx
        
        homepage = page.get_site().root_page.localized
        children  = homepage.get_children().live().public()

        sections = [
            p.specific
            for p in children
            if not getattr(p.specific, "exclude_from_sitemap", False)
            and p.id != page.id
        ]

        mid = len(sections) // 2
        ctx.update(
            sections_left=sections[:mid],
            sections_right=sections[mid:],
        )
        return ctx


    # # ──────────────────────────────────────────────────────────────────────
    # # Final render (glues template + context together)
    # # ──────────────────────────────────────────────────────────────────────
    # def render(self, value, parent_context=None):
    #     template_name = self._pick_template(parent_context or {})
    #     context = self.get_context(value, parent_context)
    #     return loader.render_to_string(template_name, context)


class NewsBlock(blocks.StructBlock):
    category = SnippetChooserBlock(Category, required=False)

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)

        # Get current time
        now = timezone.now()

        # Base query: Only include news items that are NOT archived and NOT expired
        news_items = NewsItem.objects.filter(archive=False).filter(
            models.Q(expiry_date__isnull=True) | models.Q(expiry_date__gt=now)
        )

        # Filter by category if selected
        if value["category"]:
            news_items = news_items.filter(category=value["category"])

        # Order by published date (newest first)
        context["news_items"] = news_items.order_by("sort_order", "-published_at")

        return context

    class Meta:
        icon = "snippet"
        label = "News"
        template = "blocks/news.html"


class MenuBlock(blocks.StructBlock):
    """
    A custom block for selecting a menu using the MenuChooserBlock.

    Attributes:
        menu (MenuChooserBlock): A block that allows choosing a menu snippet. It is optional.

    Meta:
        template (str): The template used to render this block.
        icon (str): The icon used to represent this block in the admin interface.
        label (str): The label used for this block in the admin interface.
    """

    menu = MenuChooserBlock(required=False)

    class Meta:
        template = "blocks/menu.html"
        icon = "bars"
        label = "Menu grid using Snippet Menu"


class ContentStreamBlock(blocks.StreamBlock):

    header_image = HeaderImageBlock()
    heading = HeadingBlock()
    paragraph = ParagraphBlock(features=RICH_TEXT_FEATURES)
    styled_paragraph = StyledRichTextBlock()
    call_to_action = CallToActionBlock()
    image_with_caption = ImageWithCaptionBlock()
    accordian = AccordianBlock()
    gallery = GalleryGridBlock()
    news = NewsBlock()
    embed = EmbedBlock(max_width=800, max_height=400)
    table = TableBlock(table_options=new_table_options)
    sitemap = SiteMapBlock()
    # polygon_map = PolygonsBlock()

    class Meta:
        block_counts = {
            "header_image": {"max_num": 1},
            "heading": {"max_num": 1},
        }


class MultiColumnContentStreamBlock(ContentStreamBlock):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.child_blocks.pop("events")


class SimpleContentStreamBlock(ContentStreamBlock):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Remove the 'gallery' block
        self.child_blocks.pop("gallery")
        # self.child_blocks.pop("menu")


class SingleColumnBlock(blocks.StructBlock):
    column = ContentStreamBlock()

    class Meta:
        template = "blocks/single_column.html"
        label = "Single column"

    # def get_context(self, value, parent_context=None):
    #     context = super().get_context(value, parent_context)
    #     # Add the class name to the context
    #     context["block_class"] = "single-column-block"
    #     return context

    # def __init_subclass__(cls, **kwargs):
    #     super().__init_subclass__(**kwargs)

        # from events.blocks import EventsBlock # Lazy import to avoid cicular import
        # from maps.blocks import MapPolygon # Lazy import to avoid cicular import

        # Add a new StructBlock (like EventsBlock)
        # blocks["events"] = EventsBlock()
        # blocks["polygon_map"] = MapPolygon()


class TwoColumnBlock(blocks.StructBlock):

    full_span_header = HeadingBlock(
        required=False, help_text="Optional full width h2 header"
    )
    css_class = blocks.ChoiceBlock(
        choices=[
            ("", "No Style"),
            ("lnp", "LNP"),
            ("highlight", "highlight"),
        ],
        required=False,
        help_text="Select an optional CSS style for this block.",
    )
    left_column = ContentStreamBlock(required=False)
    right_column = ContentStreamBlock(required=False)

    class Meta:
        template = "blocks/two_columns.html"
        label = "Two columns"

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        # Add the class name to the context
        context["block_class"] = "two-column-block"
        return context


class TwoColumnLeftSidebarBlock(blocks.StructBlock):
    full_span_header = HeadingBlock(
        required=False, help_text="Optional full width h2 header"
    )
    sidebar_content = SimpleContentStreamBlock()
    main_content = SimpleContentStreamBlock()

    class Meta:
        template = "blocks/two_column_left_sidebar.html"
        label = "Two columns (left sidebar)"

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        # Add the class name to the context
        context["block_class"] = "two-column-left-sidebar-block"
        return context


class TwoColumnRightSidebarBlock(blocks.StructBlock):
    full_span_header = HeadingBlock(
        required=False, help_text="Optional full width h2 header"
    )
    main_content = SimpleContentStreamBlock()
    sidebar_content = SimpleContentStreamBlock()

    class Meta:
        template = "blocks/two_column_right_sidebar.html"
        label = "Two columns (right sidebar)"

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        # Add the class name to the context
        context["block_class"] = "two-column-right-sidebar-block"
        return context


class ThreeColumnBlock(blocks.StructBlock):
    full_span_header = HeadingBlock(
        required=False, help_text="Optional full width h2 header"
    )
    css_class = blocks.ChoiceBlock(
        choices=[
            ("", "No Style"),
            ("lnp", "LNP"),
            ("highlight", "highlight"),
        ],
        required=False,
        help_text="Select an optional CSS style for this block.",
    )
    left_column = SimpleContentStreamBlock(required=False)
    middle_column = SimpleContentStreamBlock(required=False)
    right_column = SimpleContentStreamBlock(required=False)

    class Meta:
        template = "blocks/three_column.html"
        label = "Three columns"

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        # Add the class name to the context
        context["block_class"] = "three-column-block"
        return context


class LayoutBlock(blocks.StructBlock):

    section = blocks.StreamBlock(
        [
            ("single_column", SingleColumnBlock(required=False)),
            ("left_sidebar", TwoColumnLeftSidebarBlock(required=False)),
            ("right_sidebar", TwoColumnRightSidebarBlock(required=False)),
            ("three_columns", ThreeColumnBlock(required=False)),
        ]
    )

    class Meta:
        template = "blocks/layout_block.html"
        label = "Body layout"


class InlineVideoBlock(blocks.StructBlock):
    embed = EmbedBlock(label="Video URL", max_width=1200, max_height=400)

    class Meta:
        template = "blocks/inline_embed.html"
        icon = "media"
        label = "Inline Video"
