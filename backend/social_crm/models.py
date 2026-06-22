"""
Social CRM — schema normalitzat (3NF).

Principis de disseny:
  - Company és el tenant anchor de totes les entitats.
  - Els totals de campanya (reach, impressions, conversions…) mai es guarden
    directament a Campaign: sempre es deriven de SocialPost + Collaboration +
    PaidAdSet per evitar inconsistències.
  - Les mètriques de col·laboració s'introdueixen manualment per publicació
    (CollaborationPublication) i s'agreguen a Collaboration.actual_* per
    lectura ràpida. Els clics/conversions/vendes vénen de TrackedLink.
  - Les mètriques de les comptes de xarxa social es capturen diàriament a
    SocialAccountSnapshot per poder traçar l'evolució en el temps.
  - Les alertes referencien l'entitat que les ha generat via FK nullable;
    un CHECK constraint de BD garanteix que com a mínim una FK és no nul·la.
"""

from __future__ import annotations

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


# ── TextChoices ───────────────────────────────────────────────────────────────


class Platform(models.TextChoices):
    INSTAGRAM = 'instagram', 'Instagram'
    TIKTOK    = 'tiktok',    'TikTok'
    TWITTER   = 'twitter',   'Twitter/X'
    FACEBOOK  = 'facebook',  'Facebook'
    YOUTUBE   = 'youtube',   'YouTube'
    LINKEDIN  = 'linkedin',  'LinkedIn'


class AdPlatform(models.TextChoices):
    FACEBOOK  = 'facebook',  'Meta Ads'
    GOOGLE    = 'google',    'Google Ads'
    TIKTOK    = 'tiktok',    'TikTok Ads'
    INSTAGRAM = 'instagram', 'Instagram Ads'


class PostContentType(models.TextChoices):
    IMAGE    = 'image',    'Imatge'
    VIDEO    = 'video',    'Vídeo'
    REEL     = 'reel',     'Reel'
    STORY    = 'story',    'Story'
    CAROUSEL = 'carousel', 'Carrusel'
    TWEET    = 'tweet',    'Tweet'
    THREAD   = 'thread',   'Fil'
    SHORT    = 'short',    'Short'


class CampaignObjective(models.TextChoices):
    AWARENESS   = 'awareness',   'Awareness'
    TRAFFIC     = 'traffic',     'Trànsit'
    CONVERSIONS = 'conversions', 'Conversions'
    ENGAGEMENT  = 'engagement',  'Engagement'
    SALES       = 'sales',       'Vendes'
    LEADS       = 'leads',       'Leads'


class CampaignStatus(models.TextChoices):
    DRAFT     = 'draft',     'Esborrany'
    ACTIVE    = 'active',    'Activa'
    PAUSED    = 'paused',    'Pausada'
    COMPLETED = 'completed', 'Completada'


class CampaignChannel(models.TextChoices):
    OWNED       = 'owned',       'Comptes propis'
    INFLUENCERS = 'influencers', 'Influencers'
    PAID        = 'paid',        'Anuncis de pagament'


class CampaignMetricKey(models.TextChoices):
    REACH       = 'reach',       'Abast objectiu'
    CLICKS      = 'clicks',      'Clics objectiu'
    CONVERSIONS = 'conversions', 'Conversions objectiu'
    SALES       = 'sales',       'Vendes objectiu (€)'


class TimelineEventType(models.TextChoices):
    MILESTONE = 'milestone', 'Fita'
    POST      = 'post',      'Publicació'
    REVIEW    = 'review',    'Revisió'


class InfluencerStatus(models.TextChoices):
    ACTIVE   = 'active',   'Actiu'
    PROSPECT = 'prospect', 'Prospecte'
    ARCHIVED = 'archived', 'Arxivat'


class CollaborationStatus(models.TextChoices):
    DRAFT     = 'draft',     'Esborrany'
    PENDING   = 'pending',   'Pendent'
    ACTIVE    = 'active',    'Activa'
    COMPLETED = 'completed', 'Completada'
    CANCELLED = 'cancelled', 'Cancel·lada'


