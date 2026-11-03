"use client";

import React, { useEffect, useState } from "react";
import {
  Building2,
  Users,
  Flame,
  CalendarCheck,
  MessageSquare,
  Sparkles,
  TrendingUp,
  AlertCircle,
  RefreshCw,
  Send,
  CheckCircle2,
  Phone,
  MapPin,
  IndianRupee,
  ShieldCheck,
  FileText,
} from "lucide-react";
import {
  api,
  DashboardOverview,
  CustomerInsights,
  LeadItem,
  PropertyItem,
  AIDecisionItem,
} from "@/lib/api";

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState<"pipeline" | "inventory" | "intelligence" | "audit">("pipeline");
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [leads, setLeads] = useState<LeadItem[]>([]);
  const [properties, setProperties] = useState<PropertyItem[]>([]);
  const [insights, setInsights] = useState<CustomerInsights | null>(null);
  const [decisions, setDecisions] = useState<AIDecisionItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [actionLoading, setActionLoading] = useState<boolean>(false);
  const [notification, setNotification] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const [ovData, leadsData, propsData, insightsData, decisionsData] = await Promise.allSettled([
        api.getOverview(),
        api.getLeads(),
        api.getProperties(),
        api.getCustomerInsights(),
        api.getAIDecisions(),
      ]);

      if (ovData.status === "fulfilled") setOverview(ovData.value);
      if (leadsData.status === "fulfilled") setLeads(leadsData.value.items || []);
      if (propsData.status === "fulfilled") setProperties(propsData.value.items || []);
      if (insightsData.status === "fulfilled") setInsights(insightsData.value);
      if (decisionsData.status === "fulfilled") setDecisions(decisionsData.value || []);
    } catch (err) {
      console.error("Dashboard data load error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleTriggerFollowUps = async () => {
    setActionLoading(true);
    try {
      const res = await api.triggerFollowUps();
      setNotification(`✅ Dispatched ${res.executed_count} automated follow-up messages!`);
      setTimeout(() => setNotification(null), 4000);
      await loadData();
    } catch (err: any) {
      setNotification(`❌ Failed to execute follow-ups: ${err.message}`);
      setTimeout(() => setNotification(null), 4000);
    } finally {
      setActionLoading(false);
    }
  };

  const formatPrice = (amount?: number | null) => {
    if (!amount) return "Undisclosed";
    if (amount >= 10000000) {
      return `₹${(amount / 10000000).toFixed(2)} Cr`;
    }
    if (amount >= 100000) {
      return `₹${(amount / 100000).toFixed(1)} Lakhs`;
    }
    return `₹${amount.toLocaleString()}`;
  };

  const hotLeads = leads.filter((l) => l.lead_category === "HOT");
  const warmLeads = leads.filter((l) => l.lead_category === "WARM");
  const coldLeads = leads.filter((l) => l.lead_category === "COLD");

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 flex flex-col">
      {/* Top Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="bg-emerald-600 text-white p-2.5 rounded-xl shadow-md flex items-center justify-center">
              <Building2 className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight text-slate-900">
                Prestige Realty AI
              </h1>
              <p className="text-xs text-slate-500 font-medium">
                Autonomous Sales & Marketing Automation Platform
              </p>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="flex items-center gap-3">
            <span className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              Live WhatsApp Connected
            </span>

            <span className="hidden md:inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
              <span className="w-2 h-2 rounded-full bg-blue-500"></span>
              Supabase Connected
            </span>

            <button
              onClick={handleTriggerFollowUps}
              disabled={actionLoading}
              className="inline-flex items-center gap-2 px-3.5 py-2 text-xs font-semibold rounded-lg bg-emerald-600 text-white hover:bg-emerald-700 active:scale-95 transition-all shadow-sm disabled:opacity-50"
            >
              <Send className="w-3.5 h-3.5" />
              {actionLoading ? "Dispatching..." : "Trigger Due Follow-Ups"}
            </button>

            <button
              onClick={loadData}
              disabled={loading}
              className="p-2 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition-all"
              title="Refresh Dashboard"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
            </button>
          </div>
        </div>

        {/* Global Notification Banner */}
        {notification && (
          <div className="bg-slate-900 text-white px-4 py-2 text-center text-xs font-semibold animate-in fade-in">
            {notification}
          </div>
        )}

        {/* Navigation Tabs */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex space-x-6 border-t border-slate-100">
          {[
            { id: "pipeline", label: "Lead Pipeline", icon: Users },
            { id: "inventory", label: "Properties Inventory", icon: Building2 },
            { id: "intelligence", label: "Marketing Intelligence", icon: TrendingUp },
            { id: "audit", label: "AI Decisions Audit", icon: ShieldCheck },
          ].map((tab) => {
            const Icon = tab.icon;
            const active = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 py-3 text-sm font-semibold border-b-2 transition-all ${
                  active
                    ? "border-emerald-600 text-emerald-600"
                    : "border-transparent text-slate-500 hover:text-slate-800 hover:border-slate-300"
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            );
          })}
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* KPI Summary Cards */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
          <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm">
            <div className="flex items-center justify-between text-slate-500 text-xs font-medium mb-1">
              <span>Total Leads</span>
              <Users className="w-4 h-4 text-blue-500" />
            </div>
            <div className="text-2xl font-bold text-slate-900">
              {overview?.total_leads ?? "—"}
            </div>
            <div className="text-[11px] text-slate-400 mt-1">From WhatsApp & Ads</div>
          </div>

          <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm">
            <div className="flex items-center justify-between text-slate-500 text-xs font-medium mb-1">
              <span>HOT Leads</span>
              <Flame className="w-4 h-4 text-red-500" />
            </div>
            <div className="text-2xl font-bold text-red-600">
              {overview?.leads_by_category?.HOT ?? 0}
            </div>
            <div className="text-[11px] text-slate-400 mt-1">Score ≥ 75 pts</div>
          </div>

          <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm">
            <div className="flex items-center justify-between text-slate-500 text-xs font-medium mb-1">
              <span>WARM Leads</span>
              <Sparkles className="w-4 h-4 text-amber-500" />
            </div>
            <div className="text-2xl font-bold text-amber-600">
              {overview?.leads_by_category?.WARM ?? 0}
            </div>
            <div className="text-[11px] text-slate-400 mt-1">Score 45–74 pts</div>
          </div>

          <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm">
            <div className="flex items-center justify-between text-slate-500 text-xs font-medium mb-1">
              <span>Active Chats</span>
              <MessageSquare className="w-4 h-4 text-emerald-500" />
            </div>
            <div className="text-2xl font-bold text-emerald-600">
              {overview?.active_conversations ?? "—"}
            </div>
            <div className="text-[11px] text-slate-400 mt-1">Conversing with AI</div>
          </div>

          <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm">
            <div className="flex items-center justify-between text-slate-500 text-xs font-medium mb-1">
              <span>Site Visits</span>
              <CalendarCheck className="w-4 h-4 text-indigo-500" />
            </div>
            <div className="text-2xl font-bold text-indigo-600">
              {overview?.upcoming_site_visits ?? "—"}
            </div>
            <div className="text-[11px] text-slate-400 mt-1">Upcoming appointments</div>
          </div>

          <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm">
            <div className="flex items-center justify-between text-slate-500 text-xs font-medium mb-1">
              <span>Available Units</span>
              <Building2 className="w-4 h-4 text-purple-500" />
            </div>
            <div className="text-2xl font-bold text-purple-600">
              {overview?.available_properties ?? "—"}
            </div>
            <div className="text-[11px] text-slate-400 mt-1">Verified catalog</div>
          </div>
        </div>

        {/* TAB 1: Lead Pipeline Kanban */}
        {activeTab === "pipeline" && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <Users className="w-4 h-4 text-emerald-600" />
                Qualification Pipeline Kanban
              </h2>
              <span className="text-xs text-slate-500">
                Categorized deterministically via 100-point algorithmic scoring
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* HOT COLUMN */}
              <div className="bg-slate-100/70 p-4 rounded-2xl border border-slate-200">
                <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-200">
                  <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-full bg-red-500"></span>
                    <h3 className="font-bold text-sm text-slate-800">HOT Leads</h3>
                  </div>
                  <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-red-100 text-red-700">
                    {hotLeads.length}
                  </span>
                </div>

                <div className="space-y-3 max-h-[600px] overflow-y-auto pr-1">
                  {hotLeads.length === 0 ? (
                    <div className="p-8 text-center text-xs text-slate-400 bg-white/60 rounded-xl">
                      No HOT leads currently.
                    </div>
                  ) : (
                    hotLeads.map((lead) => <LeadCard key={lead.id} lead={lead} formatPrice={formatPrice} />)
                  )}
                </div>
              </div>

              {/* WARM COLUMN */}
              <div className="bg-slate-100/70 p-4 rounded-2xl border border-slate-200">
                <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-200">
                  <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-full bg-amber-500"></span>
                    <h3 className="font-bold text-sm text-slate-800">WARM Leads</h3>
                  </div>
                  <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-700">
                    {warmLeads.length}
                  </span>
                </div>

                <div className="space-y-3 max-h-[600px] overflow-y-auto pr-1">
                  {warmLeads.length === 0 ? (
                    <div className="p-8 text-center text-xs text-slate-400 bg-white/60 rounded-xl">
                      No WARM leads currently.
                    </div>
                  ) : (
                    warmLeads.map((lead) => <LeadCard key={lead.id} lead={lead} formatPrice={formatPrice} />)
                  )}
                </div>
              </div>

              {/* COLD COLUMN */}
              <div className="bg-slate-100/70 p-4 rounded-2xl border border-slate-200">
                <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-200">
                  <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-full bg-slate-400"></span>
                    <h3 className="font-bold text-sm text-slate-800">COLD Leads</h3>
                  </div>
                  <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-slate-200 text-slate-700">
                    {coldLeads.length}
                  </span>
                </div>

                <div className="space-y-3 max-h-[600px] overflow-y-auto pr-1">
                  {coldLeads.length === 0 ? (
                    <div className="p-8 text-center text-xs text-slate-400 bg-white/60 rounded-xl">
                      No COLD leads currently.
                    </div>
                  ) : (
                    coldLeads.map((lead) => <LeadCard key={lead.id} lead={lead} formatPrice={formatPrice} />)
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: Property Inventory */}
        {activeTab === "inventory" && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-base font-bold text-slate-900">
                Verified Property Catalog ({properties.length} listings)
              </h2>
              <span className="text-xs text-slate-500">
                Authoritative inventory used by AI agent for matching (zero hallucination)
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {properties.map((prop) => (
                <div
                  key={prop.id}
                  className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm hover:shadow-md transition-all flex flex-col"
                >
                  <div className="h-44 bg-slate-100 relative overflow-hidden">
                    {prop.images && prop.images[0] ? (
                      <img
                        src={prop.images[0]}
                        alt={prop.name}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-slate-400">
                        <Building2 className="w-10 h-10 opacity-40" />
                      </div>
                    )}
                    <span className="absolute top-3 left-3 px-2.5 py-1 rounded-full text-xs font-bold bg-slate-900/80 text-white backdrop-blur-sm">
                      {prop.property_type}
                    </span>
                    <span className="absolute top-3 right-3 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500 text-white shadow">
                      {prop.status}
                    </span>
                  </div>

                  <div className="p-5 flex-1 flex flex-col justify-between">
                    <div>
                      <h3 className="font-bold text-slate-900 text-base mb-1">{prop.name}</h3>
                      <p className="text-xs text-slate-500 flex items-center gap-1 mb-3">
                        <MapPin className="w-3.5 h-3.5 text-slate-400" />
                        {prop.location}
                      </p>

                      <div className="grid grid-cols-3 gap-2 py-2.5 my-2 border-y border-slate-100 text-xs">
                        <div>
                          <span className="text-slate-400 block text-[10px]">Bedrooms</span>
                          <span className="font-bold text-slate-700">{prop.bedrooms} BHK</span>
                        </div>
                        <div>
                          <span className="text-slate-400 block text-[10px]">Bathrooms</span>
                          <span className="font-bold text-slate-700">{prop.bathrooms}</span>
                        </div>
                        <div>
                          <span className="text-slate-400 block text-[10px]">Area</span>
                          <span className="font-bold text-slate-700">{prop.area_sqft} sqft</span>
                        </div>
                      </div>

                      <div className="flex flex-wrap gap-1.5 my-2">
                        {prop.amenities?.slice(0, 3).map((amenity, i) => (
                          <span
                            key={i}
                            className="px-2 py-0.5 rounded-md text-[10px] font-medium bg-slate-100 text-slate-600"
                          >
                            {amenity}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                      <div className="text-xs">
                        <span className="text-slate-400 block text-[10px]">Price Bounds</span>
                        <span className="font-bold text-emerald-700">
                          {formatPrice(prop.price_min)} – {formatPrice(prop.price_max)}
                        </span>
                      </div>
                      <span className="text-[11px] text-slate-400">ID: {prop.id.slice(0, 8)}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB 3: Marketing Intelligence & Customer Insights */}
        {activeTab === "intelligence" && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
              <h2 className="text-base font-bold text-slate-900 mb-1 flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-emerald-600" />
                Conversational Demand & Inquiry Intelligence
              </h2>
              <p className="text-xs text-slate-500 mb-6">
                Aggregated in-platform customer inquiries and resistance patterns ({insights?.period_days ?? 30}-day lookback)
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Frequently Asked Inquiries */}
                <div>
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">
                    Top Inquired Topics
                  </h3>
                  <div className="space-y-2.5">
                    {insights?.frequent_inquiry_topics?.map((item) => (
                      <div key={item.topic} className="flex items-center justify-between text-xs p-2.5 rounded-lg bg-slate-50 border border-slate-100">
                        <span className="font-medium capitalize text-slate-700">
                          {item.topic.replace(/_/g, " ")}
                        </span>
                        <span className="font-bold bg-white px-2 py-0.5 rounded border border-slate-200 text-slate-800">
                          {item.mention_count} mentions
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Common Customer Objections */}
                <div>
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">
                    Frequent Customer Objections
                  </h3>
                  <div className="space-y-2.5">
                    {insights?.top_customer_objections?.map((item) => (
                      <div key={item.objection} className="flex items-center justify-between text-xs p-2.5 rounded-lg bg-red-50/50 border border-red-100">
                        <span className="font-medium capitalize text-slate-700">
                          {item.objection.replace(/_/g, " ")}
                        </span>
                        <span className="font-bold bg-white px-2 py-0.5 rounded border border-red-200 text-red-700">
                          {item.count} occurrences
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Conversion Metric Card */}
              <div className="mt-8 pt-6 border-t border-slate-100 grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 text-center">
                  <span className="text-xs text-slate-400 block mb-1">Site Visits Requested</span>
                  <span className="text-2xl font-bold text-slate-800">
                    {insights?.site_visit_interest?.total_visits_requested ?? 0}
                  </span>
                </div>
                <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 text-center">
                  <span className="text-xs text-slate-400 block mb-1">Confirmed Site Visits</span>
                  <span className="text-2xl font-bold text-emerald-600">
                    {insights?.site_visit_interest?.confirmed_visits ?? 0}
                  </span>
                </div>
                <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 text-center">
                  <span className="text-xs text-slate-400 block mb-1">Confirmation Rate</span>
                  <span className="text-2xl font-bold text-indigo-600">
                    {insights?.site_visit_interest?.confirmation_rate ?? 0}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 4: AI Decision Audit Trail */}
        {activeTab === "audit" && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-emerald-600" />
                Explainable AI Decisions Stream
              </h2>
              <span className="text-xs text-slate-500">
                Real-time audit log of OpenRouter extraction, intent routing, and scoring decisions
              </span>
            </div>

            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
              <div className="divide-y divide-slate-100">
                {decisions.length === 0 ? (
                  <div className="p-12 text-center text-xs text-slate-400">
                    No AI decision records logged yet.
                  </div>
                ) : (
                  decisions.map((d) => (
                    <div key={d.id} className="p-4 hover:bg-slate-50 transition-colors">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <span className="px-2.5 py-0.5 rounded text-[11px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-200">
                            {d.decision_type}
                          </span>
                          <span className="text-xs font-semibold text-slate-800">
                            ID: {d.id.slice(0, 8)}
                          </span>
                        </div>
                        <span className="text-[11px] text-slate-400">
                          {new Date(d.created_at).toLocaleString()}
                        </span>
                      </div>

                      <div className="text-xs text-slate-600 mb-2">
                        <span className="font-semibold text-slate-800">Trigger:</span>{" "}
                        {d.input_summary}
                      </div>

                      <div className="text-xs bg-slate-50 p-2.5 rounded-lg border border-slate-100 mb-2 text-slate-700">
                        <span className="font-semibold text-slate-800 block mb-0.5">
                          Reasoning Summary:
                        </span>
                        {d.reasoning}
                      </div>

                      <div className="text-[11px] text-slate-400">
                        {d.lead_id && (
                          <span className="mr-3">Lead: {d.lead_id.slice(0, 8)}</span>
                        )}
                        {d.conversation_id && (
                          <span>Convo: {d.conversation_id.slice(0, 8)}</span>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

function LeadCard({
  lead,
  formatPrice,
}: {
  lead: LeadItem;
  formatPrice: (amt?: number | null) => string;
}) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm hover:shadow transition-all text-xs">
      <div className="flex items-start justify-between gap-2 mb-2">
        <div>
          <h4 className="font-bold text-slate-900 text-sm">{lead.name || "Anonymous Prospect"}</h4>
          <span className="text-slate-400 text-[11px] flex items-center gap-1">
            <Phone className="w-3 h-3" />
            {lead.phone}
          </span>
        </div>
        <span
          className={`px-2 py-0.5 rounded-md font-bold text-xs ${
            lead.lead_category === "HOT"
              ? "bg-red-50 text-red-700 border border-red-200"
              : lead.lead_category === "WARM"
              ? "bg-amber-50 text-amber-700 border border-amber-200"
              : "bg-slate-100 text-slate-600"
          }`}
        >
          {lead.lead_score} pts
        </span>
      </div>

      <div className="space-y-1 text-slate-600 my-2 pt-2 border-t border-slate-100 text-[11px]">
        {lead.preferred_location && (
          <div className="flex items-center gap-1.5">
            <MapPin className="w-3 h-3 text-slate-400" />
            <span>{lead.preferred_location}</span>
          </div>
        )}
        {lead.property_type && (
          <div className="flex items-center gap-1.5">
            <Building2 className="w-3 h-3 text-slate-400" />
            <span>
              {lead.bedroom_preference ? `${lead.bedroom_preference} BHK ` : ""}
              {lead.property_type}
            </span>
          </div>
        )}
        {(lead.budget_max || lead.budget_min) && (
          <div className="flex items-center gap-1.5">
            <IndianRupee className="w-3 h-3 text-slate-400" />
            <span>Budget: Up to {formatPrice(lead.budget_max || lead.budget_min)}</span>
          </div>
        )}
      </div>

      {lead.qualification_reasons && lead.qualification_reasons.length > 0 && (
        <div className="mt-2 pt-2 border-t border-slate-100">
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-[10px] text-emerald-600 hover:text-emerald-700 font-semibold flex items-center gap-1"
          >
            {expanded ? "Hide Scoring Breakdown ▲" : "View Scoring Breakdown ▼"}
          </button>
          {expanded && (
            <ul className="mt-1.5 space-y-1 text-[10px] text-slate-500 bg-slate-50 p-2 rounded border border-slate-100">
              {lead.qualification_reasons.map((r, idx) => (
                <li key={idx} className="flex items-center gap-1">
                  <CheckCircle2 className="w-2.5 h-2.5 text-emerald-600 flex-shrink-0" />
                  <span>{r}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
