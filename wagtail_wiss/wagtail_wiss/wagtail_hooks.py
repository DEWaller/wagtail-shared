from wagtail.snippets.models import register_snippet

from .viewsets import (
    CategoryViewSet,
    MenuViewSet,
    GalleryViewSet,
    NewsItemViewSet,
    VideoHeaderViewSet,
)


register_snippet(CategoryViewSet)
register_snippet(MenuViewSet)
register_snippet(GalleryViewSet)
register_snippet(VideoHeaderViewSet)
# register_snippet(NewsItemViewSet)
