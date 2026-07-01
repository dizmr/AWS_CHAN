from django.contrib import messages
from django.db.models import F
from django.http import JsonResponse, HttpResponseNotAllowed
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator

from .forms import ConfessionForm
from .models import Confession
from .moderation import moderate_confession

LIKED_SESSION_KEY = 'liked_confessions'


def index(request):
    """Публічна стрічка — лише опубліковані (APPROVED) записи."""
    qs = Confession.objects.filter(status=Confession.Status.APPROVED)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    liked = request.session.get(LIKED_SESSION_KEY, [])
    return render(request, 'board/index.html', {
        'page_obj': page_obj,
        'liked': liked,
    })


def create_confession(request):
    if request.method == 'POST':
        form = ConfessionForm(request.POST)
        if form.is_valid():
            confession = form.save()  # status=PENDING за замовчуванням
            moderate_confession(confession)  # одразу проганяємо через модерацію

            if confession.status == Confession.Status.APPROVED:
                messages.success(request, 'Ваше зізнання опубліковано.')
            else:
                messages.warning(
                    request,
                    'Запис не пройшов автоматичну перевірку і не буде опубліковано.'
                )
            return redirect('board:index')
    else:
        form = ConfessionForm()

    return render(request, 'board/create.html', {'form': form})


def detail(request, pk):
    confession = get_object_or_404(
        Confession, pk=pk, status=Confession.Status.APPROVED
    )
    Confession.objects.filter(pk=pk).update(views_count=F('views_count') + 1)
    confession.refresh_from_db(fields=['views_count'])
    liked = str(confession.pk) in request.session.get(LIKED_SESSION_KEY, [])
    return render(request, 'board/detail.html', {
        'confession': confession,
        'liked': liked,
    })


@require_POST
def like_confession(request, pk):
    confession = get_object_or_404(
        Confession, pk=pk, status=Confession.Status.APPROVED
    )
    liked = request.session.get(LIKED_SESSION_KEY, [])
    key = str(confession.pk)

    if key in liked:
        return JsonResponse({'likes_count': confession.likes_count, 'liked': True})

    Confession.objects.filter(pk=pk).update(likes_count=F('likes_count') + 1)
    confession.refresh_from_db(fields=['likes_count'])

    liked.append(key)
    request.session[LIKED_SESSION_KEY] = liked

    return JsonResponse({'likes_count': confession.likes_count, 'liked': True})