class AlertType(models.TextChoices):
    REACH_DROP        = 'reach_drop',        "Caiguda d'abast"
    BROKEN_LINK       = 'broken_link',       'Enllaç trencat'
    LOW_CAMPAIGN      = 'low_campaign',      'Campanya amb baix rendiment'
    NEGATIVE_COMMENTS = 'negative_comments', 'Molts comentaris negatius'
    MISSING_METRICS   = 'missing_metrics',   'Mètriques pendents'
    HIGH_COST         = 'high_cost',         'Cost alt sense conversió'
    UNVALIDATED_DATA  = 'unvalidated_data',  'Dada manual sense validar'


class AlertSeverity(models.TextChoices):
    LOW    = 'low',    'Baixa'
    MEDIUM = 'medium', 'Mitja'
    HIGH   = 'high',   'Alta'


class AlertStatus(models.TextChoices):
    PENDING  = 'pending',  'Pendent'
    ASSIGNED = 'assigned', 'Assignada'
    REVIEWED = 'reviewed', 'Revisada'
    RESOLVED = 'resolved', 'Resolta'


class MetricsEntryStatus(models.TextChoices):
    PENDING   = 'pending',   'Pendent de validació'
    VALIDATED = 'validated', 'Validada'


class AccountStatus(models.TextChoices):
    CONNECTED    = 'connected',    'Connectat'
    DISCONNECTED = 'disconnected', 'Desconnectat'
    ERROR        = 'error',        'Error'


# ── Abstract base ─────────────────────────────────────────────────────────────


class TenantModel(models.Model):
    """Abstract base que afegeix la FK de tenant (Company) a cada model."""

    company = models.ForeignKey(
        'accounts.Company',
        on_delete=models.CASCADE,
        db_index=True,
    )

    class Meta:
        abstract = True


# ── 1. Social Accounts ────────────────────────────────────────────────────────


