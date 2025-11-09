from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def make_fish_questions(n=55):
    tags = ["WEB", "Технопарк", "Python", "Django", "Algorithms"]
    questions = []
    for i in range(1, n + 1):
        questions.append({
            "id": i,
            "title": f"Заголовок вопроса {i}",
            "text": f"Текст вопроса {i}. Короткое описание сути проблемы.",
            "answers_count": (i * 3) % 7,
            "tags": [tags[i % len(tags)], tags[(i + 2) % len(tags)]],
            "rating": (i * 7) % 10,
            "avatar_url": "/static/img/avatar.png",
        })
    return questions

def paginate(objects_list, request, per_page=10):
    try:
        per_page = int(request.GET.get("per_page", per_page))
        if per_page <= 0:
            per_page = 10
    except (TypeError, ValueError):
        per_page = 10

    page_number = request.GET.get("page", 1)
    paginator = Paginator(objects_list, per_page)
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    return page
