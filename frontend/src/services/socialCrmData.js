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

export const CONTENT_TYPES = ['Imagen', 'Vídeo', 'Reel', 'Story', 'Carrusel', 'Tweet', 'Hilo', 'Short']

export const CAMPAIGN_OBJECTIVES = ['Awareness', 'Tráfico', 'Conversiones', 'Engagement', 'Ventas', 'Leads']

export const CAMPAIGN_STATUSES = {
  active:    { label: 'Activa',     cls: 'badge-active' },
  draft:     { label: 'Borrador',   cls: 'badge-inactive' },
  paused:    { label: 'Pausada',    cls: 'badge-warning' },
  completed: { label: 'Completada', cls: 'badge-info' },
}

export const COLLAB_STATUSES = {
  draft:     { label: 'Borrador',   cls: 'badge-inactive' },
  pending:   { label: 'Pendiente',  cls: 'badge-warning' },
  active:    { label: 'Activa',     cls: 'badge-active' },
  completed: { label: 'Completada', cls: 'badge-info' },
  cancelled: { label: 'Cancelada',  cls: 'badge-error' },
}

export const ALERT_TYPES = {
  reach_drop:       { label: 'Caída de alcance',           icon: 'TrendingDown' },
  broken_link:      { label: 'Enlace roto',                icon: 'LinkOff' },
  low_campaign:     { label: 'Campaña bajo rendimiento',   icon: 'Target' },
  negative_comments:{ label: 'Comentarios negativos altos',icon: 'MessageCircleWarning' },
  missing_metrics:  { label: 'Métricas pendientes',        icon: 'ClipboardX' },
  high_cost:        { label: 'Coste alto sin conversión',  icon: 'DollarSign' },
  unvalidated_data: { label: 'Dato manual sin validar',    icon: 'AlertCircle' },
}

// ── Social Accounts ───────────────────────────────────────────────────────────
export const socialAccounts = [
  { id: 1, platform: 'instagram', name: 'Marca Principal', username: '@marca.es',     status: 'connected', lastSync: '2026-04-17T09:30:00', followers: 48300, posts: 524, responsible: 'Laura Martínez', observations: 'Cuenta principal de la marca' },
  { id: 2, platform: 'tiktok',    name: 'Marca TikTok',    username: '@marca_tiktok', status: 'connected', lastSync: '2026-04-17T08:00:00', followers: 22100, posts: 188, responsible: 'Laura Martínez', observations: '' },
  { id: 3, platform: 'twitter',   name: 'Marca Twitter',   username: '@marca_es',     status: 'connected', lastSync: '2026-04-16T22:00:00', followers: 9800,  posts: 1204, responsible: 'Carlos Ruiz', observations: '' },
  { id: 4, platform: 'facebook',  name: 'Página Facebook', username: 'Marca España',  status: 'disconnected', lastSync: '2026-04-10T10:00:00', followers: 15200, posts: 340, responsible: 'Carlos Ruiz', observations: 'Token caducado, renovar' },
  { id: 5, platform: 'youtube',   name: 'Canal YouTube',   username: 'Marca Oficial', status: 'connected', lastSync: '2026-04-17T07:00:00', followers: 6700,  posts: 89,  responsible: 'Ana Torres', observations: '' },
  { id: 6, platform: 'linkedin',  name: 'Empresa LinkedIn','username': 'Marca S.L.',  status: 'connected', lastSync: '2026-04-17T06:00:00', followers: 3400,  posts: 167, responsible: 'Ana Torres', observations: '' },
]

