"""
User ORM Model
"""

from typing import List, Optional, TYPE_CHECKING
import uuid
from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.lead import Lead
    from app.models.site_visit import SiteVisit


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Internal user: sales agent, manager, or admin."""
    __tablename__ = "users"

    organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="agent", nullable=False)  # admin | manager | agent
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    organization: Mapped[Optional["Organization"]] = relationship("Organization", back_populates="users")
    assigned_leads: Mapped[List["Lead"]] = relationship("Lead", back_populates="assigned_agent")
    assigned_site_visits: Mapped[List["SiteVisit"]] = relationship("SiteVisit", back_populates="assigned_agent")

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"
