from django.utils import timezone
from django.db.models import Count
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    CreateView, TemplateView, DetailView, UpdateView
)
from django.urls import reverse_lazy, reverse
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator

from .forms import CustomUserCreationForm, UserEditForm
from blog.models import Post

User = get_user_model()


class AboutView(TemplateView):
    template_name = 'pages/about.html'


class RulesView(TemplateView):
    template_name = 'pages/rules.html'


class RegistrationView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('blog:index')
    template_name = 'registration/registration_form.html'


class ProfileView(DetailView):
    model = User
    template_name = 'blog/profile.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # The profile owner
        profile_user = self.object

        # The person viewing the page
        viewer = self.request.user

        post_list = Post.objects.filter(author=profile_user).annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')

        # If the viewer is not the profile owner, filter for public posts
        if viewer != profile_user:
            post_list = post_list.filter(
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now()
            )

        paginator = Paginator(post_list, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserEditForm
    template_name = 'registration/registration_form.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)


def server_error(request):
    return render(request, 'pages/500.html', status=500)


def csrf_failure(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)
