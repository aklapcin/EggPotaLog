import logging
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required


class PostDashboard(TemplateView):
    #moja paginacja
    @login_required
    def get(self, request, *args, **kwargs):
        return super(PostDashboard, self).get(request, *args, **kwargs)


class NewPost(TemplateView):
    template_name = "posts/new_post.html"

    @login_required
    def get(self, request, *args, **kwargs):
        return super(NewPost, self).get(request, *args, **kwargs)


class EditPost(TemplateView):
    temaplate_name = "posts/edit_post.html"

    @login_required
    def get(self, request, *args, **kwargs):
        return super(EditPost, self).get(request, *args, **kwargs)
