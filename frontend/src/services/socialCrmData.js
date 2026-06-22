// ── Social CRM Mock Data ──────────────────────────────────────────────────────
// All data is fabricated for development. No real API connections.

// ── Platform config ──────────────────────────────────────────────────────────
export const PLATFORMS = {
  instagram: { label: 'Instagram', color: '#E4405F', bg: '#fce4ec' },
  tiktok:    { label: 'TikTok',    color: '#000000', bg: '#f5f5f5' },
  twitter:   { label: 'Twitter/X', color: '#1DA1F2', bg: '#e3f2fd' },
  facebook:  { label: 'Facebook',  color: '#1877F2', bg: '#e8f0fe' },
  youtube:   { label: 'YouTube',   color: '#FF0000', bg: '#ffebee' },
  linkedin:  { label: 'LinkedIn',  color: '#0A66C2', bg: '#e3f2fd' },
}

export const CONTENT_TYPES = ['Imatge', 'Vídeo', 'Reel', 'Story', 'Carrusel', 'Tweet', 'Fil', 'Short']

export const CAMPAIGN_OBJECTIVES = ['Awareness', 'Trànsit', 'Conversions', 'Engagement', 'Vendes', 'Leads']

export const CAMPAIGN_STATUSES = {
  active:    { label: 'Activa',     cls: 'badge-active' },
  draft:     { label: 'Esborrany',  cls: 'badge-inactive' },
  paused:    { label: 'Pausada',    cls: 'badge-warning' },
  completed: { label: 'Completada', cls: 'badge-info' },
}

// ── Campaign channels (the 3 "methods" a campaign can use) ────────────────────
// `auto`  → metrics arrive automatically via platform APIs.
// `manual`→ metrics must be entered by hand (influencer collaborations).
export const CAMPAIGN_CHANNELS = {
  owned:       { key: 'owned',       label: 'Comptes propis',   short: 'Propi',       icon: 'Megaphone', color: '#667eea', source: 'auto'   },
  influencers: { key: 'influencers', label: 'Influencers',      short: 'Influencers', icon: 'Users',     color: '#EC4899', source: 'manual' },
  paid:        { key: 'paid',        label: 'Anuncis de pagament', short: 'Ads',      icon: 'Target',    color: '#F59E0B', source: 'auto'   },
}

// ── Paid-ad platforms ─────────────────────────────────────────────────────────
export const AD_PLATFORMS = {
  facebook:  { label: 'Meta Ads',      color: '#1877F2', bg: '#e8f0fe' },
  google:    { label: 'Google Ads',    color: '#4285F4', bg: '#e8f0fe' },
  tiktok:    { label: 'TikTok Ads',    color: '#111111', bg: '#f5f5f5' },
  instagram: { label: 'Instagram Ads', color: '#E4405F', bg: '#fce4ec' },
}

export const COLLAB_STATUSES = {
  draft:     { label: 'Esborrany',  cls: 'badge-inactive' },
  pending:   { label: 'Pendent',    cls: 'badge-warning' },
  active:    { label: 'Activa',     cls: 'badge-active' },
  completed: { label: 'Completada', cls: 'badge-info' },
  cancelled: { label: 'Cancel·lada', cls: 'badge-error' },
}

export const ALERT_TYPES = {
  reach_drop:       { label: 'Caiguda d\'abast',            icon: 'TrendingDown' },
  broken_link:      { label: 'Enllaç trencat',             icon: 'LinkOff' },
  low_campaign:     { label: 'Campanya amb baix rendiment', icon: 'Target' },
  negative_comments:{ label: 'Molts comentaris negatius',  icon: 'MessageCircleWarning' },
  missing_metrics:  { label: 'Mètriques pendents',         icon: 'ClipboardX' },
  high_cost:        { label: 'Cost alt sense conversió',   icon: 'DollarSign' },
  unvalidated_data: { label: 'Dada manual sense validar',  icon: 'AlertCircle' },
}

// ── Social Accounts ───────────────────────────────────────────────────────────
export const socialAccounts = [
  { id: 1, platform: 'instagram', name: 'Sazed',        username: '@sazed.es',  status: 'connected',    lastSync: '2026-04-17T09:30:00', followers: 48300, posts: 524,  responsible: 'Laura Martínez', observations: 'Compte principal de la marca' },
  { id: 4, platform: 'facebook',  name: 'Sazed',        username: 'Sazed',      status: 'connected',    lastSync: '2026-04-17T10:15:00', followers: 15200, posts: 340,  responsible: 'Carlos Ruiz',   observations: '' },
  { id: 5, platform: 'youtube',   name: 'Sazed',        username: '@Sazed',     status: 'connected',    lastSync: '2026-04-17T07:00:00', followers: 6700,  posts: 89,   responsible: 'Ana Torres',    observations: '' },
  { id: 2, platform: 'tiktok',    name: 'Sazed TikTok', username: '@sazed',     status: 'disconnected', lastSync: '2026-04-10T08:00:00', followers: 22100, posts: 188,  responsible: 'Laura Martínez', observations: 'Token caducat, renovar' },
  { id: 3, platform: 'twitter',   name: 'Sazed X',      username: '@sazed_es',  status: 'disconnected', lastSync: '2026-04-12T22:00:00', followers: 9800,  posts: 1204, responsible: 'Carlos Ruiz',   observations: '' },
]

