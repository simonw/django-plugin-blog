from django.contrib import admin
from .models import Entry, Tag, Authorship


class AuthorshipInline(admin.TabularInline):
    model = Authorship
    extra = 1


class EntryAdmin(admin.ModelAdmin):
    inlines = (AuthorshipInline,)
    list_display = ("title", "created", "is_draft")
    prepopulated_fields = {"slug": ("title",)}
    list_filter = ("is_draft",)


class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(Entry, EntryAdmin)
admin.site.register(Tag, TagAdmin)