// ── Social Posts ──────────────────────────────────────────────────────────────
export const socialPosts = [
  { id: 1,  date: '2026-04-15', platform: 'instagram', accountId: 1, accountName: '@marca.es',     title: 'Nueva colección Primavera 2026 🌸', type: 'Reel',    campaignId: 1, campaignName: 'Primavera 2026', productId: null, likes: 2840, comments: 134, shares: 312, saves: 780,  views: 28400, reach: 34200, impressions: 48000, clicks: 890, engagement: 7.2 },
  { id: 2,  date: '2026-04-14', platform: 'instagram', accountId: 1, accountName: '@marca.es',     title: 'Detrás de cámaras: making of',       type: 'Carrusel', campaignId: 1, campaignName: 'Primavera 2026', productId: null, likes: 1240, comments: 87,  shares: 145, saves: 320,  views: 0,     reach: 18400, impressions: 22000, clicks: 340, engagement: 4.8 },
  { id: 3,  date: '2026-04-13', platform: 'tiktok',    accountId: 2, accountName: '@marca_tiktok', title: 'Tendencias outfit verano 2026',       type: 'Vídeo',   campaignId: 1, campaignName: 'Primavera 2026', productId: 3,   likes: 8900, comments: 340, shares: 1200, saves: 2300, views: 142000, reach: 89000, impressions: 142000, clicks: 2100, engagement: 8.9 },
  { id: 4,  date: '2026-04-12', platform: 'instagram', accountId: 1, accountName: '@marca.es',     title: 'Descubre nuestros nuevos colores',    type: 'Imagen',  campaignId: 1, campaignName: 'Primavera 2026', productId: 1,   likes: 980,  comments: 42,  shares: 89,  saves: 210,  views: 0,     reach: 12300, impressions: 15600, clicks: 230, engagement: 3.4 },
  { id: 5,  date: '2026-04-10', platform: 'twitter',   accountId: 3, accountName: '@marca_es',     title: 'Lanzamos la nueva línea eco-friendly', type: 'Tweet',  campaignId: 2, campaignName: 'Eco Collection', productId: null, likes: 345,  comments: 67,  shares: 234, saves: 0,    views: 12400, reach: 9800,  impressions: 12400, clicks: 189, engagement: 3.1 },
  { id: 6,  date: '2026-04-09', platform: 'tiktok',    accountId: 2, accountName: '@marca_tiktok', title: 'Tutorial: cómo combinar prendas',      type: 'Short',   campaignId: null, campaignName: null, productId: null, likes: 4500, comments: 212, shares: 890, saves: 1800, views: 67000, reach: 45000, impressions: 67000, clicks: 1200, engagement: 7.1 },
  { id: 7,  date: '2026-04-08', platform: 'instagram', accountId: 1, accountName: '@marca.es',     title: 'Lookbook Primavera disponible',        type: 'Carrusel', campaignId: 1, campaignName: 'Primavera 2026', productId: null, likes: 1680, comments: 98,  shares: 234, saves: 490, views: 0,     reach: 21000, impressions: 26800, clicks: 480, engagement: 5.7 },
  { id: 8,  date: '2026-04-06', platform: 'youtube',   accountId: 5, accountName: 'Marca Oficial', title: 'Unboxing: Colección Primavera 2026',   type: 'Vídeo',   campaignId: 1, campaignName: 'Primavera 2026', productId: null, likes: 892,  comments: 145, shares: 67,  saves: 0,    views: 18900, reach: 14200, impressions: 18900, clicks: 340, engagement: 5.3 },
  { id: 9,  date: '2026-04-04', platform: 'instagram', accountId: 1, accountName: '@marca.es',     title: 'Story exclusiva: primeras unidades',  type: 'Story',   campaignId: null, campaignName: null, productId: 2, likes: 0,    comments: 0,   shares: 0,   saves: 0,    views: 8900,  reach: 8900,  impressions: 8900, clicks: 145, engagement: 1.6 },
  { id: 10, date: '2026-04-02', platform: 'linkedin',  accountId: 6, accountName: 'Marca S.L.',    title: 'Crecemos: nuevas incorporaciones',     type: 'Imagen',  campaignId: null, campaignName: null, productId: null, likes: 234,  comments: 45,  shares: 78,  saves: 0,    views: 0,     reach: 3400,  impressions: 4200, clicks: 89, engagement: 6.7 },
]