class SocialAccount(TenantModel):
    """
    Un compte de xarxa social propietat de l'empresa.
    Un registre per compte i plataforma.
    """

    platform    = models.CharField(max_length=20, choices=Platform.choices)
    name        = models.CharField(max_length=200)
    username    = models.CharField(max_length=100)
    status      = models.CharField(
        max_length=20, choices=AccountStatus.choices, default=AccountStatus.CONNECTED,
    )
    followers   = models.PositiveIntegerField(default=0)
    posts_count = models.PositiveIntegerField(default=0)
    responsible = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='managed_social_accounts',
    )
    observations   = models.TextField(blank=True, default='')
    last_synced_at = models.DateTimeField(null=True, blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        db_table       = 'social_crm_socialaccount'
        unique_together = [('company', 'platform', 'username')]
        ordering        = ['platform', 'name']
        indexes = [
            models.Index(fields=['company', 'platform']),
            models.Index(fields=['company', 'status']),
        ]

    def __str__(self):
        return f'{self.get_platform_display()} · {self.username}'


class SocialAccountSnapshot(models.Model):
    """
    Instantània diària de les mètriques d'un SocialAccount.
    Permet construir el gràfic d'evolució de seguidors al llarg del temps.
    No hereta TenantModel: la Company s'infereix via account.company.
    """

    account         = models.ForeignKey(SocialAccount, on_delete=models.CASCADE, related_name='snapshots')
    snapshot_date   = models.DateField()
    followers       = models.PositiveIntegerField()
    posts_count     = models.PositiveIntegerField(default=0)
    avg_engagement_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    avg_reach       = models.PositiveIntegerField(null=True, blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table        = 'social_crm_socialaccountsnapshot'
        unique_together = [('account', 'snapshot_date')]
        ordering        = ['account', '-snapshot_date']
        indexes = [
            models.Index(fields=['account', 'snapshot_date']),
        ]

    def __str__(self):
        return f'{self.account} · {self.snapshot_date}'


# ── 2. Campaigns ──────────────────────────────────────────────────────────────


class Campaign(TenantModel):
    """
    Campanya de màrqueting. Els totals (reach, impressions, conversions…)
    SEMPRE es deriven en temps de consulta a partir de SocialPost +
    Collaboration + PaidAdSet. Aquí només es guarden el pressupost, les
    dates, la descripció i els KPI objectiu.
    """

    name         = models.CharField(max_length=200)
    objective    = models.CharField(max_length=20, choices=CampaignObjective.choices)
    status       = models.CharField(
        max_length=20, choices=CampaignStatus.choices, default=CampaignStatus.DRAFT,
    )
    start_date   = models.DateField(null=True, blank=True)
    end_date     = models.DateField(null=True, blank=True)
    total_budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    description  = models.TextField(blank=True, default='')
    responsible  = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='managed_campaigns',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'social_crm_campaign'
        ordering = ['-start_date', 'name']
        indexes = [
            models.Index(fields=['company', 'status']),
            models.Index(fields=['company', 'start_date', 'end_date']),
        ]
        constraints = [
            models.CheckConstraint(
                name='campaign_end_gte_start',
                check=(
                    models.Q(end_date__isnull=True)
                    | models.Q(start_date__isnull=True)
                    | models.Q(end_date__gte=models.F('start_date'))
                ),
            ),
        ]

    def __str__(self):
        return self.name


class CampaignChannelBudget(models.Model):
    """
    Pressupost planificat per canal dins d'una campanya.
    Un registre per parell (campanya, canal) — restricció d'unicitat enforçada.
    No hereta TenantModel perquè la Company s'infereix via campaign.company.
    """

    campaign      = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='channel_budgets')
    channel       = models.CharField(max_length=20, choices=CampaignChannel.choices)
    budget_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        db_table        = 'social_crm_campaignchannelbudget'
        unique_together = [('campaign', 'channel')]

    def __str__(self):
        return f'{self.campaign} · {self.channel}: {self.budget_amount}'


class CampaignTarget(models.Model):
    """
    Objectiu KPI per a una mètrica específica dins d'una campanya.
    Un registre per parell (campanya, mètrica).
    """

    campaign     = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='targets')
    metric_key   = models.CharField(max_length=20, choices=CampaignMetricKey.choices)
    target_value = models.DecimalField(max_digits=14, decimal_places=2)

    class Meta:
        db_table        = 'social_crm_campaigntarget'
        unique_together = [('campaign', 'metric_key')]

    def __str__(self):
        return f'{self.campaign} · {self.metric_key}: {self.target_value}'


