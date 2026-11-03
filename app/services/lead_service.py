"""
Lead Management & Algorithmic Qualification Service
"""

from typing import List, Optional, Tuple
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.settings import settings
from app.core.constants import LeadCategory
from app.core.exceptions import EntityNotFoundException, ValidationException
from app.models.lead import Lead
from app.repositories.lead_repository import LeadRepository
from app.schemas.common import PaginatedResponse
from app.schemas.lead import (
    LeadCreate,
    LeadFilter,
    LeadQualificationUpdate,
    LeadResponse,
    LeadUpdate,
)


class LeadService:
    """Service managing lead profiles and deterministic qualification scoring."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = LeadRepository(session)

    async def get_or_create_lead_entity(self, phone: str, name: Optional[str] = None) -> Lead:
        """Fetch existing lead ORM instance or create a new one."""
        lead = await self.repo.get_by_phone(phone)
        if not lead:
            lead = Lead(
                phone=phone,
                name=name,
                lead_category=LeadCategory.COLD.value,
                lead_score=0,
                qualification_reasons=["Initial inquiry received"],
            )
            lead = await self.repo.create(lead)
        elif name and not lead.name:
            lead.name = name
            await self.session.flush()

        return lead

    async def get_or_create_by_phone(self, phone: str, name: Optional[str] = None) -> LeadResponse:
        """Fetch existing lead or initialize a new record upon inbound WhatsApp discovery."""
        lead = await self.get_or_create_lead_entity(phone, name)
        return LeadResponse.model_validate(lead)

    async def create_lead(self, payload: LeadCreate) -> LeadResponse:
        """Create a new lead explicitly with validation."""
        existing = await self.repo.get_by_phone(payload.phone)
        if existing:
            raise ValidationException(f"Lead with phone number '{payload.phone}' already exists")

        lead = Lead(
            organization_id=payload.organization_id,
            phone=payload.phone,
            name=payload.name,
            preferred_location=payload.preferred_location,
            property_type=payload.property_type,
            bedroom_preference=payload.bedroom_preference,
            budget_min=payload.budget_min,
            budget_max=payload.budget_max,
            purchase_timeline=payload.purchase_timeline,
            financing_status=payload.financing_status,
            assigned_agent_id=payload.assigned_agent_id,
            consent_status=payload.consent_status,
        )
        saved = await self.repo.create(lead)
        # Calculate initial score
        scored = await self.recalculate_qualification(saved.id)
        return scored

    async def get_lead_by_id(self, lead_id: uuid.UUID) -> LeadResponse:
        """Retrieve lead by ID or raise 404."""
        lead = await self.repo.get_by_id(lead_id)
        if not lead:
            raise EntityNotFoundException(f"Lead with ID '{lead_id}' not found")
        return LeadResponse.model_validate(lead)

    async def list_leads(self, filters: LeadFilter) -> PaginatedResponse[LeadResponse]:
        """List and filter leads with pagination."""
        items, total = await self.repo.filter_leads(filters)
        total_pages = (total + filters.page_size - 1) // filters.page_size if total > 0 else 0
        return PaginatedResponse(
            items=[LeadResponse.model_validate(lead) for lead in items],
            total=total,
            page=filters.page,
            page_size=filters.page_size,
            total_pages=total_pages,
        )

    async def update_lead(self, lead_id: uuid.UUID, payload: LeadUpdate) -> LeadResponse:
        """Update lead attributes and trigger qualification scoring update if preferences changed."""
        lead = await self.repo.get_by_id(lead_id)
        if not lead:
            raise EntityNotFoundException(f"Lead with ID '{lead_id}' not found")

        update_dict = payload.model_dump(exclude_unset=True)
        if "lead_category" in update_dict and update_dict["lead_category"]:
            update_dict["lead_category"] = update_dict["lead_category"].value

        updated = await self.repo.update(lead, update_dict)
        return LeadResponse.model_validate(updated)

    @staticmethod
    def compute_qualification_breakdown(
        budget_max: Optional[int] = None,
        budget_min: Optional[int] = None,
        purchase_timeline: Optional[str] = None,
        preferred_location: Optional[str] = None,
        property_type: Optional[str] = None,
        bedroom_preference: Optional[int] = None,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        has_active_site_visit: bool = False,
    ) -> Tuple[int, LeadCategory, List[str], dict]:
        """
        Pure deterministic multi-criteria lead scoring (0 to 100 points):
        - Budget Clarity (up to 30 pts)
        - Purchase Timeline (up to 30 pts)
        - Preference Specificity (up to 20 pts)
        - Identity & Engagement (up to 20 pts)
        - Active Site Visit Engagement Bonus (up to 20 pts)
        Returns: (total_score_clamped, category, reasons_list, breakdown_dict)
        """
        reasons: List[str] = []
        breakdown = {
            "budget_score": 0,
            "timeline_score": 0,
            "preference_score": 0,
            "identity_score": 0,
            "engagement_bonus": 0,
        }

        # 1. Budget clarity (max 30 pts)
        if budget_max and budget_max > 0:
            breakdown["budget_score"] = 30
            reasons.append(f"Budget specified up to INR {budget_max:,} (+30)")
        elif budget_min and budget_min > 0:
            breakdown["budget_score"] = 15
            reasons.append(f"Starting budget specified from INR {budget_min:,} (+15)")

        # 2. Timeline readiness (max 30 pts)
        timeline = (purchase_timeline or "").lower().strip()
        if any(term in timeline for term in ["immediate", "now", "this month", "< 1 month", "urgent", "ready"]):
            breakdown["timeline_score"] = 30
            reasons.append("Immediate buying timeline (< 1 month) (+30)")
        elif any(term in timeline for term in ["1-3", "2 months", "3 months", "soon", "near"]):
            breakdown["timeline_score"] = 15
            reasons.append("Near-term buying timeline (1-3 months) (+15)")
        elif timeline:
            breakdown["timeline_score"] = 5
            reasons.append("Long-term exploration timeline (> 3 months) (+5)")

        # 3. Preference specificity (max 20 pts)
        pref_pts = 0
        if preferred_location and preferred_location.strip():
            pref_pts += 10
            reasons.append(f"Target location specified: {preferred_location.strip()} (+10)")
        if property_type or bedroom_preference:
            pref_pts += 10
            reasons.append("Unit type/BHK preference defined (+10)")
        breakdown["preference_score"] = min(pref_pts, 20)

        # 4. Identity verification (max 20 pts)
        ident_pts = 0
        if name and len(name.strip()) >= 2:
            ident_pts += 10
            reasons.append(f"Prospect name verified: {name.strip()} (+10)")
        if phone and len(phone.strip()) >= 10:
            ident_pts += 10
            reasons.append("Verified mobile communication channel (+10)")
        breakdown["identity_score"] = min(ident_pts, 20)

        # 5. Site visit engagement bonus (20 pts) - does not overwrite timeline
        if has_active_site_visit:
            breakdown["engagement_bonus"] = 20
            reasons.append("Active site visit appointment scheduled (+20)")

        raw_score = sum(breakdown.values())
        final_score = min(max(raw_score, 0), 100)

        if final_score >= settings.LEAD_SCORE_HOT_THRESHOLD:
            category = LeadCategory.HOT
        elif final_score >= settings.LEAD_SCORE_WARM_THRESHOLD:
            category = LeadCategory.WARM
        else:
            category = LeadCategory.COLD

        breakdown["total_score"] = final_score
        breakdown["category"] = category.value
        return final_score, category, reasons, breakdown

    async def calculate_and_update_qualification(
        self,
        lead: Lead,
        has_active_site_visit: Optional[bool] = None,
    ) -> Lead:
        """
        Executes deterministic lead scoring directly on an ORM Lead entity.
        Automatically queries site visits if has_active_site_visit is not explicitly passed.
        """
        if has_active_site_visit is None:
            from app.models.site_visit import SiteVisit
            from sqlalchemy import select
            visit_check = await self.session.execute(
                select(SiteVisit.id).where(
                    SiteVisit.lead_id == lead.id,
                    SiteVisit.status.in_(["REQUESTED", "CONFIRMED"]),
                ).limit(1)
            )
            has_active_site_visit = visit_check.scalars().first() is not None

        score, category, reasons, _ = self.compute_qualification_breakdown(
            budget_max=lead.budget_max,
            budget_min=lead.budget_min,
            purchase_timeline=lead.purchase_timeline,
            preferred_location=lead.preferred_location,
            property_type=lead.property_type,
            bedroom_preference=lead.bedroom_preference,
            name=lead.name,
            phone=lead.phone,
            has_active_site_visit=has_active_site_visit,
        )

        return await self.repo.update_qualification(
            lead=lead,
            score=score,
            category=category,
            reasons=reasons,
        )

    async def recalculate_qualification(self, lead_id: uuid.UUID) -> LeadResponse:
        """
        Executes deterministic multi-criteria lead scoring (0 to 100 points) by lead UUID.
        """
        lead = await self.repo.get_by_id(lead_id)
        if not lead:
            raise EntityNotFoundException(f"Lead with ID '{lead_id}' not found")

        updated = await self.calculate_and_update_qualification(lead)
        return LeadResponse.model_validate(updated)
