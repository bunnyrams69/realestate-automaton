"""
Dashboard & Analytics REST Endpoints
Provides real-time marketing intelligence: lead pipeline, conversion funnel,
property demand heatmap, and AI decision audit trail.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select, case, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.constants import (
    ConversationState,
    FollowUpStatus,
    LeadCategory,
    PropertyStatus,
    SiteVisitStatus,
)
from app.db.session import get_db_session
from app.models.ai_decision import AIDecision
from app.models.conversation import Conversation
from app.models.follow_up import FollowUpTask
from app.models.lead import Lead
from app.models.message import Message
from app.models.property import Property
from app.models.site_visit import SiteVisit
from app.models.webhook import WebhookEvent

router = APIRouter(prefix="/dashboard", tags=["Dashboard & Analytics"])


@router.get("/overview", summary="Platform Overview KPIs")
async def get_overview(session: AsyncSession = Depends(get_db_session)) -> Dict[str, Any]:
    """
    Returns key performance indicators:
    - Total leads by category (HOT/WARM/COLD)
    - Active conversations count
    - Scheduled site visits (requested + confirmed)
    - Properties available
    - Pending follow-ups
    """
    # Lead tier distribution
    lead_dist = await session.execute(
        select(Lead.lead_category, func.count(Lead.id)).group_by(Lead.lead_category)
    )
    leads_by_category = {row[0]: row[1] for row in lead_dist.all()}
    total_leads = sum(leads_by_category.values())

    # Active conversations
    active_convos = await session.execute(
        select(func.count(Conversation.id)).where(
            Conversation.state.notin_([
                ConversationState.CLOSED.value,
                ConversationState.OPTED_OUT.value,
            ])
        )
    )
    active_count = active_convos.scalar() or 0

    # Upcoming site visits
    upcoming_visits = await session.execute(
        select(func.count(SiteVisit.id)).where(
            SiteVisit.status.in_([
                SiteVisitStatus.REQUESTED.value,
                SiteVisitStatus.CONFIRMED.value,
            ]),
            SiteVisit.scheduled_time >= datetime.now(timezone.utc),
        )
    )
    upcoming_visit_count = upcoming_visits.scalar() or 0

    # Available properties
    available_props = await session.execute(
        select(func.count(Property.id)).where(
            Property.status == PropertyStatus.AVAILABLE.value
        )
    )
    property_count = available_props.scalar() or 0

    # Pending follow-ups
    pending_fups = await session.execute(
        select(func.count(FollowUpTask.id)).where(
            FollowUpTask.status == FollowUpStatus.PENDING.value
        )
    )
    pending_count = pending_fups.scalar() or 0

    return {
        "total_leads": total_leads,
        "leads_by_category": {
            "HOT": leads_by_category.get(LeadCategory.HOT.value, 0),
            "WARM": leads_by_category.get(LeadCategory.WARM.value, 0),
            "COLD": leads_by_category.get(LeadCategory.COLD.value, 0),
        },
        "active_conversations": active_count,
        "upcoming_site_visits": upcoming_visit_count,
        "available_properties": property_count,
        "pending_follow_ups": pending_count,
    }


@router.get("/conversion-funnel", summary="Lead-to-Visit Conversion Funnel")
async def get_conversion_funnel(
    days: int = Query(30, ge=1, le=365, description="Lookback period in days"),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """
    Returns the conversion funnel:
    Enquiries → Qualified (WARM+HOT) → Site Visit Booked → Visit Completed
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    # Total leads created in window
    total_leads = await session.execute(
        select(func.count(Lead.id)).where(Lead.created_at >= cutoff)
    )

    # Qualified (WARM + HOT)
    qualified = await session.execute(
        select(func.count(Lead.id)).where(
            Lead.created_at >= cutoff,
            Lead.lead_category.in_([LeadCategory.HOT.value, LeadCategory.WARM.value]),
        )
    )

    # Site visits booked
    visits_booked = await session.execute(
        select(func.count(SiteVisit.id)).where(SiteVisit.created_at >= cutoff)
    )

    # Site visits completed
    visits_completed = await session.execute(
        select(func.count(SiteVisit.id)).where(
            SiteVisit.created_at >= cutoff,
            SiteVisit.status == SiteVisitStatus.COMPLETED.value,
        )
    )

    total = total_leads.scalar() or 0
    qual = qualified.scalar() or 0
    booked = visits_booked.scalar() or 0
    completed = visits_completed.scalar() or 0

    return {
        "period_days": days,
        "funnel": {
            "enquiries": total,
            "qualified_leads": qual,
            "site_visits_booked": booked,
            "site_visits_completed": completed,
        },
        "rates": {
            "qualification_rate": round(qual / total * 100, 1) if total else 0,
            "booking_rate": round(booked / qual * 100, 1) if qual else 0,
            "completion_rate": round(completed / booked * 100, 1) if booked else 0,
        },
    }


