from django.contrib.syndication.views import Feed
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.utils.feedgenerator import Atom1Feed
from django.urls import reverse
from .models import Entry, Tag

base_template = (
    getattr(settings, "DJANGO_PLUGIN_BLOG_BASE_TEMPLATE", None)
    or "django_plugin_blog/base.html"
)

ENTRIES_ON_HOMEPAGE = 5


def index(request):
    entries = list(
        Entry.objects.filter(is_draft=False).order_by("-created")[
            : ENTRIES_ON_HOMEPAGE + 1
        ]
    )
    has_more = False
    if len(entries) > ENTRIES_ON_HOMEPAGE:
        has_more = True
        entries = entries[:ENTRIES_ON_HOMEPAGE]
    return render(
        request,
        "django_plugin_blog/index.html",
        {
            "base_template": base_template,
            "atom_url": reverse("django_plugin_blog_feed"),
            "entries": entries,
            "has_more": has_more,
        },
    )


def entry(request, year, slug):
    entry = get_object_or_404(Entry, created__year=year, slug=slug)
    return render(
        request,
        "django_plugin_blog/entry.html",
        {"base_template": base_template, "entry": entry},
    )


def year(request, year):
    entries = Entry.objects.filter(created__year=year, is_draft=False).order_by(
        "-created"
    )
    return render(
        request,
        "django_plugin_blog/year.html",
        {"base_template": base_template, "entries": entries, "year": year},
    )


def archive(request):
    entries = Entry.objects.filter(is_draft=False).order_by("-created")
    return render(
        request,
        "django_plugin_blog/archive.html",
        {"base_template": base_template, "entries": entries},
    )


def tag(request, slug):
    tag = Tag.objects.get(slug=slug)
    entries = tag.entry_set.filter(is_draft=False).order_by("-created")
    return render(
        request,
        "django_plugin_blog/tag.html",
        {"base_template": base_template, "tag": tag, "entries": entries},
    )


class BlogFeed(Feed):
    link = "/blog/"
    feed_type = Atom1Feed

    def get_object(self, request):
        return request

    def title(self, obj):
        return (
            getattr(settings, "DJANGO_PLUGIN_BLOG_FEED_TITLE", None) or obj.get_host()
        )

    def link(self, obj):
        return reverse("django_plugin_blog_index")

    def items(self):
        return Entry.objects.filter(is_draft=False).order_by("-created")[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.summary_rendered + "\n" + item.body_rendered

    def item_link(self, item):
        return "/blog/%d/%s/" % (item.created.year, item.slug)

    def item_author_name(self, item):
        return (
            ", ".join([a.get_full_name() or str(a) for a in item.authors.all()]) or None
        )

    def get_feed(self, obj, request):
        feedgen = super().get_feed(obj, request)
        feedgen.content_type = "application/xml; charset=utf-8"
        return feedgen