// ── Social Posts ──────────────────────────────────────────────────────────────
export const socialPosts = [
  { id: 1,  date: '2026-04-15', platform: 'instagram', accountId: 1, accountName: '@marca.es',     title: 'Nova col·lecció Primavera 2026 🌸', type: 'Reel',    campaignId: 1, campaignName: 'Primavera 2026', productId: null, likes: 2840, comments: 134, shares: 312, saves: 780,  views: 28400, reach: 34200, impressions: 48000, clicks: 890, engagement: 7.2 },
  { id: 2,  date: '2026-04-14', platform: 'instagram', accountId: 1, accountName: '@marca.es',     title: 'Darrere de càmeres: making of',       type: 'Carrusel', campaignId: 1, campaignName: 'Primavera 2026', productId: null, likes: 1240, comments: 87,  shares: 145, saves: 320,  views: 0,     reach: 18400, impressions: 22000, clicks: 340, engagement: 4.8 },
  { id: 3,  date: '2026-04-13', platform: 'tiktok',    accountId: 2, accountName: '@marca_tiktok', title: 'Tendències outfit estiu 2026',       type: 'Vídeo',   campaignId: 1, campaignName: 'Primavera 2026', productId: 3,   likes: 8900, comments: 340, shares: 1200, saves: 2300, views: 142000, reach: 89000, impressions: 142000, clicks: 2100, engagement: 8.9 },
  { id: 4,  date: '2026-04-12', platform: 'instagram', accountId: 1, accountName: '@marca.es',     title: 'Descobreix els nostres nous colors',  type: 'Imatge',  campaignId: 1, campaignName: 'Primavera 2026', productId: 1,   likes: 980,  comments: 42,  shares: 89,  saves: 210,  views: 0,     reach: 12300, impressions: 15600, clicks: 230, engagement: 3.4 },
  { id: 5,  date: '2026-04-10', platform: 'twitter',   accountId: 3, accountName: '@marca_es',     title: 'Llancem la nova línia eco-friendly', type: 'Tweet',  campaignId: 2, campaignName: 'Eco Collection', productId: null, likes: 345,  comments: 67,  shares: 234, saves: 0,    views: 12400, reach: 9800,  impressions: 12400, clicks: 189, engagement: 3.1 },
  { id: 6,  date: '2026-04-09', platform: 'tiktok',    accountId: 2, accountName: '@marca_tiktok', title: 'Tutorial: com combinar peces',      type: 'Short',   campaignId: null, campaignName: null, productId: null, likes: 4500, comments: 212, shares: 890, saves: 1800, views: 67000, reach: 45000, impressions: 67000, clicks: 1200, engagement: 7.1 },
  { id: 7,  date: '2026-04-08', platform: 'instagram', accountId: 1, accountName: '@marca.es',     title: 'Lookbook Primavera disponible',        type: 'Carrusel', campaignId: 1, campaignName: 'Primavera 2026', productId: null, likes: 1680, comments: 98,  shares: 234, saves: 490, views: 0,     reach: 21000, impressions: 26800, clicks: 480, engagement: 5.7 },
  { id: 8,  date: '2026-04-06', platform: 'youtube',   accountId: 5, accountName: 'Marca Oficial', title: 'Unboxing: Colección Primavera 2026',   type: 'Vídeo',   campaignId: 1, campaignName: 'Primavera 2026', productId: null, likes: 892,  comments: 145, shares: 67,  saves: 0,    views: 18900, reach: 14200, impressions: 18900, clicks: 340, engagement: 5.3 },
  { id: 9,  date: '2026-04-04', platform: 'instagram', accountId: 1, accountName: '@marca.es',     title: 'Story exclusiva: primeras unidades',  type: 'Story',   campaignId: null, campaignName: null, productId: 2, likes: 0,    comments: 0,   shares: 0,   saves: 0,    views: 8900,  reach: 8900,  impressions: 8900, clicks: 145, engagement: 1.6 },
  { id: 10, date: '2026-04-02', platform: 'linkedin',  accountId: 6, accountName: 'Marca S.L.',    title: 'Creixem: noves incorporacions',         type: 'Imatge',  campaignId: null, campaignName: null, productId: null, likes: 234,  comments: 45,  shares: 78,  saves: 0,    views: 0,     reach: 3400,  impressions: 4200, clicks: 89, engagement: 6.7 },
  // Campaign 6 · Rebaixes Estiu 2026
  { id: 11, date: '2026-06-01', platform: 'instagram', accountId: 1, accountName: '@marca.es',     title: 'Rebaixes Estiu 2026 🌊 Fins al 40% en moda d\'estiu', type: 'Reel',    campaignId: 6, campaignName: 'Rebaixes Estiu 2026', productId: 7,   likes: 3200, comments: 184, shares: 420, saves: 890,  views: 38000, reach: 38000, impressions: 52000, clicks: 1240, engagement: 6.8 },
  { id: 12, date: '2026-06-02', platform: 'tiktok',    accountId: 2, accountName: '@marca_tiktok', title: 'Haul de rebaixes d\'estiu — fins al 40% off 🛍️',     type: 'Vídeo',   campaignId: 6, campaignName: 'Rebaixes Estiu 2026', productId: null, likes: 7200, comments: 312, shares: 1800, saves: 2400, views: 94000, reach: 58000, impressions: 94000, clicks: 2800, engagement: 9.4 },
  { id: 13, date: '2026-06-03', platform: 'instagram', accountId: 1, accountName: '@marca.es',     title: '10 peces estrella de les rebaixes d\'estiu ☀️',       type: 'Carrusel', campaignId: 6, campaignName: 'Rebaixes Estiu 2026', productId: null, likes: 1840, comments: 96,  shares: 280, saves: 520,  views: 0,     reach: 24000, impressions: 31000, clicks: 680, engagement: 5.1 },
  { id: 14, date: '2026-06-04', platform: 'instagram', accountId: 1, accountName: '@marca.es',     title: '48h d\'ofertes exclusives per a seguidors 🔥',        type: 'Story',   campaignId: 6, campaignName: 'Rebaixes Estiu 2026', productId: 10,  likes: 0,    comments: 0,   shares: 0,   saves: 0,    views: 14000, reach: 14000, impressions: 14000, clicks: 540, engagement: 3.9 },
  { id: 15, date: '2026-06-05', platform: 'youtube',   accountId: 5, accountName: 'Marca Oficial', title: 'REBAIXES ESTIU 2026 | Haul complet amb preus reals',  type: 'Vídeo',   campaignId: 6, campaignName: 'Rebaixes Estiu 2026', productId: null, likes: 720,  comments: 98,  shares: 45,  saves: 0,    views: 9200,  reach: 9200,  impressions: 9200,  clicks: 380, engagement: 5.3 },
  { id: 16, date: '2026-06-07', platform: 'twitter',   accountId: 3, accountName: '@marca_es',     title: '🌊 Rebaixes d\'estiu de fins al 40%! Entra ara 👉',   type: 'Tweet',   campaignId: 6, campaignName: 'Rebaixes Estiu 2026', productId: null, likes: 187,  comments: 23,  shares: 134, saves: 0,    views: 8400,  reach: 6100,  impressions: 8400,  clicks: 245, engagement: 3.7 },
  { id: 17, date: '2026-06-09', platform: 'instagram', accountId: 1, accountName: '@marca.es',     title: 'Nous vestits d\'estiu afegits a les rebaixes 👙',      type: 'Reel',    campaignId: 6, campaignName: 'Rebaixes Estiu 2026', productId: 14,  likes: 1920, comments: 108, shares: 340, saves: 620,  views: 22000, reach: 22000, impressions: 28000, clicks: 680, engagement: 6.5 },
]

