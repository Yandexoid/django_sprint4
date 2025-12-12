from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .models import Post, Category


def index(request):
    posts = Post.objects.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    ).select_related('category', 'location').order_by('-pub_date')[:5]

    template = 'blog/index.html'
    context = {
        'post_list': posts,
    }
    return render(request, template, context)


def post_detail(request, pk):
    post = get_object_or_404(
        Post.objects.select_related('category', 'location', 'author'),
        pk=pk,
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    )
    template = 'blog/detail.html'
    context = {
        'post': post,
    }
    return render(request, template, context)


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    posts = Post.objects.filter(
        category=category,
        is_published=True,
        pub_date__lte=timezone.now()
    ).select_related('location').order_by('-pub_date')

    template = 'blog/category.html'
    context = {
        'category': category,
        'post_list': posts,
    }
    return render(request, template, context)
