from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    CreateView, TemplateView, DetailView, UpdateView
)
from django.urls import reverse_lazy, reverse
from django.shortcuts import render
from django.contrib.auth import get_user_model

from .forms import CustomUserCreationForm, UserEditForm
from blog.models import Post
from blog.utils import paginate_queryset

User = get_user_model()


class AboutView(TemplateView):
    template_name = 'pages/about.html'


class RulesView(TemplateView):
    template_name = 'pages/rules.html'


class RegistrationView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/registration_form.html'


class ProfileView(DetailView):
    model = User
    template_name = 'blog/profile.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        profile_user = self.object
        viewer = self.request.user

        post_list = (
            Post.objects.filter(author=profile_user)
            .with_comment_count()
            .order_by('-pub_date')
        )

        if viewer != profile_user:
            post_list = post_list.filter(
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now()
            )

        context['page_obj'] = paginate_queryset(self.request, post_list)
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