// ── Campaigns ─────────────────────────────────────────────────────────────────
export const socialCampaigns = [
  {
    id: 1, name: 'Primavera 2026', objective: 'Conversions', startDate: '2026-03-21', endDate: '2026-05-21',
    status: 'active', budget: 5000, posts: 12, influencers: 3,
    clicks: 8900, conversions: 312, sales: 14200,
    description: 'Campanya de llançament de la col·lecció Primavera-Estiu 2026. Objectiu: augmentar les vendes un 30% respecte a l\'any anterior.',
    responsible: 'Laura Martínez',
    reach: 145000, impressions: 210000, engagement: 5.8, cost: 4200, roas: 3.38,
    channels: ['owned', 'influencers', 'paid'],
    budgetByChannel: { owned: 500, influencers: 2500, paid: 2000 },
    targets: { reach: 160000, clicks: 9000, conversions: 350, sales: 16000 },
    timeline: [
      { date: '2026-03-21', event: 'Inici de la campanya', type: 'milestone' },
      { date: '2026-04-01', event: 'Publicacions dels influencers Ana García i Pablo Vidal', type: 'post' },
      { date: '2026-04-15', event: 'Reel viral 28K d\'abast', type: 'milestone' },
      { date: '2026-04-17', event: 'Revisió intermèdia de KPI', type: 'review' },
    ]
  },
  {
    id: 2, name: 'Eco Collection', objective: 'Awareness', startDate: '2026-04-01', endDate: '2026-04-30',
    status: 'active', budget: 2000, posts: 8, influencers: 2,
    clicks: 3400, conversions: 89, sales: 3200,
    description: 'Campanya per donar a conèixer la nova línia de productes eco-friendly.',
    responsible: 'Carlos Ruiz',
    reach: 67000, impressions: 98000, engagement: 4.2, cost: 1600, roas: 2.0,
    channels: ['owned', 'influencers', 'paid'],
    budgetByChannel: { owned: 200, influencers: 900, paid: 900 },
    targets: { reach: 80000, clicks: 4000, conversions: 120, sales: 4000 },
    timeline: [
      { date: '2026-04-01', event: 'Inici de la campanya', type: 'milestone' },
      { date: '2026-04-10', event: 'Post viral a Twitter', type: 'milestone' },
    ]
  },
  {
    id: 3, name: 'Vuelta al Cole 2025', objective: 'Vendes', startDate: '2025-08-15', endDate: '2025-09-30',
    status: 'completed', budget: 3500, posts: 18, influencers: 4,
    clicks: 12400, conversions: 480, sales: 22000,
    description: 'Campanya de back-to-school amb descomptes i col·laboracions amb influencers educatius.',
    responsible: 'Laura Martínez',
    reach: 189000, impressions: 267000, engagement: 6.1, cost: 3480, roas: 6.32,
    channels: ['owned', 'influencers', 'paid'],
    budgetByChannel: { owned: 300, influencers: 1200, paid: 2000 },
    targets: { reach: 180000, clicks: 12000, conversions: 450, sales: 20000 },
    timeline: []
  },
  {
    id: 4, name: 'Black Friday 2025', objective: 'Vendes', startDate: '2025-11-20', endDate: '2025-11-30',
    status: 'completed', budget: 6000, posts: 24, influencers: 6,
    clicks: 28900, conversions: 1240, sales: 58000,
    description: 'Campanya Black Friday amb descomptes de fins al 50%.',
    responsible: 'Laura Martínez',
    reach: 380000, impressions: 520000, engagement: 7.8, cost: 5800, roas: 10.0,
    channels: ['owned', 'influencers', 'paid'],
    budgetByChannel: { owned: 400, influencers: 1600, paid: 4000 },
    targets: { reach: 350000, clicks: 25000, conversions: 1100, sales: 50000 },
    timeline: []
  },
  {
    id: 5, name: 'Navidad 2025', objective: 'Conversions', startDate: '2025-12-01', endDate: '2025-12-31',
    status: 'completed', budget: 4500, posts: 20, influencers: 5,
    clicks: 18600, conversions: 720, sales: 34000,
    description: 'Campanya nadalenca amb guia de regals i col·laboracions especials.',
    responsible: 'Ana Torres',
    reach: 260000, impressions: 380000, engagement: 6.9, cost: 4320, roas: 7.87,
    channels: ['owned', 'influencers', 'paid'],
    budgetByChannel: { owned: 300, influencers: 1700, paid: 2500 },
    targets: { reach: 250000, clicks: 17000, conversions: 700, sales: 32000 },
    timeline: []
  },
  {
    id: 6, name: 'Rebaixes Estiu 2026', objective: 'Vendes', startDate: '2026-06-01', endDate: '2026-07-31',
    status: 'active', budget: 8500, posts: 7, influencers: 4,
    clicks: 8400, conversions: 267, sales: 18200,
    description: 'Campanya de rebaixes d\'estiu amb descomptes de fins al 40%. Objectiu: maximitzar les vendes de la temporada estival coordinant comptes propis, influencers i anuncis de pagament.',
    responsible: 'Laura Martínez',
    reach: 142000, impressions: 218000, engagement: 5.9, cost: 3420, roas: 5.32,
    channels: ['owned', 'influencers', 'paid'],
    budgetByChannel: { owned: 500, influencers: 3800, paid: 4200 },
    targets: { reach: 400000, clicks: 28000, conversions: 1000, sales: 45000 },
    timeline: [
      { date: '2026-06-01', event: 'Llançament de la campanya de rebaixes d\'estiu', type: 'milestone' },
      { date: '2026-06-02', event: 'Vídeo de TikTok viral: 58K d\'abast en 12h', type: 'milestone' },
      { date: '2026-06-05', event: 'Marta Domínguez publica el primer TikTok de la campanya', type: 'post' },
      { date: '2026-06-07', event: 'Ana García publica el Reel d\'estiu — 54K d\'abast', type: 'post' },
      { date: '2026-06-09', event: 'Revisió setmanal de KPI: ROAS 5.32x ✓', type: 'review' },
    ]
  },
]

