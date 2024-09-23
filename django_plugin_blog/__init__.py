from django.urls import path
from django.conf import settings
import djp


@djp.hookimpl
def installed_apps():
    return ["django_plugin_blog"]


@djp.hookimpl
def urlpatterns():
    from .views import index, entry, year, archive, tag, BlogFeed

    blog = getattr(settings, "DJANGO_PLUGIN_BLOG_URL_PREFIX", None) or "blog"
    return [
        path(f"{blog}/", index, name="django_plugin_blog_index"),
        path(f"{blog}/<int:year>/<slug:slug>/", entry, name="django_plugin_blog_entry"),
        path(f"{blog}/archive/", archive, name="django_plugin_blog_archive"),
        path(f"{blog}/<int:year>/", year, name="django_plugin_blog_year"),
        path(f"{blog}/tag/<slug:slug>/", tag, name="django_plugin_blog_tag"),
        path(f"{blog}/feed/", BlogFeed(), name="django_plugin_blog_feed"),
    ]
