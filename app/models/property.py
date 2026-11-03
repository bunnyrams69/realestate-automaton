"""
Property Inventory ORM Model
"""

from typing import Any, Dict, List, Optional, TYPE_CHECKING
import uuid
from sqlalchemy import BigInteger, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.constants import PropertyStatus, PropertyType
from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.match import LeadPropertyMatch
    from app.models.site_visit import SiteVisit


class Property(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Authoritative real estate inventory catalog listing."""
    __tablename__ = "properties"

    organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    property_type: Mapped[str] = mapped_column(
        String(50),
        default=PropertyType.APARTMENT.value,
        nullable=False,
        index=True,
    )
    location: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    price_min: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    price_max: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    bedrooms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    bathrooms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    area_sqft: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    amenities: Mapped[List[str]] = mapped_column(JSONB, default=list, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50),
        default=PropertyStatus.AVAILABLE.value,
        nullable=False,
        index=True,
    )
    images: Mapped[List[str]] = mapped_column(JSONB, default=list, nullable=False)
    metadata_json: Mapped[Dict[str, Any]] = mapped_column("metadata", JSONB, default=dict, nullable=False)

    # Relationships
    organization: Mapped[Optional["Organization"]] = relationship("Organization", back_populates="properties")
    lead_matches: Mapped[List["LeadPropertyMatch"]] = relationship("LeadPropertyMatch", back_populates="property")
    site_visits: Mapped[List["SiteVisit"]] = relationship("SiteVisit", back_populates="property")

    __table_args__ = (
        Index(
            "ix_properties_matching_filter",
            "property_type",
            "status",
            "price_min",
            "price_max",
        ),
    )

    def __repr__(self) -> str:
        return f"<Property id={self.id} name='{self.name}' type={self.property_type} loc='{self.location}'>"