// ── Paid Ads (ad sets per platform, linked to a campaign) ─────────────────────
// Metrics arrive automatically from the ad platform API (source: 'auto').
export const socialAds = [
  // Campaign 1 · Primavera 2026
  { id: 1, campaignId: 1, platform: 'facebook', name: 'Primavera · Retargeting carrito',  status: 'active',    startDate: '2026-03-22', endDate: '2026-05-21', budget: 1200, spend: 1180, impressions: 84000,  clicks: 3100, conversions: 96,  sales: 4300 },
  { id: 2, campaignId: 1, platform: 'google',   name: 'Primavera · Search marca',         status: 'active',    startDate: '2026-03-21', endDate: '2026-05-21', budget: 800,  spend: 760,  impressions: 52000,  clicks: 2400, conversions: 71,  sales: 3100 },
  { id: 3, campaignId: 1, platform: 'tiktok',   name: 'Primavera · Spark Ads',            status: 'active',    startDate: '2026-04-01', endDate: '2026-05-10', budget: 600,  spend: 540,  impressions: 61000,  clicks: 1900, conversions: 54,  sales: 2400 },
  // Campaign 2 · Eco Collection
  { id: 4, campaignId: 2, platform: 'facebook', name: 'Eco · Awareness vídeo',            status: 'active',    startDate: '2026-04-02', endDate: '2026-04-30', budget: 700,  spend: 620,  impressions: 38000,  clicks: 1400, conversions: 38,  sales: 1500 },
  // Campaign 3 · Vuelta al Cole 2025
  { id: 5, campaignId: 3, platform: 'google',   name: 'Vuelta cole · Shopping',           status: 'completed', startDate: '2025-08-15', endDate: '2025-09-30', budget: 1100, spend: 1100, impressions: 96000,  clicks: 4200, conversions: 180, sales: 8200 },
  { id: 6, campaignId: 3, platform: 'facebook', name: 'Vuelta cole · Catálogo',           status: 'completed', startDate: '2025-08-15', endDate: '2025-09-30', budget: 900,  spend: 880,  impressions: 72000,  clicks: 3100, conversions: 130, sales: 6000 },
  // Campaign 4 · Black Friday 2025
  { id: 7, campaignId: 4, platform: 'facebook', name: 'BF · Descuentos dinámicos',        status: 'completed', startDate: '2025-11-20', endDate: '2025-11-30', budget: 2200, spend: 2200, impressions: 210000, clicks: 9800, conversions: 480, sales: 22000 },
  { id: 8, campaignId: 4, platform: 'google',   name: 'BF · Performance Max',             status: 'completed', startDate: '2025-11-20', endDate: '2025-11-30', budget: 1500, spend: 1500, impressions: 150000, clicks: 7200, conversions: 360, sales: 16000 },
  { id: 9, campaignId: 4, platform: 'tiktok',   name: 'BF · Spark Ads',                   status: 'completed', startDate: '2025-11-22', endDate: '2025-11-30', budget: 900,  spend: 900,  impressions: 120000, clicks: 5400, conversions: 240, sales: 11000 },
  // Campaign 5 · Navidad 2025
  { id: 10, campaignId: 5, platform: 'facebook', name: 'Navidad · Guía de regalos',       status: 'completed', startDate: '2025-12-01', endDate: '2025-12-31', budget: 1400, spend: 1380, impressions: 130000, clicks: 6100, conversions: 290, sales: 13000 },
  { id: 11, campaignId: 5, platform: 'google',   name: 'Navidad · Search + Shopping',     status: 'completed', startDate: '2025-12-01', endDate: '2025-12-31', budget: 1000, spend: 980,  impressions: 98000,  clicks: 4600, conversions: 210, sales: 9000 },
  // Campaign 6 · Rebaixes Estiu 2026
  { id: 12, campaignId: 6, platform: 'facebook',  name: 'Rebaixes Estiu · Catàleg dinàmic',    status: 'active', startDate: '2026-06-01', endDate: '2026-07-31', budget: 2000, spend: 820,  impressions: 72000, clicks: 2800, conversions: 86,  sales: 3800 },
  { id: 13, campaignId: 6, platform: 'google',    name: 'Rebaixes Estiu · Shopping + Search',  status: 'active', startDate: '2026-06-01', endDate: '2026-07-31', budget: 1800, spend: 680,  impressions: 48000, clicks: 2300, conversions: 72,  sales: 3200 },
  { id: 14, campaignId: 6, platform: 'tiktok',    name: 'Rebaixes Estiu · Spark Ads',          status: 'active', startDate: '2026-06-02', endDate: '2026-07-31', budget: 1000, spend: 380,  impressions: 84000, clicks: 1900, conversions: 48,  sales: 2100 },
  { id: 15, campaignId: 6, platform: 'instagram', name: 'Rebaixes Estiu · Reels Promotion',    status: 'active', startDate: '2026-06-04', endDate: '2026-07-31', budget: 600,  spend: 240,  impressions: 32000, clicks: 1100, conversions: 28,  sales: 1200 },
]

// ── Influencers ────────────────────────────────────────────────────────────────
export const socialInfluencers = [
  {
    id: 1, name: 'Ana García', alias: '@analifestyle', photo: null,
    platform: 'instagram', platforms: ['instagram', 'tiktok'],
    followers: 85000, niche: 'Lifestyle', contact: 'ana@talentx.com', agency: 'TalentX',
    country: 'Espanya', language: 'Espanyol', status: 'active',
    collaborations: 3, salesGenerated: 8400, rating: 4.8,
    engagementMid: 4.2, reachMid: 42000, clicksMid: 980, conversionsMid: 48,
    contentQuality: 5, reliability: 4.5, brandAffinity: 5, reputationRisk: 1,
    notes: 'Excel·lent creadora, molt professional. Recomanada per a campanyes de moda i lifestyle.',
  },
  {
    id: 2, name: 'Pablo Vidal', alias: '@pablovidal', photo: null,
    platform: 'instagram', platforms: ['instagram', 'youtube'],
    followers: 42000, niche: 'Moda masculina', contact: 'pablo@gmail.com', agency: null,
    country: 'Espanya', language: 'Espanyol', status: 'active',
    collaborations: 2, salesGenerated: 3200, rating: 4.2,
    engagementMid: 3.8, reachMid: 21000, clicksMid: 540, conversionsMid: 28,
    contentQuality: 4, reliability: 4, brandAffinity: 4.5, reputationRisk: 1,
    notes: 'Bon influencer per a moda masculina. Compleix els terminis.',
  },
  {
    id: 3, name: 'Marta Domínguez', alias: '@martamoda', photo: null,
    platform: 'tiktok', platforms: ['tiktok', 'instagram'],
    followers: 234000, niche: 'Moda', contact: 'marta@agencia-moda.com', agency: 'Moda Agency',
    country: 'Espanya', language: 'Espanyol', status: 'active',
    collaborations: 4, salesGenerated: 18600, rating: 4.6,
    engagementMid: 6.1, reachMid: 120000, clicksMid: 3400, conversionsMid: 180,
    contentQuality: 5, reliability: 5, brandAffinity: 4.5, reputationRisk: 1,
    notes: 'Top influencer a TikTok. Alta conversió. Preu elevat però ROI excel·lent.',
  },
  {
    id: 4, name: 'Luis Fernández', alias: '@luisf_style', photo: null,
    platform: 'instagram', platforms: ['instagram'],
    followers: 18000, niche: 'Streetwear', contact: 'luisf@outlook.com', agency: null,
    country: 'Espanya', language: 'Espanyol', status: 'prospect',
    collaborations: 0, salesGenerated: 0, rating: 0,
    engagementMid: 5.4, reachMid: 9000, clicksMid: 240, conversionsMid: 0,
    contentQuality: 3.5, reliability: 0, brandAffinity: 3, reputationRisk: 2,
    notes: 'Perfil interessant per a streetwear. Pendent del primer contacte.',
  },
  {
    id: 5, name: 'Sofía Ramírez', alias: '@sofiabeauty', photo: null,
    platform: 'instagram', platforms: ['instagram', 'youtube', 'tiktok'],
    followers: 156000, niche: 'Bellesa', contact: 'sofia@starmanagement.com', agency: 'Star Management',
    country: 'Espanya', language: 'Espanyol', status: 'archived',
    collaborations: 1, salesGenerated: 1200, rating: 2.8,
    engagementMid: 2.1, reachMid: 45000, clicksMid: 300, conversionsMid: 12,
    contentQuality: 3, reliability: 2, brandAffinity: 2.5, reputationRisk: 4,
    notes: 'Arxivada. No va complir els lliurables a la col·laboració de Nadal.',
  },
  {
    id: 6, name: 'Elena Vega', alias: '@elenavegafit', photo: null,
    platform: 'instagram', platforms: ['instagram', 'youtube'],
    followers: 67000, niche: 'Fitness', contact: 'elena@fit-agency.com', agency: 'FitAgency',
    country: 'Espanya', language: 'Espanyol', status: 'active',
    collaborations: 2, salesGenerated: 4800, rating: 4.4,
    engagementMid: 4.8, reachMid: 32000, clicksMid: 780, conversionsMid: 42,
    contentQuality: 4.5, reliability: 4.5, brandAffinity: 4, reputationRisk: 1,
    notes: 'Bona per a campanyes de roba esportiva i lifestyle actiu.',
  },
  {
    id: 7, name: 'Clara Puig', alias: '@clarapuig_moda', photo: null,
    platform: 'instagram', platforms: ['instagram'],
    followers: 52000, niche: 'Moda i lifestyle', contact: 'clara@talentx.com', agency: 'TalentX',
    country: 'Espanya', language: 'Català', status: 'active',
    collaborations: 1, salesGenerated: 0, rating: 0,
    engagementMid: 5.2, reachMid: 26000, clicksMid: 680, conversionsMid: 0,
    contentQuality: 0, reliability: 0, brandAffinity: 4, reputationRisk: 1,
    notes: 'Nova col·laboració. Primera campanya amb la marca. Perfil molt alineat amb l\'estètica Sazed.',
  },
  {
    id: 8, name: 'Marc Roca', alias: '@marcroca_style', photo: null,
    platform: 'instagram', platforms: ['instagram', 'tiktok'],
    followers: 28000, niche: 'Moda masculina', contact: 'marc.roca@gmail.com', agency: null,
    country: 'Espanya', language: 'Català', status: 'active',
    collaborations: 1, salesGenerated: 0, rating: 0,
    engagementMid: 6.1, reachMid: 14000, clicksMid: 380, conversionsMid: 0,
    contentQuality: 0, reliability: 0, brandAffinity: 4.5, reputationRisk: 1,
    notes: 'Microinfluencer català. Alta afinitat de marca. Col·laboració pendent de publicació (12/06).',
  },
]