// ── Campaigns ─────────────────────────────────────────────────────────────────
export const socialCampaigns = [
  {
    id: 1, name: 'Primavera 2026', objective: 'Conversiones', startDate: '2026-03-21', endDate: '2026-05-21',
    status: 'active', budget: 5000, posts: 12, influencers: 3,
    clicks: 8900, conversions: 312, sales: 14200,
    description: 'Campaña de lanzamiento de la colección Primavera-Verano 2026. Objetivo: aumentar ventas un 30% respecto al año anterior.',
    responsible: 'Laura Martínez',
    reach: 145000, impressions: 210000, engagement: 5.8, cost: 4200, roas: 3.38,
    timeline: [
      { date: '2026-03-21', event: 'Inicio campaña', type: 'milestone' },
      { date: '2026-04-01', event: 'Publicaciones influencers Ana García y Pablo Vidal', type: 'post' },
      { date: '2026-04-15', event: 'Reel viral 28K alcance', type: 'milestone' },
      { date: '2026-04-17', event: 'Revisión intermedia KPIs', type: 'review' },
    ]
  },
  {
    id: 2, name: 'Eco Collection', objective: 'Awareness', startDate: '2026-04-01', endDate: '2026-04-30',
    status: 'active', budget: 2000, posts: 8, influencers: 2,
    clicks: 3400, conversions: 89, sales: 3200,
    description: 'Campaña para dar a conocer la nueva línea de productos eco-friendly.',
    responsible: 'Carlos Ruiz',
    reach: 67000, impressions: 98000, engagement: 4.2, cost: 1600, roas: 2.0,
    timeline: [
      { date: '2026-04-01', event: 'Inicio campaña', type: 'milestone' },
      { date: '2026-04-10', event: 'Post viral en Twitter', type: 'milestone' },
    ]
  },
  {
    id: 3, name: 'Vuelta al Cole 2025', objective: 'Ventas', startDate: '2025-08-15', endDate: '2025-09-30',
    status: 'completed', budget: 3500, posts: 18, influencers: 4,
    clicks: 12400, conversions: 480, sales: 22000,
    description: 'Campaña de back-to-school con descuentos y colaboraciones con influencers educativos.',
    responsible: 'Laura Martínez',
    reach: 189000, impressions: 267000, engagement: 6.1, cost: 3480, roas: 6.32,
    timeline: []
  },
  {
    id: 4, name: 'Black Friday 2025', objective: 'Ventas', startDate: '2025-11-20', endDate: '2025-11-30',
    status: 'completed', budget: 6000, posts: 24, influencers: 6,
    clicks: 28900, conversions: 1240, sales: 58000,
    description: 'Campaña Black Friday con descuentos de hasta el 50%.',
    responsible: 'Laura Martínez',
    reach: 380000, impressions: 520000, engagement: 7.8, cost: 5800, roas: 10.0,
    timeline: []
  },
  {
    id: 5, name: 'Navidad 2025', objective: 'Conversiones', startDate: '2025-12-01', endDate: '2025-12-31',
    status: 'completed', budget: 4500, posts: 20, influencers: 5,
    clicks: 18600, conversions: 720, sales: 34000,
    description: 'Campaña navideña con guía de regalos y colaboraciones especiales.',
    responsible: 'Ana Torres',
    reach: 260000, impressions: 380000, engagement: 6.9, cost: 4320, roas: 7.87,
    timeline: []
  },
  {
    id: 6, name: 'Rebajas Verano 2026', objective: 'Tráfico', startDate: '2026-06-01', endDate: '2026-07-31',
    status: 'draft', budget: 3000, posts: 0, influencers: 0,
    clicks: 0, conversions: 0, sales: 0,
    description: 'Campaña de rebajas de verano. En planificación.',
    responsible: 'Laura Martínez',
    reach: 0, impressions: 0, engagement: 0, cost: 0, roas: 0,
    timeline: []
  },
]

