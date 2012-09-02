import logging
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.contrib import messages
from django.utils.decorators import method_decorator

from misc.paginator import create_paginator

from blogApp.posts.models import Post
from blogApp.posts.forms import PostForm


class PostDashboard(TemplateView):

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        ctx = RequestContext(request)
        query = Post.all()

        paginator = create_paginator(request=request, query=query, \
            possible_ordering=["title", "published", "date_created", "last_edited"])

        ctx['paginator'] = paginator
        ctx['per_page'] = paginator.per_page
        ctx['order_by'] = paginator.order_by

        return render_to_response('posts/dashboard.html', {}, context_instance=ctx)


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
        form = PostForm(request=request, instance=None)
        if form.is_valid():
            post = form.save(commit=True)
            if post.title:
                msg = "Blog post %s have been created" % post.title
                msg += post.public and " and published" or "."
            else:
                msg = "New blog post have bee created."

            messages.info(request, msg)
            return HttpResponseRedirect(reverse('post_dashboard'))
        else:
            ctx = RequestContext(request)
            ctx['form'] = form
            import pdb; pdb.set_trace()

        return render_to_response(self.template_name, {}, context_instance=ctx)


class EditPost(TemplateView):
    temaplate_name = "posts/edit_post.html"

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

        form = PostForm(request=request, instance=post)
        if form.is_valid():
            post = form.save(commit=True)
            if post.title:
                msg = "Blog post %s have been edited" % post.title
                msg += post.public and " and published" or "."
            else:
                msg = "Blog post have been edited."

            messages.info(request, msg)
            return HttpResponseRedirect(reverse('post_dashboars'))
        else:
            ctx = RequestContext(request)
            ctx['form'] = form
            ctx['post'] = post
        return render_to_response(self.template_name, {}, context_instance=ctx)