class CampaignTimelineEvent(models.Model):
    """
    Un esdeveniment notable a la línia de temps d'una campanya
    (llançament, publicació viral, revisió de KPI…).
    """

    campaign   = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='timeline_events')
    event_date = models.DateField()
    description = models.CharField(max_length=500)
    event_type  = models.CharField(
        max_length=20, choices=TimelineEventType.choices, default=TimelineEventType.MILESTONE,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'social_crm_campaigntimelineevent'
        ordering = ['event_date']

    def __str__(self):
        return f'{self.campaign} · {self.event_date}: {self.description[:50]}'


# ── 3. Influencers ────────────────────────────────────────────────────────────


class Influencer(TenantModel):
    """
    Creador de contingut extern amb qui l'empresa pot col·laborar.
    primary_platform és el seu canal principal; InfluencerPlatformPresence
    guarda el detall per plataforma (username, seguidors, mètriques mitjanes).
    """

    name             = models.CharField(max_length=200)
    alias            = models.CharField(max_length=100, help_text='@handle principal')
    photo            = models.ImageField(upload_to='influencers/', null=True, blank=True)
    primary_platform = models.CharField(max_length=20, choices=Platform.choices)
    niche            = models.CharField(max_length=100, blank=True, default='')
    contact_email    = models.EmailField(blank=True, default='')
    agency_name      = models.CharField(max_length=200, blank=True, default='')
    country          = models.CharField(max_length=100, blank=True, default='')
    language         = models.CharField(max_length=50, blank=True, default='')
    status           = models.CharField(
        max_length=20, choices=InfluencerStatus.choices, default=InfluencerStatus.PROSPECT,
    )
    # Puntuacions d'avaluació (0–5)
    score_content_quality = models.DecimalField(
        max_digits=3, decimal_places=1, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )
    score_reliability = models.DecimalField(
        max_digits=3, decimal_places=1, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )
    score_brand_affinity = models.DecimalField(
        max_digits=3, decimal_places=1, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )
    score_reputation_risk = models.DecimalField(
        max_digits=3, decimal_places=1, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )
    notes      = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'social_crm_influencer'
        ordering = ['name']
        indexes = [
            models.Index(fields=['company', 'status']),
            models.Index(fields=['company', 'primary_platform']),
        ]

    def __str__(self):
        return f'{self.alias} ({self.name})'


class InfluencerPlatformPresence(models.Model):
    """
    Presència d'un influencer en una plataforma concreta.
    Guarda username, seguidors actuals i mètriques mitjanes observades,
    de manera que el sistema pugui estimar resultats esperats sense esperar
    dades reals.
    """

    influencer          = models.ForeignKey(Influencer, on_delete=models.CASCADE, related_name='platform_presences')
    platform            = models.CharField(max_length=20, choices=Platform.choices)
    username            = models.CharField(max_length=100)
    followers           = models.PositiveIntegerField(default=0)
    avg_engagement_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    avg_reach           = models.PositiveIntegerField(null=True, blank=True)
    avg_clicks          = models.PositiveIntegerField(null=True, blank=True)
    avg_conversions     = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        db_table        = 'social_crm_influencerplatformpresence'
        unique_together = [('influencer', 'platform')]
        ordering        = ['influencer', 'platform']

    def __str__(self):
        return f'{self.influencer.alias} @ {self.platform}'


# ── 4. Social Posts ───────────────────────────────────────────────────────────


class SocialPost(TenantModel):
    """
    Una publicació a un compte de xarxa social.
    La columna `platform` és una denormalització de account.platform per
    permetre filtres per plataforma sense JOIN addicional.
    """

    account      = models.ForeignKey(SocialAccount, on_delete=models.PROTECT, related_name='posts')
    campaign     = models.ForeignKey(
        Campaign, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts',
    )
    product      = models.ForeignKey(
        'products.Product', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='social_posts',
    )
    # Denormalitzat de account.platform per rendiment de consultes
    platform     = models.CharField(max_length=20, choices=Platform.choices)
    title        = models.CharField(max_length=500)
    content_type = models.CharField(max_length=20, choices=PostContentType.choices)
    published_at = models.DateField()
    url          = models.URLField(max_length=500, blank=True, default='')
    # Mètriques d'engagement
    likes        = models.PositiveIntegerField(default=0)
    comments     = models.PositiveIntegerField(default=0)
    shares       = models.PositiveIntegerField(default=0)
    saves        = models.PositiveIntegerField(default=0)
    views        = models.PositiveIntegerField(default=0)
    reach        = models.PositiveIntegerField(default=0)
    impressions  = models.PositiveIntegerField(default=0)
    clicks       = models.PositiveIntegerField(default=0)
    # engagement_rate = (interaccions / abast) * 100; es guarda per filtrar
    engagement_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'social_crm_socialpost'
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['company', 'published_at']),
            models.Index(fields=['company', 'platform', 'published_at']),
            models.Index(fields=['campaign', 'published_at']),
        ]

    def __str__(self):
        return f'{self.platform} · {self.published_at}: {self.title[:60]}'


# ── 5. Collaborations ─────────────────────────────────────────────────────────