// ── Collaborations ────────────────────────────────────────────────────────────
export const socialCollaborations = [
  {
    id: 1, influencerId: 1, influencerName: 'Ana García', influencerAlias: '@analifestyle',
    campaignId: 1, campaignName: 'Primavera 2026',
    format: 'Reel + 3 Stories', publishDate: '2026-04-01', cost: 1800,
    linkId: 1, code: 'ANA15',
    status: 'completed',
    clicks: 2800, conversions: 134, sales: 5600,
    deliverables: '1 Reel (60s), 3 Stories amb swipe up, menció a la bio durant 7 dies',
    reach: 67000, impressions: 89000, views: 0, likes: 3400, comments: 187, shares: 240,
    evidences: ['captura_reel.jpg', 'captura_story1.jpg'],
    expectedReach: 60000, expectedClicks: 2000, expectedConversions: 100,
    observations: 'Resultats per sobre del que s\'esperava. Excel·lent col·laboració.',
    recommendation: 'Renovar per a la pròxima campanya',
  },
  {
    id: 2, influencerId: 2, influencerName: 'Pablo Vidal', influencerAlias: '@pablovidal',
    campaignId: 1, campaignName: 'Primavera 2026',
    format: 'Post + 2 Stories', publishDate: '2026-04-08', cost: 800,
    linkId: 2, code: 'PABLO10',
    status: 'completed',
    clicks: 890, conversions: 42, sales: 1680,
    deliverables: '1 post carrusel, 2 stories amb enllaç',
    reach: 28000, impressions: 34000, views: 0, likes: 1240, comments: 67, shares: 89,
    evidences: ['captura_post.jpg'],
    expectedReach: 30000, expectedClicks: 1000, expectedConversions: 50,
    observations: 'Resultats lleugerament per sota de l\'objectiu.',
    recommendation: 'Revisar el briefing abans de la pròxima col·laboració',
  },
  {
    id: 3, influencerId: 3, influencerName: 'Marta Domínguez', influencerAlias: '@martamoda',
    campaignId: 1, campaignName: 'Primavera 2026',
    format: '2 TikToks + Dueto', publishDate: '2026-04-10', cost: 2400,
    linkId: 3, code: 'MARTA20',
    status: 'active',
    clicks: 4200, conversions: 0, sales: 0,
    deliverables: '2 TikToks de 60s, 1 duet amb el compte oficial',
    reach: 0, impressions: 0, views: 89000, likes: 0, comments: 0, shares: 0,
    evidences: [],
    expectedReach: 0, expectedClicks: 5000, expectedConversions: 200,
    observations: 'Primer TikTok publicat. Segon pendent.',
    recommendation: '',
  },
  {
    id: 4, influencerId: 6, influencerName: 'Elena Vega', influencerAlias: '@elenavegafit',
    campaignId: 2, campaignName: 'Eco Collection',
    format: 'Post + Story', publishDate: '2026-04-12', cost: 900,
    linkId: 4, code: 'ELENA10',
    status: 'completed',
    clicks: 1200, conversions: 58, sales: 2400,
    deliverables: '1 post imatge, 1 story amb enllaç',
    reach: 38000, impressions: 45000, views: 0, likes: 1890, comments: 89, shares: 120,
    evidences: ['captura_eco_post.jpg'],
    expectedReach: 35000, expectedClicks: 1000, expectedConversions: 50,
    observations: 'Molt bons resultats per a una campanya d\'awareness.',
    recommendation: 'Continuar la col·laboració',
  },
  {
    id: 5, influencerId: 1, influencerName: 'Ana García', influencerAlias: '@analifestyle',
    campaignId: 5, campaignName: 'Navidad 2025',
    format: 'Reel + 5 Stories', publishDate: '2025-12-10', cost: 2000,
    linkId: 5, code: 'ANAXMAS',
    status: 'completed',
    clicks: 3400, conversions: 167, sales: 7800,
    deliverables: '1 Reel nadalenc, 5 stories amb countdowns i enllaços',
    reach: 78000, impressions: 102000, views: 0, likes: 4200, comments: 234, shares: 380,
    evidences: ['captura_navidad_reel.jpg', 'captura_navidad_stories.jpg'],
    expectedReach: 70000, expectedClicks: 3000, expectedConversions: 150,
    observations: 'Excel·lent rendiment nadalenc. Top col·laboració de l\'any.',
    recommendation: 'Col·laboració prioritària per a pròximes campanyes',
  },
  // Campaign 6 · Rebaixes Estiu 2026
  {
    id: 6, influencerId: 3, influencerName: 'Marta Domínguez', influencerAlias: '@martamoda',
    campaignId: 6, campaignName: 'Rebaixes Estiu 2026',
    format: '2 TikToks + Reel Instagram', publishDate: '2026-06-05', cost: 2800,
    linkId: 7, code: 'MARTA30',
    status: 'active',
    clicks: 3200, conversions: 98, sales: 4200,
    deliverables: '2 TikToks de 60s + 1 Reel d\'Instagram. TikTok #1 i #2 publicats. Reel pendent.',
    reach: 112000, impressions: 142000, views: 180000, likes: 9800, comments: 420, shares: 2400,
    evidences: ['tiktok_rebaixes_1.jpg', 'tiktok_rebaixes_2.jpg'],
    expectedReach: 100000, expectedClicks: 5000, expectedConversions: 200,
    observations: 'Dos TikToks publicats amb molt bon rendiment. El primer va superar les 180K visualitzacions.',
    recommendation: '',
  },
  {
    id: 7, influencerId: 1, influencerName: 'Ana García', influencerAlias: '@analifestyle',
    campaignId: 6, campaignName: 'Rebaixes Estiu 2026',
    format: 'Reel + 4 Stories', publishDate: '2026-06-07', cost: 2000,
    linkId: 8, code: 'ANA30',
    status: 'active',
    clicks: 1800, conversions: 67, sales: 2900,
    deliverables: '1 Reel + 4 Stories amb swipe up a la pàgina de rebaixes. Reel publicat. Stories en curs.',
    reach: 54000, impressions: 71000, views: 0, likes: 3800, comments: 198, shares: 320,
    evidences: ['reel_rebaixes_ana.jpg'],
    expectedReach: 50000, expectedClicks: 1500, expectedConversions: 80,
    observations: 'Molt bon inici. Per sobre del reach esperat als 2 dies de publicació.',
    recommendation: '',
  },
  {
    id: 8, influencerId: 7, influencerName: 'Clara Puig', influencerAlias: '@clarapuig_moda',
    campaignId: 6, campaignName: 'Rebaixes Estiu 2026',
    format: 'Reel + 3 Stories', publishDate: '2026-06-09', cost: 1200,
    linkId: 9, code: 'CLARA20',
    status: 'active',
    clicks: 320, conversions: 0, sales: 0,
    deliverables: '1 Reel + 3 Stories. Reel publicat avui. Stories pendents.',
    reach: 8400, impressions: 11000, views: 8400, likes: 620, comments: 42, shares: 89,
    evidences: ['reel_clara_rebaixes.jpg'],
    expectedReach: 28000, expectedClicks: 800, expectedConversions: 30,
    observations: 'Publicació d\'avui. Massa d\'hora per avaluar el rendiment.',
    recommendation: '',
  },
  {
    id: 9, influencerId: 8, influencerName: 'Marc Roca', influencerAlias: '@marcroca_style',
    campaignId: 6, campaignName: 'Rebaixes Estiu 2026',
    format: 'Post + 2 Stories', publishDate: '2026-06-12', cost: 800,
    linkId: null, code: 'MARC15',
    status: 'pending',
    clicks: 0, conversions: 0, sales: 0,
    deliverables: '1 post imatge + 2 stories. Publicació prevista el 12/06.',
    reach: 0, impressions: 0, views: 0, likes: 0, comments: 0, shares: 0,
    evidences: [],
    expectedReach: 14000, expectedClicks: 380, expectedConversions: 15,
    observations: 'Col·laboració acordada. Briefing enviat. Pendent de publicació.',
    recommendation: '',
  },
]

