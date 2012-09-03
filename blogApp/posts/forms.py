import datetime
from django import forms
from blogApp.posts.models import Post


class PostForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea, required=False)
    title = forms.CharField(required=False)
    slug = forms.SlugField(required=False)
    intro = forms.CharField(widget=forms.Textarea, required=False)
    public = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        self.instance = kwargs.pop('instance')
        super(PostForm, self).__init__(*args, **kwargs)
        self.init_from_instance()

    def init_from_instance(self):
        if self.instance is not None:
            self.fields['title'].initial = self.instance.title
            self.fields['intro'].initial = self.instance.intro
            self.fields['slug'].initial = self.instance.slug
            self.fields['content'].initial = self.instance.content
            self.fields['public'].initial = self.instance.published

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if slug is not None:
            c = Post.all().filter('slug = ', slug).get()
            if c:
                if self.instance is None:
                    raise forms.ValidationError('Slug already taken')
                else:
                    if c.key() != self.instance.key():
                        raise forms.ValidationError('Slug already taken')

        return self.cleaned_data.get('slug')

    def clean(self):
        cleaned_data = super(PostForm, self).clean()
        public = cleaned_data.get("public")
        if public:
            content = cleaned_data.get('content')
            title = cleaned_data.get('title')
            intro = cleaned_data.get('intro')
            slug = cleaned_data.get('slug')

            if content is None or  title is None \
                or intro is None or slug is None:
                raise forms.ValidationError("If you want to publish article... everything required")

        return cleaned_data

    def save(self, commit=False):
        clean_d = self.cleaned_data
        if self.instance is None:
            self.instance = Post()
        self.instance.title = clean_d['title']
        self.instance.intro = clean_d['intro']
        self.instance.slug = clean_d['slug']
        self.instance.content = clean_d['content']
        if self.instance.user is None:
            self.instance.user = self.request.user

        if self.instance.published == False and clean_d['public'] \
            and not self.instance.date_published:
            self.instance.date_published = datetime.datetime.now()
        self.instance.published = clean_d['public']

        if commit:
            self.instance.put()

        return self.instance