class Collaboration(TenantModel):
    """
    Col·laboració d'influencer màrqueting dins d'una campanya.
    Vincula una Campaign i un Influencer.

    Les mètriques orgàniques (reach, impressions…) s'introdueixen manualment
    per publicació (CollaborationPublication) i s'agreguen aquí (actual_*)
    per lectura ràpida via recalculate_actuals().

    Clics, conversions i vendes NO es guarden aquí: vénen del TrackedLink
    associat, evitant duplicació de dades.
    """

    campaign          = models.ForeignKey(Campaign, on_delete=models.PROTECT, related_name='collaborations')
    influencer        = models.ForeignKey(Influencer, on_delete=models.PROTECT, related_name='collaborations')
    # Plataforma concreta d'aquest influencer per a aquesta col·laboració
    platform_presence = models.ForeignKey(
        InfluencerPlatformPresence,
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='collaborations',
        help_text='Plataforma de l\'influencer usada en aquesta col·laboració.',
    )
    content_format            = models.CharField(max_length=200)
    publish_date              = models.DateField(null=True, blank=True)
    agreed_cost               = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_code             = models.CharField(max_length=50, blank=True, default='')
    status                    = models.CharField(
        max_length=20, choices=CollaborationStatus.choices, default=CollaborationStatus.DRAFT,
    )
    deliverables_description  = models.TextField(blank=True, default='')
    # KPI esperats (objectius contractuals / estimats)
    expected_reach       = models.PositiveIntegerField(default=0)
    expected_clicks      = models.PositiveIntegerField(default=0)
    expected_conversions = models.PositiveIntegerField(default=0)
    # Mètriques orgàniques agregades (suma de CollaborationPublication)
    actual_reach       = models.PositiveIntegerField(default=0)
    actual_impressions = models.PositiveIntegerField(default=0)
    actual_views       = models.PositiveIntegerField(default=0)
    actual_likes       = models.PositiveIntegerField(default=0)
    actual_comments    = models.PositiveIntegerField(default=0)
    actual_shares      = models.PositiveIntegerField(default=0)
    observations  = models.TextField(blank=True, default='')
    recommendation = models.TextField(blank=True, default='')
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'social_crm_collaboration'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company', 'status']),
            models.Index(fields=['campaign', 'influencer']),
        ]

    def __str__(self):
        return f'{self.campaign.name} × {self.influencer.alias}'

    def recalculate_actuals(self) -> None:
        """Recalcula actual_* a partir de les publicacions."""
        from django.db.models import Sum

        agg = self.publications.aggregate(
            r=Sum('reach'), im=Sum('impressions'), vi=Sum('views'),
            li=Sum('likes'), co=Sum('comments'), sh=Sum('shares'),
        )
        self.actual_reach       = agg['r']  or 0
        self.actual_impressions = agg['im'] or 0
        self.actual_views       = agg['vi'] or 0
        self.actual_likes       = agg['li'] or 0
        self.actual_comments    = agg['co'] or 0
        self.actual_shares      = agg['sh'] or 0
        self.save(update_fields=[
            'actual_reach', 'actual_impressions', 'actual_views',
            'actual_likes', 'actual_comments', 'actual_shares',
        ])


