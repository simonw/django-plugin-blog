import pytest
from datetime import datetime, timezone
from django.contrib.auth.models import User
from django_plugin_blog.models import Entry, Tag
from xml.etree import ElementTree as ET


@pytest.fixture
def client():
    from django.test import Client

    return Client()


@pytest.fixture
def five_entries():
    author = User.objects.create_user(username="author")
    all = Tag.objects.get_or_create(name="All", slug="all")[0]
    entries = []
    for i in range(5):
        i += 1
        entry = Entry.objects.create(
            title=f"Test Entry {i}",
            slug=f"test-entry-{i}",
            created=datetime(2023, 5, i, tzinfo=timezone.utc),
            summary=f"This is test entry {i}",
            body=f"This is the body of test entry {i}.",
            is_draft=i == 1,
        )
        entry.authors.add(author)
        entry.tags.add(all)
        entries.append(entry)

    return entries


@pytest.mark.django_db
def test_index_page(client, five_entries):
    response = client.get("/blog/")
    html = response.content.decode("utf-8")

    # Should have five entries without a more link
    for i in range(5):
        i += 1
        if i == 1:
            # It's the draft one
            assert f"Test Entry {i}" not in html
            assert f"This is test entry {i}" not in html
        else:
            assert f"Test Entry {i}" in html
            assert f"This is test entry {i}" in html
    assert "Older entries" not in html

    # Add two more entries to get a more link
    Entry.objects.create(
        title="Test Entry 6", slug="test-entry-6", summary=".", body="."
    )
    Entry.objects.create(
        title="Test Entry 7", slug="test-entry-7", summary=".", body="."
    )
    response2 = client.get("/blog/")
    html2 = response2.content.decode("utf-8")
    assert "Older entries" in html2


@pytest.mark.django_db
def test_entry_page(client, five_entries):
    # Test a draft and a not-draft one
    draft_entry = five_entries[0]
    not_draft_entry = five_entries[1]
    for entry, should_be_draft in (
        (draft_entry, True),
        (not_draft_entry, False),
    ):
        response = client.get(f"/blog/{entry.created.year}/{entry.slug}/")
        html = response.content.decode("utf-8")

        # Check that each entry's title and body are present on their respective page
        assert entry.title in html
        assert entry.body in html

        if should_be_draft:
            assert "(draft)" in html
            assert '<meta name="robots" content="noindex">' in html
        else:
            assert "(draft)" not in html
            assert '<meta name="robots" content="noindex">' not in html


@pytest.mark.django_db
@pytest.mark.parametrize(
    "path", ("/blog/", "/blog/archive/", "/blog/2023/", "/blog/tag/all/")
)
def test_draft_entry_not_visible(client, five_entries, path):
    draft_entry = five_entries[0]
    assert draft_entry.title == "Test Entry 1"
    # It should not be on any of the pages
    response = client.get(path)
    html = response.content.decode("utf-8")
    assert draft_entry.title not in html


@pytest.mark.django_db
def test_atom_feed(client, five_entries):
    response = client.get("/blog/feed/")
    assert response.status_code == 200
    assert response["Content-Type"] == "application/xml; charset=utf-8"
    xml = response.content.decode("utf-8")
    et = ET.fromstring(xml)
    assert "<title>testserver</title>" in xml
    expected_entries = [e for e in five_entries if not e.is_draft]
    assert len(expected_entries) == 4
    expected_entries.sort(key=lambda e: e.created, reverse=True)
    # Should have the non-draft entries
    entries = et.findall("{http://www.w3.org/2005/Atom}entry")
    assert len(entries) == 4
    for xml_entry, entry in zip(entries, expected_entries):
        assert xml_entry.find("{http://www.w3.org/2005/Atom}title").text == entry.title
        assert (
            xml_entry.find("{http://www.w3.org/2005/Atom}link").attrib["href"]
            == f"http://testserver/blog/{entry.created.year}/{entry.slug}/"
        )
        assert (
            xml_entry.find(
                "{http://www.w3.org/2005/Atom}author/{http://www.w3.org/2005/Atom}name"
            ).text
            == "author"
        )
