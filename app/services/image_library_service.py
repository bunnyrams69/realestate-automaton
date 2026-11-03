"""
Image Library Retrieval Service
Recursively scans the image repository, manages location-to-image mappings,
and retrieves illustrative neighbourhood visuals for WhatsApp sales engagement.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel, Field

from app.config.settings import settings
from app.core.logging import logger

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


class ImageMetadata(BaseModel):
    """Metadata representing an image in the library."""
    location: str
    filename: str
    filepath: str
    url: str
    title: str = ""
    description: str = ""
    is_illustrative: bool = True
    type: str = "location"


class ImageLibraryService:
    """
    Centralized image indexing and retrieval service.
    Supports directory scanning, image manifest integration, and multi-image delivery per location.
    """

    def __init__(self, base_path: Optional[str] = None):
        self.base_path = Path(base_path or settings.IMAGE_LIBRARY_PATH)
        self._location_map: Dict[str, List[ImageMetadata]] = {}
        self._manifest_path = self.base_path / "image_manifest.json"
        self.refresh_index()

    def refresh_index(self) -> None:
        """
        Scans the image directory and parses image_manifest.json (if present)
        to build a robust location-to-images index.
        """
        self._location_map.clear()
        if not self.base_path.exists():
            logger.warning(f"Image library path '{self.base_path}' does not exist.")
            return

        base_url = settings.WEBHOOK_BASE_URL.rstrip("/")

        # 1. Load from manifest if available
        manifest_locations: Set[str] = set()
        if self._manifest_path.exists():
            try:
                with open(self._manifest_path, "r", encoding="utf-8") as f:
                    manifest_data = json.load(f)
                
                for loc_key, items in manifest_data.get("locations", {}).items():
                    norm_loc = loc_key.lower().strip()
                    manifest_locations.add(norm_loc)
                    if norm_loc not in self._location_map:
                        self._location_map[norm_loc] = []
                    
                    for item in items:
                        fname = item.get("filename")
                        fpath = self.base_path / fname
                        if fpath.exists():
                            # Web-accessible URL
                            url = f"{base_url}/static/images/{fname}" if base_url else f"/static/images/{fname}"
                            self._location_map[norm_loc].append(
                                ImageMetadata(
                                    location=norm_loc,
                                    filename=fname,
                                    filepath=str(fpath),
                                    url=url,
                                    title=item.get("title", f"{norm_loc.title()} View"),
                                    description=item.get("description", ""),
                                    type=item.get("type", "location"),
                                )
                            )
                logger.info(f"Loaded {sum(len(v) for v in self._location_map.values())} images from manifest across {len(manifest_locations)} locations.")
            except Exception as e:
                logger.error(f"Failed to read image manifest {self._manifest_path}: {e}")

        # 2. Recursively scan directory for any unindexed image files or subdirectories
        for root, dirs, files in os.walk(self.base_path):
            root_path = Path(root)
            # Check if this subdirectory represents a location
            rel_dir = root_path.relative_to(self.base_path)
            dir_location = rel_dir.parts[0].lower().strip() if rel_dir.parts else ""

            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext not in SUPPORTED_EXTENSIONS:
                    continue

                full_path = root_path / file
                rel_path = full_path.relative_to(self.base_path).as_posix()
                fname_lower = file.lower()

                # Determine location: either from subdirectory, or file name keywords
                loc = dir_location
                if not loc:
                    for known_loc in ("gachibowli", "kokapet", "financial district", "financial_district", "kondapur", "nanakramguda", "whitefield", "madhapur", "jubilee hills", "banjara hills"):
                        if known_loc.replace("_", " ") in fname_lower or known_loc.replace(" ", "_") in fname_lower:
                            loc = known_loc.replace("_", " ")
                            break

                if not loc:
                    continue

                norm_loc = loc.lower().strip()
                if norm_loc not in self._location_map:
                    self._location_map[norm_loc] = []

                # Avoid duplicate entries already loaded from manifest
                existing_files = {m.filename for m in self._location_map[norm_loc]}
                if file not in existing_files and rel_path not in existing_files:
                    url = f"{base_url}/static/images/{rel_path}" if base_url else f"/static/images/{rel_path}"
                    self._location_map[norm_loc].append(
                        ImageMetadata(
                            location=norm_loc,
                            filename=file,
                            filepath=str(full_path),
                            url=url,
                            title=f"{norm_loc.title()} Architecture",
                            description=f"Illustrative neighbourhood view in {norm_loc.title()}.",
                            type="location",
                        )
                    )

        logger.info(f"Image library indexed: {list(self._location_map.keys())} ({sum(len(v) for v in self._location_map.values())} total images).")

    def get_supported_locations(self) -> List[str]:
        """Returns all distinct location names indexed in the image library."""
        return sorted(list(self._location_map.keys()))

    def has_images_for_location(self, location: str) -> bool:
        """Checks if verified location images exist for the given query."""
        norm = self._normalize_location(location)
        return norm in self._location_map and len(self._location_map[norm]) > 0

    def get_images_for_location(
        self,
        location: str,
        limit: int = 4,
        exclude_filenames: Optional[Set[str]] = None,
    ) -> List[ImageMetadata]:
        """
        Retrieves up to `limit` relevant images for a location.
        Skips any filenames in `exclude_filenames` to prevent duplicate dispatches in a single session.
        """
        norm = self._normalize_location(location)
        if not norm or norm not in self._location_map:
            logger.info(f"Image retrieval: No images found for location '{location}' (normalized: '{norm}').")
            return []

        all_imgs = self._location_map[norm]
        exclude = exclude_filenames or set()

        # Prioritize unseen images, then cycle if needed
        unseen = [img for img in all_imgs if img.filename not in exclude]
        results = unseen[:limit] if unseen else all_imgs[:limit]

        logger.info(
            f"Image retrieval: location='{location}', available={len(all_imgs)}, excluded={len(exclude)}, returning={len(results)}"
        )
        return results

    def build_illustrative_caption(self, location: str, image_metadata: Optional[ImageMetadata] = None) -> str:
        """
        Creates a polite, clear caption emphasizing that this is an illustrative neighbourhood view,
        never claiming it is an actual private property photograph.
        """
        title = image_metadata.title if image_metadata and image_metadata.title else f"{location.title()} Area"
        return f"📍 {title}\n(Illustrative neighbourhood view of {location.title()} — not an actual private property photograph)"

    def _normalize_location(self, location: str) -> str:
        loc = location.lower().strip()
        loc = loc.replace("financial_district", "financial district")
        for k in self._location_map.keys():
            if k in loc or loc in k:
                return k
        return loc


# Global singleton instance
image_library_service = ImageLibraryService()