class CollaborationPublication(models.Model):
    """
    Una peça de contingut lliurada dins d'una col·laboració.
    Una col·laboració pot requerir múltiples publicacions
    (p. ex., "2 TikToks + 1 Duet"). Les mètriques s'introdueixen manualment
    i requereixen validació; l'agregat s'escriu a Collaboration.actual_*.
    """

    collaboration    = models.ForeignKey(Collaboration, on_delete=models.CASCADE, related_name='publications')
    content_type     = models.CharField(max_length=20, choices=PostContentType.choices)
    description      = models.CharField(max_length=300, blank=True, default='')
    publication_date = models.DateField(null=True, blank=True)
    url              = models.URLField(max_length=500, blank=True, default='')
    # Mètriques introduïdes manualment
    reach       = models.PositiveIntegerField(default=0)
    impressions = models.PositiveIntegerField(default=0)
    views       = models.PositiveIntegerField(default=0)
    likes       = models.PositiveIntegerField(default=0)
    comments    = models.PositiveIntegerField(default=0)
    shares      = models.PositiveIntegerField(default=0)
    # Traçabilitat de l'entrada de dades
    metrics_status = models.CharField(
        max_length=20, choices=MetricsEntryStatus.choices, default=MetricsEntryStatus.PENDING,
    )
    uploaded_by  = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='uploaded_publications',
    )
    validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='validated_publications',
    )
    uploaded_at  = models.DateTimeField(null=True, blank=True)
    validated_at = models.DateTimeField(null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'social_crm_collaborationpublication'
        ordering = ['collaboration', 'publication_date']

    def __str__(self):
        return f'{self.collaboration} · {self.content_type} · {self.publication_date or "—"}'


class CollaborationEvidence(models.Model):
    """
    Arxius de prova (captures de pantalla, exports) adjunts a una col·laboració.
    """

    collaboration = models.ForeignKey(Collaboration, on_delete=models.CASCADE, related_name='evidences')
    file          = models.FileField(upload_to='collab_evidences/')
    label         = models.CharField(max_length=200, blank=True, default='')
    uploaded_at   = models.DateTimeField(auto_now_add=True)
    uploaded_by   = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='uploaded_evidences',
    )

    class Meta:
        db_table = 'social_crm_collaborationevidence'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'{self.collaboration} · {self.label or self.file.name}'


# ── 6. Tracked Links ──────────────────────────────────────────────────────────


class TrackedLink(TenantModel):
    """
    Enllaç amb UTM per atribuir trànsit i conversions a una campanya, canal o
    col·laboració concreta. Un registre = una combinació UTM única.

    Clics, sessions, cistelles, compres i ingressos s'actualitzen per sincronització
    amb la plataforma d'analítica o entrada manual. Aquests valors fan de "font
    de veritat" per als KPI de conversió d'una col·laboració.
    """

    campaign      = models.ForeignKey(
        Campaign, on_delete=models.SET_NULL, null=True, blank=True, related_name='tracked_links',
    )
    collaboration = models.ForeignKey(
        Collaboration, on_delete=models.SET_NULL, null=True, blank=True, related_name='tracked_links',
    )
    name              = models.CharField(max_length=300)
    destination_url   = models.URLField(max_length=2000)
    origin_platform   = models.CharField(max_length=20, choices=Platform.choices, blank=True, default='')
    utm_source        = models.CharField(max_length=100)
    utm_medium        = models.CharField(max_length=100)
    utm_campaign      = models.CharField(max_length=200)
    utm_content       = models.CharField(max_length=200, blank=True, default='')
    utm_term          = models.CharField(max_length=200, blank=True, default='')
    is_active         = models.BooleanField(default=True)
    # Mètriques d'atribució agregades
    clicks    = models.PositiveIntegerField(default=0)
    sessions  = models.PositiveIntegerField(default=0)
    carts     = models.PositiveIntegerField(default=0)
    purchases = models.PositiveIntegerField(default=0)
    revenue   = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'social_crm_trackedlink'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company', 'campaign']),
            models.Index(fields=['utm_source', 'utm_medium', 'utm_campaign']),
        ]

    def __str__(self):
        return self.name

    @property
    def conversion_rate(self) -> float:
        return round(self.purchases / self.clicks * 100, 2) if self.clicks else 0.0


# ── 7. Paid Ad Sets ───────────────────────────────────────────────────────────


