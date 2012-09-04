from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

from misc.paginator import create_paginator

from blogApp.posts.models import Post
from blogApp.posts.forms import PostForm

from blogApp.utils import json_response


class PostDashboard(TemplateView):

    @method_decorator(ensure_csrf_cookie)
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        ctx = RequestContext(request)
        query = Post.all()

        paginator = create_paginator(request=request, query=query, \
            possible_ordering=["title", "published", "date_created", "last_edited"])

        ctx['paginator'] = paginator

        return render_to_response('posts/dashboard.html', {}, context_instance=ctx)


class MainPage(TemplateView):

    def get(self, request, *args, **kwargs):
        ctx = RequestContext(request)
        query = Post.all().filter('published = ', True).order('-date_published')

        paginator = create_paginator(request=request, query=query)

        ctx['paginator'] = paginator
        ctx['per_page'] = paginator.per_page

        return render_to_response('posts/main_page.html', {}, context_instance=ctx)


class ShowPost(TemplateView):

    def get(self, request, *args, **kwargs):
        post_slug = kwargs.get('post_slug')
        ctx = RequestContext(request)
        query = Post.all().filter('published = ', True).filter('slug = ', post_slug).fetch(1)
        if not query:
            raise Http404
        ctx['post'] = query[0]

        return render_to_response('posts/show_post.html', {}, context_instance=ctx)


class PreviewPost(TemplateView):

    def get(self, request, *args, **kwargs):
        post_key = kwargs.get('post_key')
        ctx = RequestContext(request)
        query = Post.get(post_key)
        if not query:
            raise Http404
        ctx['post'] = query

        return render_to_response('posts/show_post.html', {}, context_instance=ctx)


class NewPost(TemplateView):
    template_name = "posts/new_post.html"

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        form = PostForm(request=request, instance=None)
        ctx = RequestContext(request)
        ctx['form'] = form
        return render_to_response(self.template_name, {}, context_instance=ctx)

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        form = PostForm(request.POST, request=request, instance=None)
        if form.is_valid():
            post = form.save(commit=True)
            if post.title:
                msg = "Blog post %s have been created" % post.title
                msg += post.published and " and published" or "."
            else:
                msg = "New blog post have bee created."

            next = form.cleaned_data.get('next')
            if next == 'dashboard' or not next:
                messages.info(request, msg)
                return HttpResponseRedirect(reverse('post_dashboard'))
            if next == 'here':
                messages.info(request, msg)
                return HttpResponseRedirect(reverse('edit_post', kwargs={'post_key': str(post.key())}))
            if next == 'preview':
                return HttpResponseRedirect(reverse('preview_post', kwargs={'post_preview': str(post.key())}))
        else:
            ctx = RequestContext(request)
            ctx['form'] = form

        return render_to_response(self.template_name, {}, context_instance=ctx)


class EditPost(TemplateView):
    template_name = "posts/edit_post.html"

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        key = kwargs.get('post_key')
        post = Post.get(key)
        if post is None:
            raise Http404
        form = PostForm(request=request, instance=post)
        ctx = RequestContext(request)
        ctx['form'] = form
        ctx['post'] = post
        return render_to_response(self.template_name, {}, context_instance=ctx)

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        key = kwargs.get('post_key')
        post = Post.get(key)
        if post is None:
            raise Http404

        form = PostForm(request.POST, request=request, instance=post)
        if form.is_valid():
            post = form.save(commit=True)

            if post.title:
                msg = "Blog post %s have been edited" % post.title
                msg += post.published and " and published" or "."
            else:
                msg = "Blog post have been edited."

            next = form.cleaned_data.get('next')
            if next == 'dashboard' or not next:
                messages.info(request, msg)
                return HttpResponseRedirect(reverse('post_dashboard'))
            if next == 'here':
                messages.info(request, msg)
                return HttpResponseRedirect(reverse('edit_post', kwargs={'post_key': str(post.key())}))
            if next == 'preview':
                return HttpResponseRedirect(reverse('preview_post', kwargs={'post_preview': str(post.key())}))
        else:
            ctx = RequestContext(request)
            ctx['form'] = form
            ctx['post'] = post
        return render_to_response(self.template_name, {}, context_instance=ctx)


@json_response
@login_required
def delete_post(request, post_key=None):
    if request.method != 'POST':
        return {'status': 'error', 'msg': 'only_post', 'code': 405}
    if post_key is None:
        return {'status': 'error', 'msg': 'post_id_not_provided', 'code': 400}

    post = Post.get(post_key)
    if post is None:
        return {'status': 'error', 'msg': 'post_not_found', 'code': 404}
    post.delete()
    return {'status': 'OK', 'msg': reverse('post_dashboard')}
