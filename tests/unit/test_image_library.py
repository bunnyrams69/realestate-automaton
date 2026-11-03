"""
Unit Tests for Image Library Retrieval Service
Verifies directory indexing, manifest parsing, multi-image retrieval,
illustrative disclaimers, and deduplication logic.
"""

import pytest
from app.services.image_library_service import ImageLibraryService, image_library_service


def test_supported_locations_indexed():
    """Verify that all target real estate locations are properly indexed."""
    locations = image_library_service.get_supported_locations()
    expected = ["financial district", "gachibowli", "kokapet", "kondapur", "nanakramguda", "whitefield"]
    for loc in expected:
        assert loc in locations, f"Expected location '{loc}' not found in indexed locations: {locations}"


def test_has_images_for_known_locations():
    """Verify that known locations report available images."""
    assert image_library_service.has_images_for_location("gachibowli") is True
    assert image_library_service.has_images_for_location("Gachibowli") is True
    assert image_library_service.has_images_for_location("Kokapet") is True
    assert image_library_service.has_images_for_location("Financial District") is True
    assert image_library_service.has_images_for_location("Kondapur") is True
    assert image_library_service.has_images_for_location("Nanakramguda") is True


def test_has_no_images_for_unknown_location():
    """Verify that locations with no images return False."""
    assert image_library_service.has_images_for_location("Jubilee Hills") is False
    assert image_library_service.has_images_for_location("Random City") is False


def test_multi_image_retrieval_limit():
    """Verify that multi-image retrieval returns up to requested limit."""
    imgs = image_library_service.get_images_for_location("gachibowli", limit=2)
    assert len(imgs) >= 1
    assert len(imgs) <= 2
    for img in imgs:
        assert img.location == "gachibowli"
        assert img.url.startswith("http") or img.url.startswith("/static")
        assert img.filepath != ""


def test_illustrative_caption_generation():
    """Verify that captions explicitly mention illustrative disclaimer and never claim private ownership."""
    imgs = image_library_service.get_images_for_location("kokapet", limit=1)
    assert len(imgs) > 0
    img = imgs[0]
    caption = image_library_service.build_illustrative_caption("kokapet", img)
    assert "Illustrative neighbourhood view" in caption
    assert "Kokapet" in caption
    assert "not an actual private property photograph" in caption


def test_deduplication_excludes_sent_images():
    """Verify that excluding already sent filenames prevents repeating the same image."""
    first_batch = image_library_service.get_images_for_location("gachibowli", limit=1)
    assert len(first_batch) == 1
    sent_filename = first_batch[0].filename

    # Now request with exclude_filenames containing the first image
    second_batch = image_library_service.get_images_for_location(
        "gachibowli", limit=1, exclude_filenames={sent_filename}
    )
    if len(image_library_service._location_map["gachibowli"]) > 1:
        assert second_batch[0].filename != sent_filename