// ── Influencers ────────────────────────────────────────────────────────────────
export const socialInfluencers = [
  {
    id: 1, name: 'Ana García', alias: '@analifestyle', photo: null,
    platform: 'instagram', platforms: ['instagram', 'tiktok'],
    followers: 85000, niche: 'Lifestyle', contact: 'ana@talentx.com', agency: 'TalentX',
    country: 'España', language: 'Español', status: 'active',
    collaborations: 3, salesGenerated: 8400, rating: 4.8,
    engagementMid: 4.2, reachMid: 42000, clicksMid: 980, conversionsMid: 48,
    contentQuality: 5, reliability: 4.5, brandAffinity: 5, reputationRisk: 1,
    notes: 'Excelente creadora, muy profesional. Recomendada para campañas de moda y lifestyle.',
  },
  {
    id: 2, name: 'Pablo Vidal', alias: '@pablovidal', photo: null,
    platform: 'instagram', platforms: ['instagram', 'youtube'],
    followers: 42000, niche: 'Moda masculina', contact: 'pablo@gmail.com', agency: null,
    country: 'España', language: 'Español', status: 'active',
    collaborations: 2, salesGenerated: 3200, rating: 4.2,
    engagementMid: 3.8, reachMid: 21000, clicksMid: 540, conversionsMid: 28,
    contentQuality: 4, reliability: 4, brandAffinity: 4.5, reputationRisk: 1,
    notes: 'Buen influencer para moda masculina. Cumple plazos.',
  },
  {
    id: 3, name: 'Marta Domínguez', alias: '@martamoda', photo: null,
    platform: 'tiktok', platforms: ['tiktok', 'instagram'],
    followers: 234000, niche: 'Moda', contact: 'marta@agencia-moda.com', agency: 'Moda Agency',
    country: 'España', language: 'Español', status: 'active',
    collaborations: 4, salesGenerated: 18600, rating: 4.6,
    engagementMid: 6.1, reachMid: 120000, clicksMid: 3400, conversionsMid: 180,
    contentQuality: 5, reliability: 5, brandAffinity: 4.5, reputationRisk: 1,
    notes: 'Top influencer en TikTok. Alta conversión. Precio elevado pero ROI excelente.',
  },
  {
    id: 4, name: 'Luis Fernández', alias: '@luisf_style', photo: null,
    platform: 'instagram', platforms: ['instagram'],
    followers: 18000, niche: 'Streetwear', contact: 'luisf@outlook.com', agency: null,
    country: 'España', language: 'Español', status: 'prospect',
    collaborations: 0, salesGenerated: 0, rating: 0,
    engagementMid: 5.4, reachMid: 9000, clicksMid: 240, conversionsMid: 0,
    contentQuality: 3.5, reliability: 0, brandAffinity: 3, reputationRisk: 2,
    notes: 'Perfil interesante para streetwear. Pendiente primer contacto.',
  },
  {
    id: 5, name: 'Sofía Ramírez', alias: '@sofiabeauty', photo: null,
    platform: 'instagram', platforms: ['instagram', 'youtube', 'tiktok'],
    followers: 156000, niche: 'Belleza', contact: 'sofia@starmanagement.com', agency: 'Star Management',
    country: 'España', language: 'Español', status: 'archived',
    collaborations: 1, salesGenerated: 1200, rating: 2.8,
    engagementMid: 2.1, reachMid: 45000, clicksMid: 300, conversionsMid: 12,
    contentQuality: 3, reliability: 2, brandAffinity: 2.5, reputationRisk: 4,
    notes: 'Archivada. No cumplió entregables en la colaboración de Navidad.',
  },
  {
    id: 6, name: 'Elena Vega', alias: '@elenavegafit', photo: null,
    platform: 'instagram', platforms: ['instagram', 'youtube'],
    followers: 67000, niche: 'Fitness', contact: 'elena@fit-agency.com', agency: 'FitAgency',
    country: 'España', language: 'Español', status: 'active',
    collaborations: 2, salesGenerated: 4800, rating: 4.4,
    engagementMid: 4.8, reachMid: 32000, clicksMid: 780, conversionsMid: 42,
    contentQuality: 4.5, reliability: 4.5, brandAffinity: 4, reputationRisk: 1,
    notes: 'Buena para campañas de ropa deportiva y lifestyle activo.',
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
    deliverables: '1 Reel (60s), 3 Stories con swipe up, mención en bio durante 7 días',
    reach: 67000, impressions: 89000, views: 0, likes: 3400, comments: 187, shares: 240,
    evidences: ['captura_reel.jpg', 'captura_story1.jpg'],
    expectedReach: 60000, expectedClicks: 2000, expectedConversions: 100,
    observations: 'Resultados por encima de lo esperado. Excelente colaboración.',
    recommendation: 'Renovar para próxima campaña',
  },
  {
    id: 2, influencerId: 2, influencerName: 'Pablo Vidal', influencerAlias: '@pablovidal',
    campaignId: 1, campaignName: 'Primavera 2026',
    format: 'Post + 2 Stories', publishDate: '2026-04-08', cost: 800,
    linkId: 2, code: 'PABLO10',
    status: 'completed',
    clicks: 890, conversions: 42, sales: 1680,
    deliverables: '1 post carrusel, 2 stories con enlace',
    reach: 28000, impressions: 34000, views: 0, likes: 1240, comments: 67, shares: 89,
    evidences: ['captura_post.jpg'],
    expectedReach: 30000, expectedClicks: 1000, expectedConversions: 50,
    observations: 'Resultados ligeramente por debajo del objetivo.',
    recommendation: 'Revisar briefing antes de próxima colaboración',
  },
  {
    id: 3, influencerId: 3, influencerName: 'Marta Domínguez', influencerAlias: '@martamoda',
    campaignId: 1, campaignName: 'Primavera 2026',
    format: '2 TikToks + Dueto', publishDate: '2026-04-10', cost: 2400,
    linkId: 3, code: 'MARTA20',
    status: 'active',
    clicks: 4200, conversions: 0, sales: 0,
    deliverables: '2 TikToks de 60s, 1 dueto con cuenta oficial',
    reach: 0, impressions: 0, views: 89000, likes: 0, comments: 0, shares: 0,
    evidences: [],
    expectedReach: 0, expectedClicks: 5000, expectedConversions: 200,
    observations: 'Primer TikTok publicado. Segundo pendiente.',
    recommendation: '',
  },
  {
    id: 4, influencerId: 6, influencerName: 'Elena Vega', influencerAlias: '@elenavegafit',
    campaignId: 2, campaignName: 'Eco Collection',
    format: 'Post + Story', publishDate: '2026-04-12', cost: 900,
    linkId: 4, code: 'ELENA10',
    status: 'completed',
    clicks: 1200, conversions: 58, sales: 2400,
    deliverables: '1 post imagen, 1 story con enlace',
    reach: 38000, impressions: 45000, views: 0, likes: 1890, comments: 89, shares: 120,
    evidences: ['captura_eco_post.jpg'],
    expectedReach: 35000, expectedClicks: 1000, expectedConversions: 50,
    observations: 'Muy buenos resultados para campaña de awareness.',
    recommendation: 'Continuar colaboración',
  },
  {
    id: 5, influencerId: 1, influencerName: 'Ana García', influencerAlias: '@analifestyle',
    campaignId: 5, campaignName: 'Navidad 2025',
    format: 'Reel + 5 Stories', publishDate: '2025-12-10', cost: 2000,
    linkId: 5, code: 'ANAXMAS',
    status: 'completed',
    clicks: 3400, conversions: 167, sales: 7800,
    deliverables: '1 Reel navideño, 5 stories con countdowns y links',
    reach: 78000, impressions: 102000, views: 0, likes: 4200, comments: 234, shares: 380,
    evidences: ['captura_navidad_reel.jpg', 'captura_navidad_stories.jpg'],
    expectedReach: 70000, expectedClicks: 3000, expectedConversions: 150,
    observations: 'Excelente rendimiento navideño. Top colaboración del año.',
    recommendation: 'Colaboración prioritaria para próximas campañas',
  },
]

