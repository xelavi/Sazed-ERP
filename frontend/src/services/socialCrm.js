/**
 * Social CRM API service — connects the campaigns module to the Django
 * `social_crm` app (mounted at /api/social-crm/).
 *
 * The backend stores normalized data and DERIVES campaign totals
 * (reach, cost, sales, ROAS…) on demand via the `channel-breakdown` action.
 * The frontend components were originally written against the mock shape in
 * `socialCrmData.js`, so every map* helper below translates a backend payload
 * into that same shape, keeping the templates untouched.
 */
import { get, post, patch, del } from './api'

const BASE = '/social-crm'

// DRF list endpoints are paginated ({ count, results }); unwrap defensively.
const unwrap = (d) => (Array.isArray(d) ? d : d?.results || [])

// ── Objective: backend key ⇄ display label ────────────────────────────────────
// The frontend's CAMPAIGN_OBJECTIVES use the Catalan display labels, while the
// backend stores the lowercase key. Keep both directions in sync.
export const OBJECTIVE_LABEL_TO_KEY = {
  'Awareness':   'awareness',
  'Trànsit':     'traffic',
  'Conversions': 'conversions',
  'Engagement':  'engagement',
  'Vendes':      'sales',
  'Leads':       'leads',
}

// ── Targets: frontend object ⇄ backend array ─────────────────────────────────
const TARGET_KEYS = ['reach', 'clicks', 'conversions', 'sales']

export function targetsToArray(t) {
  const out = []
  for (const key of TARGET_KEYS) {
    const v = Number(t?.[key]) || 0
    if (v > 0) out.push({ metric_key: key, target_value: v })
  }
  return out
}

function targetsFromArray(arr) {
  const t = { reach: 0, clicks: 0, conversions: 0, sales: 0 }
  for (const x of arr || []) t[x.metric_key] = Number(x.target_value) || 0
  return t
}

// ── Mappers (backend → frontend mock shape) ──────────────────────────────────
export function mapCampaign(c) {
  return {
    id:          c.id,
    name:        c.name,
    objective:   c.objective_display || c.objective,
    status:      c.status, // keys match (draft/active/paused/completed)
    startDate:   c.start_date,
    endDate:     c.end_date,
    budget:      Number(c.total_budget) || 0,
    description: c.description || '',
    responsible: c.responsible_name || '',
    targets:     targetsFromArray(c.targets),
    timeline:    (c.timeline_events || []).map(e => ({
      date:  e.event_date,
      event: e.description,
      type:  e.event_type,
    })),
    // Derived metrics — filled in by enrichWithBreakdown(); safe defaults here.
    cost: 0, sales: 0, roas: 0, reach: 0, impressions: 0,
    clicks: 0, conversions: 0, posts: 0, influencers: 0,
    channels: [],
  }
}

/** Merge a /channel-breakdown/ response into a mapped campaign (in place). */
export function enrichWithBreakdown(campaign, bd) {
  const t = bd?.totals || {}
  const byCh = Object.fromEntries((bd?.channels || []).map(ch => [ch.channel, ch]))
  campaign.cost        = t.cost        || 0
  campaign.sales       = t.sales       || 0
  campaign.roas        = t.roas        || 0
  campaign.reach       = t.reach       || 0
  campaign.impressions = t.impressions || 0
  campaign.clicks      = t.clicks      || 0
  campaign.conversions = t.conversions || 0
  campaign.posts       = byCh.owned?.items       || 0
  campaign.influencers = byCh.influencers?.items || 0
  campaign.channels    = (bd?.channels || []).filter(ch => ch.items > 0).map(ch => ch.channel)
  return campaign
}

export function mapPost(p) {
  return {
    id:           p.id,
    title:        p.title,
    type:         p.content_type_display || p.content_type,
    platform:     p.platform,
    date:         p.published_at,
    campaignId:   p.campaign,
    campaignName: p.campaign_name,
    accountId:    p.account,
    accountName:  p.account_name,
    engagement:   Number(p.engagement_rate) || 0,
    reach:        p.reach || 0,
    impressions:  p.impressions || 0,
    clicks:       p.clicks || 0,
    likes:        p.likes || 0,
    comments:     p.comments || 0,
    shares:       p.shares || 0,
    saves:        p.saves || 0,
    views:        p.views || 0,
  }
}