// ── Links ─────────────────────────────────────────────────────────────────────
export const socialLinks = [
  { id: 1, name: 'Enllaç bio Ana García - Primavera', url: 'https://mystore.es/primavera-2026', campaignId: 1, campaignName: 'Primavera 2026', origin: 'instagram', influencerId: 1, influencerName: 'Ana García', utmSource: 'instagram', utmMedium: 'influencer', utmCampaign: 'primavera2026', utmContent: 'ana-garcia', clicks: 2800, sessions: 2540, carts: 580, purchases: 134, revenue: 5600, conversion: 5.28 },
  { id: 2, name: 'Enllaç bio Pablo - Primavera',       url: 'https://mystore.es/primavera-2026', campaignId: 1, campaignName: 'Primavera 2026', origin: 'instagram', influencerId: 2, influencerName: 'Pablo Vidal',  utmSource: 'instagram', utmMedium: 'influencer', utmCampaign: 'primavera2026', utmContent: 'pablo-vidal', clicks: 890,  sessions: 780,  carts: 145, purchases: 42,  revenue: 1680, conversion: 5.38 },
  { id: 3, name: 'Enllaç TikTok Marta - Primavera',    url: 'https://mystore.es/primavera-2026', campaignId: 1, campaignName: 'Primavera 2026', origin: 'tiktok',    influencerId: 3, influencerName: 'Marta Domínguez', utmSource: 'tiktok', utmMedium: 'influencer', utmCampaign: 'primavera2026', utmContent: 'marta-moda', clicks: 4200, sessions: 3800, carts: 820, purchases: 0,   revenue: 0,    conversion: 0 },
  { id: 4, name: 'Enllaç bio Elena - Eco',             url: 'https://mystore.es/eco-collection', campaignId: 2, campaignName: 'Eco Collection', origin: 'instagram', influencerId: 6, influencerName: 'Elena Vega',   utmSource: 'instagram', utmMedium: 'influencer', utmCampaign: 'ecocollection', utmContent: 'elena-vega', clicks: 1200, sessions: 1050, carts: 210, purchases: 58,  revenue: 2400, conversion: 5.52 },
  { id: 5, name: 'Enllaç general Primavera (bio)',      url: 'https://mystore.es/primavera-2026', campaignId: 1, campaignName: 'Primavera 2026', origin: 'instagram', influencerId: null, influencerName: null, utmSource: 'instagram', utmMedium: 'organic', utmCampaign: 'primavera2026', utmContent: 'bio', clicks: 1340, sessions: 1200, carts: 290, purchases: 89, revenue: 3780, conversion: 7.42 },
  { id: 6, name: 'Enllaç Twitter Eco',                 url: 'https://mystore.es/eco-collection', campaignId: 2, campaignName: 'Eco Collection', origin: 'twitter',   influencerId: null, influencerName: null, utmSource: 'twitter', utmMedium: 'organic', utmCampaign: 'ecocollection', utmContent: 'tweet', clicks: 680, sessions: 580, carts: 89, purchases: 24, revenue: 980, conversion: 4.14 },
  // Campaign 6 · Rebaixes Estiu 2026
  { id: 7,  name: 'Enllaç TikTok Marta Domínguez - Rebaixes Estiu',     url: 'https://mystore.es/rebaixes-estiu-2026', campaignId: 6, campaignName: 'Rebaixes Estiu 2026', origin: 'tiktok',    influencerId: 3, influencerName: 'Marta Domínguez', utmSource: 'tiktok',    utmMedium: 'influencer', utmCampaign: 'rebaixes2026', utmContent: 'marta-moda',   clicks: 3200, sessions: 2900, carts: 640, purchases: 98, revenue: 4200, conversion: 3.38 },
  { id: 8,  name: 'Enllaç Instagram Ana García - Rebaixes Estiu',        url: 'https://mystore.es/rebaixes-estiu-2026', campaignId: 6, campaignName: 'Rebaixes Estiu 2026', origin: 'instagram', influencerId: 1, influencerName: 'Ana García',       utmSource: 'instagram', utmMedium: 'influencer', utmCampaign: 'rebaixes2026', utmContent: 'ana-garcia',   clicks: 1800, sessions: 1620, carts: 310, purchases: 67, revenue: 2900, conversion: 4.14 },
  { id: 9,  name: 'Enllaç Instagram Clara Puig - Rebaixes Estiu',        url: 'https://mystore.es/rebaixes-estiu-2026', campaignId: 6, campaignName: 'Rebaixes Estiu 2026', origin: 'instagram', influencerId: 7, influencerName: 'Clara Puig',        utmSource: 'instagram', utmMedium: 'influencer', utmCampaign: 'rebaixes2026', utmContent: 'clara-puig',   clicks: 320,  sessions: 290,  carts: 42,  purchases: 0,  revenue: 0,    conversion: 0    },
  { id: 10, name: 'Enllaç general Rebaixes Estiu (bio + orgànic)',        url: 'https://mystore.es/rebaixes-estiu-2026', campaignId: 6, campaignName: 'Rebaixes Estiu 2026', origin: 'instagram', influencerId: null, influencerName: null,              utmSource: 'instagram', utmMedium: 'organic',    utmCampaign: 'rebaixes2026', utmContent: 'bio-organic', clicks: 980,  sessions: 840,  carts: 168, purchases: 52, revenue: 2200, conversion: 6.19 },
]