// ── Links ─────────────────────────────────────────────────────────────────────
export const socialLinks = [
  { id: 1, name: 'Bio Link Ana García - Primavera', url: 'https://mystore.es/primavera-2026', campaignId: 1, campaignName: 'Primavera 2026', origin: 'instagram', influencerId: 1, influencerName: 'Ana García', utmSource: 'instagram', utmMedium: 'influencer', utmCampaign: 'primavera2026', utmContent: 'ana-garcia', clicks: 2800, sessions: 2540, carts: 580, purchases: 134, revenue: 5600, conversion: 5.28 },
  { id: 2, name: 'Bio Link Pablo - Primavera',       url: 'https://mystore.es/primavera-2026', campaignId: 1, campaignName: 'Primavera 2026', origin: 'instagram', influencerId: 2, influencerName: 'Pablo Vidal',  utmSource: 'instagram', utmMedium: 'influencer', utmCampaign: 'primavera2026', utmContent: 'pablo-vidal', clicks: 890,  sessions: 780,  carts: 145, purchases: 42,  revenue: 1680, conversion: 5.38 },
  { id: 3, name: 'Link TikTok Marta - Primavera',    url: 'https://mystore.es/primavera-2026', campaignId: 1, campaignName: 'Primavera 2026', origin: 'tiktok',    influencerId: 3, influencerName: 'Marta Domínguez', utmSource: 'tiktok', utmMedium: 'influencer', utmCampaign: 'primavera2026', utmContent: 'marta-moda', clicks: 4200, sessions: 3800, carts: 820, purchases: 0,   revenue: 0,    conversion: 0 },
  { id: 4, name: 'Bio Link Elena - Eco',             url: 'https://mystore.es/eco-collection', campaignId: 2, campaignName: 'Eco Collection', origin: 'instagram', influencerId: 6, influencerName: 'Elena Vega',   utmSource: 'instagram', utmMedium: 'influencer', utmCampaign: 'ecocollection', utmContent: 'elena-vega', clicks: 1200, sessions: 1050, carts: 210, purchases: 58,  revenue: 2400, conversion: 5.52 },
  { id: 5, name: 'Link General Primavera (Bio)',      url: 'https://mystore.es/primavera-2026', campaignId: 1, campaignName: 'Primavera 2026', origin: 'instagram', influencerId: null, influencerName: null, utmSource: 'instagram', utmMedium: 'organic', utmCampaign: 'primavera2026', utmContent: 'bio', clicks: 1340, sessions: 1200, carts: 290, purchases: 89, revenue: 3780, conversion: 7.42 },
  { id: 6, name: 'Link Twitter Eco',                 url: 'https://mystore.es/eco-collection', campaignId: 2, campaignName: 'Eco Collection', origin: 'twitter',   influencerId: null, influencerName: null, utmSource: 'twitter', utmMedium: 'organic', utmCampaign: 'ecocollection', utmContent: 'tweet', clicks: 680, sessions: 580, carts: 89, purchases: 24, revenue: 980, conversion: 4.14 },
]