export function mapInfluencer(i) {
  return {
    id:        i.id,
    name:      i.name,
    alias:     i.alias,
    platform:  i.primary_platform,
    followers: i.followers || 0,
    niche:     i.niche || '',
    status:    i.status,
  }
}

export function mapCollaboration(c) {
  return {
    id:              c.id,
    campaignId:      c.campaign,
    campaignName:    c.campaign_name,
    influencerId:    c.influencer,
    influencerName:  c.influencer_name,
    influencerAlias: c.influencer_alias,
    format:          c.content_format || '',
    publishDate:     c.publish_date,
    cost:            Number(c.agreed_cost) || 0,
    code:            c.discount_code || '',
    status:          c.status,
    reach:           c.actual_reach || 0,
    impressions:     c.actual_impressions || 0,
    views:           c.actual_views || 0,
    likes:           c.actual_likes || 0,
    comments:        c.actual_comments || 0,
    shares:          c.actual_shares || 0,
    // clicks/conversions/sales live on the linked TrackedLink, not here.
    clicks: 0, conversions: 0, sales: 0,
  }
}

export function mapAdSet(a) {
  return {
    id:          a.id,
    campaignId:  a.campaign,
    platform:    a.ad_platform,
    name:        a.name,
    status:      a.status,
    startDate:   a.start_date,
    endDate:     a.end_date,
    budget:      Number(a.budget_amount) || 0,
    spend:       Number(a.spend_amount) || 0,
    impressions: a.impressions || 0,
    clicks:      a.clicks || 0,
    conversions: a.conversions || 0,
    sales:       Number(a.sales_revenue) || 0,
  }
}

export function mapLink(l) {
  return {
    id:             l.id,
    name:           l.name,
    campaignId:     l.campaign,
    campaignName:   l.campaign_name,
    origin:         l.origin_platform,
    influencerId:   l.collaboration || null,
    influencerName: l.influencer_name,
    utmSource:      l.utm_source,
    utmMedium:      l.utm_medium,
    utmCampaign:    l.utm_campaign,
    utmContent:     l.utm_content,
    clicks:         l.clicks || 0,
    sessions:       l.sessions || 0,
    carts:          l.carts || 0,
    purchases:      l.purchases || 0,
    revenue:        Number(l.revenue) || 0,
    conversion:     Number(l.conversion_rate) || 0,
  }
}

// ── API calls ─────────────────────────────────────────────────────────────────
export default {
  // Campaigns
  async listCampaigns() {
    return unwrap(await get(`${BASE}/campaigns/`)).map(mapCampaign)
  },
  async getCampaign(id) {
    return mapCampaign(await get(`${BASE}/campaigns/${id}/`))
  },
  async channelBreakdown(id) {
    return get(`${BASE}/campaigns/${id}/channel-breakdown/`)
  },
  async createCampaign(payload) {
    return post(`${BASE}/campaigns/`, payload)
  },
  async deleteCampaign(id) {
    return del(`${BASE}/campaigns/${id}/`)
  },

  // Posts
  async listPosts(params = {}) {
    return unwrap(await get(`${BASE}/posts/`, params)).map(mapPost)
  },
  async linkPostToCampaign(postId, campaignId) {
    return patch(`${BASE}/posts/${postId}/`, { campaign: campaignId })
  },

  // Influencers
  async listInfluencers() {
    return unwrap(await get(`${BASE}/influencers/`)).map(mapInfluencer)
  },
  async createInfluencer(payload) {
    return post(`${BASE}/influencers/`, payload)
  },

  // Collaborations
  async listCollaborations(params = {}) {
    return unwrap(await get(`${BASE}/collaborations/`, params)).map(mapCollaboration)
  },
  async createCollaboration(payload) {
    return post(`${BASE}/collaborations/`, payload)
  },

  // Paid ad sets
  async listAdSets(params = {}) {
    return unwrap(await get(`${BASE}/ad-sets/`, params)).map(mapAdSet)
  },
  async createAdSet(payload) {
    return post(`${BASE}/ad-sets/`, payload)
  },

  // Tracked links
  async listLinks(params = {}) {
    return unwrap(await get(`${BASE}/links/`, params)).map(mapLink)
  },
}