// ── Alerts ────────────────────────────────────────────────────────────────────
export const socialAlerts = [
  { id: 1, date: '2026-04-17', type: 'reach_drop',        entity: 'Compte de Facebook @Marca España',       severity: 'high',   status: 'pending',  responsible: null,           description: 'Caiguda del 35% en abast les últimes 48h. Token possiblement caducat.' },
  { id: 2, date: '2026-04-17', type: 'missing_metrics',   entity: 'Col·laboració: Marta Domínguez #3',      severity: 'medium', status: 'pending',  responsible: 'Laura Martínez', description: 'Segon TikTok publicat però sense mètriques carregades després de 72h.' },
  { id: 3, date: '2026-04-16', type: 'broken_link',       entity: 'Enllaç: Bio Link General Primavera',     severity: 'high',   status: 'reviewed', responsible: 'Carlos Ruiz',  description: 'L\'enllaç retorna un 404. Verifica l\'URL de destinació.' },
  { id: 4, date: '2026-04-15', type: 'low_campaign',      entity: 'Campanya: Eco Collection',               severity: 'medium', status: 'assigned', responsible: 'Carlos Ruiz',  description: 'Conversió per sota del 2% objectiu. Revisa les creativitats.' },
  { id: 5, date: '2026-04-14', type: 'negative_comments', entity: 'Post: "Tendències outfit estiu 2026"',   severity: 'low',    status: 'reviewed', responsible: 'Laura Martínez', description: '12 comentaris negatius sobre talles. Monitoritzar.' },
  { id: 6, date: '2026-04-13', type: 'unvalidated_data',  entity: 'Mètriques: Col·laboració Pablo Vidal #2', severity: 'low',    status: 'pending',  responsible: null,           description: 'Dades introduïdes manualment sense validar pel supervisor.' },
  { id: 7, date: '2026-04-12', type: 'high_cost',         entity: 'Col·laboració: Marta Domínguez #3',      severity: 'medium', status: 'assigned', responsible: 'Laura Martínez', description: 'Cost/conversió actualment ∞. Esperant el segon TikTok.' },
  { id: 8, date: '2026-06-09', type: 'missing_metrics',  entity: 'Col·laboració: Clara Puig #8',            severity: 'low',    status: 'pending',  responsible: null,             description: 'Reel publicat avui. Mètriques inicials carregades, Stories pendents de publicació.' },
  { id: 9, date: '2026-06-08', type: 'high_cost',        entity: 'Anunci: Rebaixes Estiu · Spark Ads #14',  severity: 'low',    status: 'pending',  responsible: 'Laura Martínez', description: 'CPM pujant als últims 2 dies (+18%). Monitoritzar si supera el benchmark setmanal.' },
]

// ── Manual Metrics Upload history ─────────────────────────────────────────────
export const metricsHistory = [
  { id: 1, date: '2026-04-14', influencerName: 'Marta Domínguez', collaborationId: 3, publicationDesc: 'TikTok #1 - Primavera', uploadedBy: 'Laura Martínez', status: 'validated', reach: 45000, impressions: 67000, views: 89000, likes: 5400, comments: 234, shares: 890 },
  { id: 2, date: '2026-04-12', influencerName: 'Pablo Vidal',    collaborationId: 2, publicationDesc: 'Post Carrusel - Primavera', uploadedBy: 'Carlos Ruiz',   status: 'pending',   reach: 28000, impressions: 34000, views: 0,     likes: 1240, comments: 67,  shares: 89 },
  { id: 3, date: '2026-04-11', influencerName: 'Elena Vega',     collaborationId: 4, publicationDesc: 'Post Eco Collection',      uploadedBy: 'Laura Martínez', status: 'validated', reach: 38000, impressions: 45000, views: 0,     likes: 1890, comments: 89,  shares: 120 },
  { id: 4, date: '2026-06-05', influencerName: 'Marta Domínguez', collaborationId: 6, publicationDesc: 'TikTok #1 - Rebaixes Estiu', uploadedBy: 'Laura Martínez', status: 'validated', reach: 112000, impressions: 142000, views: 180000, likes: 9800, comments: 420, shares: 2400 },
  { id: 5, date: '2026-06-07', influencerName: 'Ana García',       collaborationId: 7, publicationDesc: 'Reel Instagram - Rebaixes Estiu', uploadedBy: 'Laura Martínez', status: 'validated', reach: 54000, impressions: 71000, views: 0, likes: 3800, comments: 198, shares: 320 },
  { id: 6, date: '2026-06-09', influencerName: 'Clara Puig',       collaborationId: 8, publicationDesc: 'Reel Instagram - Rebaixes Estiu', uploadedBy: 'Laura Martínez', status: 'pending',   reach: 8400,  impressions: 11000,  views: 8400, likes: 620,  comments: 42,  shares: 89 },
]

// ── ERP Products (for Social CRM product linking) ────────────────────────────
// These mirror the ERP product catalog. Used when linking products to campaign posts,
// influencers and ad sets.
export const erpProducts = [
  { id: 1,  name: 'Samarreta Bàsica Blanc',       sku: 'SAZ-001', price: 19.99, category: 'Samarretes' },
  { id: 2,  name: 'Samarreta Bàsica Negre',       sku: 'SAZ-002', price: 19.99, category: 'Samarretes' },
  { id: 3,  name: 'Samarreta Estampada Floral',   sku: 'SAZ-003', price: 24.99, category: 'Samarretes' },
  { id: 4,  name: 'Pantalons Slim Blau Marí',     sku: 'SAZ-010', price: 49.99, category: 'Pantalons'  },
  { id: 5,  name: 'Pantalons Wide Leg Beige',     sku: 'SAZ-011', price: 54.99, category: 'Pantalons'  },
  { id: 6,  name: 'Jaqueta Casual Verda',         sku: 'SAZ-020', price: 79.99, category: 'Jaquetes'   },
  { id: 7,  name: 'Vestit Midi Floral',           sku: 'SAZ-030', price: 59.99, category: 'Vestits'    },
  { id: 8,  name: 'Vestit Mini Negre',            sku: 'SAZ-031', price: 44.99, category: 'Vestits'    },
  { id: 9,  name: 'Abric de Llana Gris',          sku: 'SAZ-040', price: 129.99, category: 'Abrics'    },
  { id: 10, name: 'Faldilla Plissada Rosa',       sku: 'SAZ-050', price: 39.99, category: 'Faldilles'  },
  { id: 11, name: 'Polo Clàssic Marró',           sku: 'SAZ-060', price: 34.99, category: 'Polos'      },
  { id: 12, name: 'Bossa de Mà de Cuir',          sku: 'SAZ-070', price: 89.99, category: 'Accessoris' },
  { id: 13, name: 'Cinturó Teixit Blau',          sku: 'SAZ-080', price: 24.99, category: 'Accessoris' },
  { id: 14, name: 'Sandàlies d\'Estiu Blanques',  sku: 'SAZ-090', price: 44.99, category: 'Calçat'     },
  { id: 15, name: 'Sneakers Casual Blanc',        sku: 'SAZ-100', price: 69.99, category: 'Calçat'     },
]