// ── Alerts ────────────────────────────────────────────────────────────────────
export const socialAlerts = [
  { id: 1, date: '2026-04-17', type: 'reach_drop',        entity: 'Cuenta Facebook @Marca España',         severity: 'high',   status: 'pending',  responsible: null,           description: 'Caída del 35% en alcance en las últimas 48h. Token posiblemente caducado.' },
  { id: 2, date: '2026-04-17', type: 'missing_metrics',   entity: 'Colaboración: Marta Domínguez #3',       severity: 'medium', status: 'pending',  responsible: 'Laura Martínez', description: 'Segundo TikTok publicado pero sin métricas cargadas después de 72h.' },
  { id: 3, date: '2026-04-16', type: 'broken_link',       entity: 'Enlace: Bio Link General Primavera',     severity: 'high',   status: 'reviewed', responsible: 'Carlos Ruiz',  description: 'El enlace devuelve 404. Verificar URL de destino.' },
  { id: 4, date: '2026-04-15', type: 'low_campaign',      entity: 'Campaña: Eco Collection',                severity: 'medium', status: 'assigned', responsible: 'Carlos Ruiz',  description: 'Conversión por debajo del 2% objetivo. Revisar creatividades.' },
  { id: 5, date: '2026-04-14', type: 'negative_comments', entity: 'Post: "Tendencias outfit verano 2026"',  severity: 'low',    status: 'reviewed', responsible: 'Laura Martínez', description: '12 comentarios negativos sobre tallas. Monitorizar.' },
  { id: 6, date: '2026-04-13', type: 'unvalidated_data',  entity: 'Métricas: Colaboración Pablo Vidal #2',  severity: 'low',    status: 'pending',  responsible: null,           description: 'Datos introducidos manualmente sin validar por supervisor.' },
  { id: 7, date: '2026-04-12', type: 'high_cost',         entity: 'Colaboración: Marta Domínguez #3',       severity: 'medium', status: 'assigned', responsible: 'Laura Martínez', description: 'Coste/conversión actualmente ∞. Esperando segundo TikTok.' },
]