class PaidAdSet(TenantModel):
    """
    Conjunt d'anuncis actiu en una plataforma de publicitat de pagament,
    associat a una campanya. Les mètriques arriben automàticament per API
    de la plataforma d'anuncis (font: 'auto').
    """

    campaign      = models.ForeignKey(Campaign, on_delete=models.PROTECT, related_name='ad_sets')
    ad_platform   = models.CharField(max_length=20, choices=AdPlatform.choices)
    name          = models.CharField(max_length=300)
    status        = models.CharField(
        max_length=20, choices=CampaignStatus.choices, default=CampaignStatus.ACTIVE,
    )
    start_date    = models.DateField(null=True, blank=True)
    end_date      = models.DateField(null=True, blank=True)
    budget_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    spend_amount  = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    impressions   = models.PositiveIntegerField(default=0)
    clicks        = models.PositiveIntegerField(default=0)
    conversions   = models.PositiveIntegerField(default=0)
    sales_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'social_crm_paidadset'
        ordering = ['-start_date', 'name']
        indexes = [
            models.Index(fields=['campaign', 'ad_platform']),
            models.Index(fields=['company', 'status']),
        ]
        constraints = [
            models.CheckConstraint(
                name='adset_end_gte_start',
                check=(
                    models.Q(end_date__isnull=True)
                    | models.Q(start_date__isnull=True)
                    | models.Q(end_date__gte=models.F('start_date'))
                ),
            ),
        ]

    def __str__(self):
        return f'{self.campaign.name} · {self.get_ad_platform_display()}: {self.name}'

    @property
    def ctr(self) -> float:
        return round(self.clicks / self.impressions * 100, 2) if self.impressions else 0.0

    @property
    def cpc(self) -> float:
        return round(float(self.spend_amount) / self.clicks, 4) if self.clicks else 0.0

    @property
    def cpa(self) -> float:
        return round(float(self.spend_amount) / self.conversions, 4) if self.conversions else 0.0

    @property
    def roas(self) -> float:
        return round(float(self.sales_revenue) / float(self.spend_amount), 4) if self.spend_amount else 0.0


# ── 8. Alerts ─────────────────────────────────────────────────────────────────


class Alert(TenantModel):
    """
    Alerta del sistema o creada manualment que assenyala un problema que
    requereix atenció. Es vincula a l'entitat que l'ha generada via una de les
    FK nullable: social_account, tracked_link, campaign, post o collaboration.

    Un CHECK constraint de BD garanteix que com a mínim una FK és no nul·la,
    de manera que cap alerta quedi "flotant" sense referència.
    """

    alert_date  = models.DateField()
    alert_type  = models.CharField(max_length=30, choices=AlertType.choices)
    severity    = models.CharField(
        max_length=10, choices=AlertSeverity.choices, default=AlertSeverity.MEDIUM,
    )
    status      = models.CharField(
        max_length=20, choices=AlertStatus.choices, default=AlertStatus.PENDING,
    )
    description = models.TextField()
    responsible = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_alerts',
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    # Entitats referenciades (com a mínim una ha de ser no nul·la)
    social_account = models.ForeignKey(
        SocialAccount, on_delete=models.CASCADE, null=True, blank=True, related_name='alerts',
    )
    tracked_link = models.ForeignKey(
        TrackedLink, on_delete=models.CASCADE, null=True, blank=True, related_name='alerts',
    )
    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, null=True, blank=True, related_name='alerts',
    )
    post = models.ForeignKey(
        SocialPost, on_delete=models.CASCADE, null=True, blank=True, related_name='alerts',
    )
    collaboration = models.ForeignKey(
        Collaboration, on_delete=models.CASCADE, null=True, blank=True, related_name='alerts',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'social_crm_alert'
        ordering = ['-alert_date', '-created_at']
        indexes = [
            models.Index(fields=['company', 'status', 'severity']),
            models.Index(fields=['company', 'alert_date']),
        ]
        constraints = [
            # Garantia d'integritat referencial: tota alerta té almenys una entitat associada.
            models.CheckConstraint(
                name='alert_has_entity_ref',
                check=(
                    models.Q(social_account__isnull=False)
                    | models.Q(tracked_link__isnull=False)
                    | models.Q(campaign__isnull=False)
                    | models.Q(post__isnull=False)
                    | models.Q(collaboration__isnull=False)
                ),
            ),
        ]

    def __str__(self):
        return f'{self.get_alert_type_display()} [{self.severity}] · {self.alert_date}'
