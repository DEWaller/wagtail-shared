from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def paginate(request, object_list, per_page=10):
    paginator = Paginator(object_list, per_page)
    page = request.GET.get("page")

    try:
        objects = paginator.page(page)
    except PageNotAnInteger:
        objects = paginator.page(1)
    except EmptyPage:
        objects = paginator.page(paginator.num_pages)

    return objects