// ── Manual Metrics Upload history ─────────────────────────────────────────────
export const metricsHistory = [
  { id: 1, date: '2026-04-14', influencerName: 'Marta Domínguez', collaborationId: 3, publicationDesc: 'TikTok #1 - Primavera', uploadedBy: 'Laura Martínez', status: 'validated', reach: 45000, impressions: 67000, views: 89000, likes: 5400, comments: 234, shares: 890 },
  { id: 2, date: '2026-04-12', influencerName: 'Pablo Vidal',    collaborationId: 2, publicationDesc: 'Post Carrusel - Primavera', uploadedBy: 'Carlos Ruiz',   status: 'pending',   reach: 28000, impressions: 34000, views: 0,     likes: 1240, comments: 67,  shares: 89 },
  { id: 3, date: '2026-04-11', influencerName: 'Elena Vega',     collaborationId: 4, publicationDesc: 'Post Eco Collection',      uploadedBy: 'Laura Martínez', status: 'validated', reach: 38000, impressions: 45000, views: 0,     likes: 1890, comments: 89,  shares: 120 },
]

// ── KPI Summary (Dashboard) ───────────────────────────────────────────────────
export const dashboardKPIs = {
  totalFollowers:      { value: 105700, change: +3.4, label: 'Seguidores totales' },
  totalReach:          { value: 212000, change: +8.2, label: 'Alcance total' },
  avgEngagement:       { value: 5.3,    change: +0.4, label: 'Engagement medio (%)' },
  totalClicks:         { value: 12400,  change: +15.1, label: 'Clics totales' },
  totalConversions:    { value: 401,    change: +22.3, label: 'Conversiones' },
  attributedSales:     { value: 17400,  change: +18.7, label: 'Ventas atribuidas (€)' },
  activeCollaborations:{ value: 2,      change: 0,     label: 'Colaboraciones activas' },
}

export const evolutionData = {
  labels: ['Ene', 'Feb', 'Mar', 'Abr'],
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

export function formatNumber(n) {
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M'
  if (n >= 1000) return (n / 1000).toFixed(1) + 'K'
  return String(n)
}

export function formatCurrency(n) {
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(n)
}

export function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric' })
}