// ── KPI Summary (Dashboard) ───────────────────────────────────────────────────
export const dashboardKPIs = {
  totalFollowers:      { value: 105700, change: +3.4, label: 'Seguidors totals' },
  totalReach:          { value: 212000, change: +8.2, label: 'Abast total' },
  avgEngagement:       { value: 5.3,    change: +0.4, label: 'Engagement mitjà (%)' },
  totalClicks:         { value: 12400,  change: +15.1, label: 'Clics totals' },
  totalConversions:    { value: 401,    change: +22.3, label: 'Conversions' },
  attributedSales:     { value: 17400,  change: +18.7, label: 'Vendes atribuïdes (€)' },
  activeCollaborations:{ value: 2,      change: 0,     label: 'Col·laboracions actives' },
}

export const evolutionData = {
  labels: ['Gen', 'Feb', 'Març', 'Abr'],
  followers: [98400, 100200, 103100, 105700],
  reach:     [145000, 168000, 189000, 212000],
  engagement:[4.8, 5.0, 5.1, 5.3],
  conversions:[210, 260, 320, 401],
}

// ── Top/Worst posts ───────────────────────────────────────────────────────────
export const topPosts = [1, 3, 7, 8, 2]   // post IDs by engagement
export const worstPosts = [9, 10, 5, 4, 6] // post IDs by engagement

// ── Helper utilities ──────────────────────────────────────────────────────────
export function getPlatform(key) {
  return PLATFORMS[key] || { label: key, color: '#999', bg: '#f5f5f5' }
}

export function getAdPlatform(key) {
  return AD_PLATFORMS[key] || { label: key, color: '#999', bg: '#f5f5f5' }
}

// ── Campaign relations ────────────────────────────────────────────────────────
export function getCampaignPosts(campaignId)   { return socialPosts.filter(p => p.campaignId === campaignId) }
export function getCampaignCollabs(campaignId) { return socialCollaborations.filter(c => c.campaignId === campaignId) }
export function getCampaignAds(campaignId)     { return socialAds.filter(a => a.campaignId === campaignId) }
export function getCampaignLinks(campaignId)   { return socialLinks.filter(l => l.campaignId === campaignId) }

// Campaigns an influencer has participated in (via collaborations), for cross-nav.
export function getInfluencerCampaigns(influencerId) {
  const ids = [...new Set(
    socialCollaborations.filter(c => c.influencerId === influencerId).map(c => c.campaignId)
  )]
  return ids
    .map(id => socialCampaigns.find(c => c.id === id))
    .filter(Boolean)
}

// Derived ad metrics (kept out of the raw data to avoid hand-math drift).
export function adMetrics(ad) {
  return {
    ctr:  ad.impressions ? (ad.clicks / ad.impressions) * 100 : 0,
    cpc:  ad.clicks ? ad.spend / ad.clicks : 0,
    cpa:  ad.conversions ? ad.spend / ad.conversions : 0,
    roas: ad.spend ? ad.sales / ad.spend : 0,
  }
}

// ── Channel breakdown ─────────────────────────────────────────────────────────
// Single source of truth: a campaign's per-channel performance is DERIVED from
// its posts (owned), collaborations (influencers) and ad sets (paid). Totals are
// the sum of the three, so the numbers never go out of sync with their sources.
export function getCampaignChannelBreakdown(campaignId) {
  const posts   = getCampaignPosts(campaignId)
  const collabs = getCampaignCollabs(campaignId)
  const ads     = getCampaignAds(campaignId)
  const links   = getCampaignLinks(campaignId)
  const sum = (arr, k) => arr.reduce((s, x) => s + (x[k] || 0), 0)

  // Owned = organic posts; sales/conversions attributed via non-influencer links.
  const organicLinks = links.filter(l => !l.influencerId)
  const owned = {
    ...CAMPAIGN_CHANNELS.owned,
    items:       posts.length,
    reach:       sum(posts, 'reach'),
    impressions: sum(posts, 'impressions'),
    clicks:      sum(posts, 'clicks'),
    conversions: sum(organicLinks, 'purchases'),
    sales:       sum(organicLinks, 'revenue'),
    cost:        0,
  }
  const influencers = {
    ...CAMPAIGN_CHANNELS.influencers,
    items:       collabs.length,
    reach:       sum(collabs, 'reach'),
    impressions: sum(collabs, 'impressions'),
    clicks:      sum(collabs, 'clicks'),
    conversions: sum(collabs, 'conversions'),
    sales:       sum(collabs, 'sales'),
    cost:        sum(collabs, 'cost'),
  }
  const paid = {
    ...CAMPAIGN_CHANNELS.paid,
    items:       ads.length,
    reach:       0,
    impressions: sum(ads, 'impressions'),
    clicks:      sum(ads, 'clicks'),
    conversions: sum(ads, 'conversions'),
    sales:       sum(ads, 'sales'),
    cost:        sum(ads, 'spend'),
  }

  const channels = [owned, influencers, paid].map(ch => ({
    ...ch,
    roas: ch.cost > 0 ? ch.sales / ch.cost : 0,
  }))

  const totals = channels.reduce((t, ch) => ({
    reach:       t.reach + ch.reach,
    impressions: t.impressions + ch.impressions,
    clicks:      t.clicks + ch.clicks,
    conversions: t.conversions + ch.conversions,
    sales:       t.sales + ch.sales,
    cost:        t.cost + ch.cost,
  }), { reach: 0, impressions: 0, clicks: 0, conversions: 0, sales: 0, cost: 0 })
  totals.roas = totals.cost > 0 ? totals.sales / totals.cost : 0

  return { channels, totals }
}

export function formatNumber(n) {
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M'
  if (n >= 1000) return (n / 1000).toFixed(1) + 'K'
  return String(n)
}

export function formatCurrency(n) {
  return new Intl.NumberFormat('ca-ES', { style: 'currency', currency: 'EUR' }).format(n)
}

export function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('ca-ES', { day: '2-digit', month: '2-digit', year: 'numeric' })
}