@router.get("/property-demand", summary="Property Demand Heatmap")
async def get_property_demand(
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """
    Returns demand signals aggregated from lead preferences:
    - Top locations by lead interest
    - Top property types by demand
    - Budget distribution
    """
    # Top locations
    location_query = await session.execute(
        select(Lead.preferred_location, func.count(Lead.id))
        .where(Lead.preferred_location.isnot(None))
        .group_by(Lead.preferred_location)
        .order_by(func.count(Lead.id).desc())
        .limit(10)
    )
    top_locations = [{"location": r[0], "lead_count": r[1]} for r in location_query.all()]

    # Top property types
    type_query = await session.execute(
        select(Lead.property_type, func.count(Lead.id))
        .where(Lead.property_type.isnot(None))
        .group_by(Lead.property_type)
        .order_by(func.count(Lead.id).desc())
    )
    top_types = [{"type": r[0], "lead_count": r[1]} for r in type_query.all()]

    # Budget distribution buckets
    budget_query = await session.execute(
        select(
            case(
                (Lead.budget_max < 5000000, "Under 50L"),
                (Lead.budget_max < 10000000, "50L - 1Cr"),
                (Lead.budget_max < 20000000, "1Cr - 2Cr"),
                (Lead.budget_max < 50000000, "2Cr - 5Cr"),
                else_="5Cr+",
            ).label("bucket"),
            func.count(Lead.id),
        )
        .where(Lead.budget_max.isnot(None), Lead.budget_max > 0)
        .group_by("bucket")
    )
    budget_dist = [{"range": r[0], "lead_count": r[1]} for r in budget_query.all()]

    return {
        "top_locations": top_locations,
        "top_property_types": top_types,
        "budget_distribution": budget_dist,
    }


@router.get("/ai-decisions", summary="AI Decision Audit Trail")
async def get_ai_decisions(
    decision_type: Optional[str] = Query(None, description="Filter by type (LEAD_CLASSIFICATION, PROPERTY_MATCHING, INTENT_DETECTION)"),
    lead_id: Optional[uuid.UUID] = Query(None),
    limit: int = Query(25, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
) -> List[Dict[str, Any]]:
    """Returns the audit trail of autonomous AI decisions for transparency and oversight."""
    stmt = select(AIDecision).order_by(AIDecision.created_at.desc()).limit(limit)

    if decision_type:
        stmt = stmt.where(AIDecision.decision_type == decision_type)
    if lead_id:
        stmt = stmt.where(AIDecision.lead_id == lead_id)

    result = await session.execute(stmt)
    decisions = result.scalars().all()

    return [
        {
            "id": str(d.id),
            "decision_type": d.decision_type,
            "input_summary": d.input_context_summary[:200],
            "output": d.output_decision,
            "reasoning": d.reasoning_summary,
            "lead_id": str(d.lead_id) if d.lead_id else None,
            "conversation_id": str(d.conversation_id) if d.conversation_id else None,
            "created_at": d.created_at.isoformat(),
        }
        for d in decisions
    ]


@router.get("/customer-insights", summary="Aggregated Customer Intelligence & Objections")
async def get_customer_insights(
    days: int = Query(30, ge=1, le=365),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """
    Produces aggregated customer intelligence mined from WhatsApp inquiries and AI decision logs:
    - Common question categories (Pricing, Amenities, Possession, Loans)
    - Frequent customer objections (Price, Distance, Timeline)
    - Property demand and location preference distribution
    - Site visit conversion interest
    NOTE: This data reflects conversational CRM demand, distinct from live Meta Marketing API ad telemetry.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    # 1. Topic & question analysis across inbound messages
    msg_stmt = select(Message.content).where(
        Message.direction == "INBOUND",
        Message.created_at >= cutoff,
    ).limit(500)
    msg_res = await session.execute(msg_stmt)
    inbound_texts = [r[0].lower() for r in msg_res.all()]

    topic_counts = {
        "pricing_and_payment_plans": 0,
        "location_and_connectivity": 0,
        "floor_plans_and_brochure": 0,
        "possession_and_rera": 0,
        "home_loans_and_financing": 0,
        "site_visit_coordination": 0,
    }

    objection_counts = {
        "budget_exceeded": 0,
        "location_too_far": 0,
        "delayed_possession": 0,
        "compact_room_sizes": 0,
        "seeking_human_agent": 0,
    }

    for text_val in inbound_texts:
        if any(w in text_val for w in ("price", "cost", "budget", "cr", "lakh", "quote", "rate")):
            topic_counts["pricing_and_payment_plans"] += 1
        if any(w in text_val for w in ("location", "where", "near", "road", "metro", "distance")):
            topic_counts["location_and_connectivity"] += 1
        if any(w in text_val for w in ("floor", "plan", "brochure", "sqft", "layout", "photo", "image")):
            topic_counts["floor_plans_and_brochure"] += 1
        if any(w in text_val for w in ("possession", "rera", "ready", "under construction", "handover")):
            topic_counts["possession_and_rera"] += 1
        if any(w in text_val for w in ("loan", "emi", "bank", "interest", "finance", "mortgage")):
            topic_counts["home_loans_and_financing"] += 1
        if any(w in text_val for w in ("visit", "view", "see", "tomorrow", "saturday", "sunday", "tour")):
            topic_counts["site_visit_coordination"] += 1

        # Objections
        if any(w in text_val for w in ("expensive", "costly", "high price", "over budget", "too high")):
            objection_counts["budget_exceeded"] += 1
        if any(w in text_val for w in ("far", "traffic", "remote", "outer")):
            objection_counts["location_too_far"] += 1
        if any(w in text_val for w in ("too late", "delay", "long wait")):
            objection_counts["delayed_possession"] += 1
        if any(w in text_val for w in ("small", "compact", "carpet")):
            objection_counts["compact_room_sizes"] += 1
        if any(w in text_val for w in ("agent", "human", "call me", "talk to")):
            objection_counts["seeking_human_agent"] += 1

    # 2. Site visit interest summary
    total_visits = await session.execute(
        select(func.count(SiteVisit.id)).where(SiteVisit.created_at >= cutoff)
    )
    confirmed_visits = await session.execute(
        select(func.count(SiteVisit.id)).where(
            SiteVisit.created_at >= cutoff,
            SiteVisit.status == SiteVisitStatus.CONFIRMED.value,
        )
    )

    t_v = total_visits.scalar() or 0
    c_v = confirmed_visits.scalar() or 0

    return {
        "period_days": days,
        "inbound_messages_analyzed": len(inbound_texts),
        "frequent_inquiry_topics": [
            {"topic": k, "mention_count": v}
            for k, v in sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
        ],
        "top_customer_objections": [
            {"objection": k, "count": v}
            for k, v in sorted(objection_counts.items(), key=lambda x: x[1], reverse=True)
        ],
        "site_visit_interest": {
            "total_visits_requested": t_v,
            "confirmed_visits": c_v,
            "confirmation_rate": round(c_v / t_v * 100, 1) if t_v else 0,
        },
        "meta_advertising_data_status": {
            "integrated": False,
            "reason": "Meta Marketing API access token not provisioned; metrics represent customer CRM demand, not paid ad telemetry.",
        },
    }
