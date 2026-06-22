"""
Seed command: Rebaixes Estiu 2026 campaign for Sazed (company id=5).

Creates from scratch:
  - 4 social accounts (instagram, tiktok, twitter, youtube)
  - 6 influencers (Ana García, Pablo Vidal, Marta Domínguez, Elena Vega,
                   Clara Puig, Marc Roca)
  - 1 campaign (Rebaixes Estiu 2026, active, Jun–Jul 2026)
  - Channel budgets, targets and timeline events
  - 7 owned social posts
  - 4 collaborations (3 active/published, 1 pending)
  - CollaborationPublications for published deliverables
  - 4 paid ad sets
  - 4 tracked links
  - 2 alerts

Run:
    python manage.py seed_summer_campaign
    python manage.py seed_summer_campaign --reset   # drops existing and re-seeds
"""

from datetime import date, datetime, timezone

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from accounts.models import Company
from social_crm.models import (
    Alert,
    AlertSeverity,
    AlertStatus,
    AlertType,
    Campaign,
    CampaignChannel,
    CampaignChannelBudget,
    CampaignMetricKey,
    CampaignObjective,
    CampaignStatus,
    CampaignTarget,
    CampaignTimelineEvent,
    Collaboration,
    CollaborationPublication,
    CollaborationStatus,
    Influencer,
    InfluencerPlatformPresence,
    InfluencerStatus,
    MetricsEntryStatus,
    PaidAdSet,
    Platform,
    PostContentType,
    SocialAccount,
    SocialPost,
    TimelineEventType,
    TrackedLink,
)

User = get_user_model()

COMPANY_ID   = 5
RESPONSIBLE_EMAIL = 'laura.martinez@sazed.com'
DESTINATION_URL   = 'https://mystore.es/rebaixes-estiu-2026'


class Command(BaseCommand):
    help = 'Seed Rebaixes Estiu 2026 Social CRM data for Sazed (company id=5)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset', action='store_true',
            help='Drop all existing Social CRM data for Sazed before seeding.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        try:
            company = Company.objects.get(id=COMPANY_ID)
        except Company.DoesNotExist:
            raise CommandError(f'Company id={COMPANY_ID} not found.')

        try:
            responsible = User.objects.get(email=RESPONSIBLE_EMAIL)
        except User.DoesNotExist:
            raise CommandError(f'User {RESPONSIBLE_EMAIL} not found.')

        if options['reset']:
            self.stdout.write('Resetting Social CRM data for Sazed...')
            Campaign.objects.filter(company=company).delete()
            Influencer.objects.filter(company=company).delete()
            SocialAccount.objects.filter(company=company).delete()
            Alert.objects.filter(company=company).delete()
            self.stdout.write('  Done.')

        # ── 1. Social Accounts ────────────────────────────────────────────────

        self.stdout.write('Creating social accounts...')
        accounts = {}
        account_defs = [
            dict(platform='instagram', name='Sazed Instagram', username='@sazed.es',    followers=48300, posts_count=524, status='connected'),
            dict(platform='tiktok',    name='Sazed TikTok',    username='@sazed_moda',  followers=22100, posts_count=188, status='connected'),
            dict(platform='twitter',   name='Sazed Twitter',   username='@sazed_es',    followers=9800,  posts_count=1204, status='connected'),
            dict(platform='youtube',   name='Sazed YouTube',   username='Sazed Oficial',followers=6700,  posts_count=89,  status='connected'),
        ]
        for a in account_defs:
            obj, _ = SocialAccount.objects.get_or_create(
                company=company, platform=a['platform'], username=a['username'],
                defaults=dict(
                    name=a['name'], followers=a['followers'],
                    posts_count=a['posts_count'], status=a['status'],
                    responsible=responsible,
                    last_synced_at=datetime(2026, 6, 9, 10, 0, tzinfo=timezone.utc),
                ),
            )
            accounts[a['platform']] = obj

        # ── 2. Influencers ────────────────────────────────────────────────────

        self.stdout.write('Creating influencers...')
        inf_defs = [
            dict(
                name='Ana García', alias='@analifestyle', primary_platform='instagram',
                niche='Lifestyle', contact_email='ana@talentx.com', agency_name='TalentX',
                country='Espanya', language='Espanyol', status=InfluencerStatus.ACTIVE,
                score_content_quality=5, score_reliability=4.5,
                score_brand_affinity=5, score_reputation_risk=1,
                notes='Excel·lent creadora. Recomanada per a campanyes de moda i lifestyle.',
                platforms=[('instagram', '@analifestyle', 85000, 4.2, 42000, 980, 48),
                           ('tiktok',    '@analifestyle', 32000, 5.1, 18000, 540, 22)],
            ),
            dict(
                name='Pablo Vidal', alias='@pablovidal', primary_platform='instagram',
                niche='Moda masculina', contact_email='pablo@gmail.com', agency_name='',
                country='Espanya', language='Espanyol', status=InfluencerStatus.ACTIVE,
                score_content_quality=4, score_reliability=4,
                score_brand_affinity=4.5, score_reputation_risk=1,
                notes='Bon influencer per a moda masculina. Compleix els terminis.',
                platforms=[('instagram', '@pablovidal', 42000, 3.8, 21000, 540, 28)],
            ),
            dict(
                name='Marta Domínguez', alias='@martamoda', primary_platform='tiktok',
                niche='Moda', contact_email='marta@agencia-moda.com', agency_name='Moda Agency',
                country='Espanya', language='Espanyol', status=InfluencerStatus.ACTIVE,
                score_content_quality=5, score_reliability=5,
                score_brand_affinity=4.5, score_reputation_risk=1,
                notes='Top influencer a TikTok. Alta conversió. ROI excel·lent.',
                platforms=[('tiktok',    '@martamoda', 234000, 6.1, 120000, 3400, 180),
                           ('instagram', '@martamoda',  42000, 4.8,  22000,  890,  60)],
            ),
            dict(
                name='Elena Vega', alias='@elenavegafit', primary_platform='instagram',
                niche='Fitness', contact_email='elena@fit-agency.com', agency_name='FitAgency',
                country='Espanya', language='Espanyol', status=InfluencerStatus.ACTIVE,
                score_content_quality=4.5, score_reliability=4.5,
                score_brand_affinity=4, score_reputation_risk=1,
                notes='Bona per a campanyes de roba esportiva i lifestyle actiu.',
                platforms=[('instagram', '@elenavegafit', 67000, 4.8, 32000, 780, 42)],
            ),
            dict(
                name='Clara Puig', alias='@clarapuig_moda', primary_platform='instagram',
                niche='Moda i lifestyle', contact_email='clara@talentx.com', agency_name='TalentX',
                country='Espanya', language='Català', status=InfluencerStatus.ACTIVE,
                score_content_quality=0, score_reliability=0,
                score_brand_affinity=4, score_reputation_risk=1,
                notes='Nova col·laboració. Perfil molt alineat amb l\'estètica Sazed.',
                platforms=[('instagram', '@clarapuig_moda', 52000, 5.2, 26000, 680, 0)],
            ),
            dict(
                name='Marc Roca', alias='@marcroca_style', primary_platform='instagram',
                niche='Moda masculina', contact_email='marc.roca@gmail.com', agency_name='',
                country='Espanya', language='Català', status=InfluencerStatus.ACTIVE,
                score_content_quality=0, score_reliability=0,
                score_brand_affinity=4.5, score_reputation_risk=1,
                notes='Microinfluencer català. Alta afinitat de marca. Col·laboració pendent.',
                platforms=[('instagram', '@marcroca_style', 28000, 6.1, 14000, 380, 0),
                           ('tiktok',    '@marcroca_style',  8000, 7.2,  5000, 180, 0)],
            ),
        ]

        influencers = {}
        for d in inf_defs:
            platforms = d.pop('platforms')
            obj, _ = Influencer.objects.get_or_create(
                company=company, alias=d['alias'],
                defaults={k: v for k, v in d.items()},
            )
            influencers[d['alias']] = obj
            for (plat, uname, followers, eng, reach, clicks, convs) in platforms:
                InfluencerPlatformPresence.objects.get_or_create(
                    influencer=obj, platform=plat,
                    defaults=dict(
                        username=uname, followers=followers,
                        avg_engagement_rate=eng, avg_reach=reach,
                        avg_clicks=clicks, avg_conversions=convs,
                    ),
                )

        ana    = influencers['@analifestyle']
        marta  = influencers['@martamoda']
        clara  = influencers['@clarapuig_moda']
        marc   = influencers['@marcroca_style']

        # ── 3. Campaign ───────────────────────────────────────────────────────

        self.stdout.write('Creating campaign...')
        campaign, created = Campaign.objects.get_or_create(
            company=company, name='Rebaixes Estiu 2026',
            defaults=dict(
                objective=CampaignObjective.SALES,
                status=CampaignStatus.ACTIVE,
                start_date=date(2026, 6, 1),
                end_date=date(2026, 7, 31),
                total_budget=8500,
                description=(
                    'Campanya de rebaixes d\'estiu amb descomptes de fins al 40%. '
                    'Objectiu: maximitzar les vendes de la temporada estival coordinant '
                    'comptes propis, influencers i anuncis de pagament.'
                ),
                responsible=responsible,
            ),
        )
        if not created:
            self.stdout.write(self.style.WARNING('  Campaign already exists — skipping sub-objects.'))
            return

        # Channel budgets
        for channel, amount in [
            (CampaignChannel.OWNED, 500),
            (CampaignChannel.INFLUENCERS, 3800),
            (CampaignChannel.PAID, 4200),
        ]:
            CampaignChannelBudget.objects.create(campaign=campaign, channel=channel, budget_amount=amount)

        # KPI targets
        for key, value in [
            (CampaignMetricKey.REACH,       400000),
            (CampaignMetricKey.CLICKS,       28000),
            (CampaignMetricKey.CONVERSIONS,   1000),
            (CampaignMetricKey.SALES,        45000),
        ]:
            CampaignTarget.objects.create(campaign=campaign, metric_key=key, target_value=value)

        # Timeline events
        timeline = [
            (date(2026, 6, 1), "Llançament de la campanya de rebaixes d'estiu", TimelineEventType.MILESTONE),
            (date(2026, 6, 2), "Vídeo de TikTok viral: 58K d'abast en 12h",     TimelineEventType.MILESTONE),
            (date(2026, 6, 5), "Marta Domínguez publica el primer TikTok de la campanya", TimelineEventType.POST),
            (date(2026, 6, 7), "Ana García publica el Reel d'estiu — 54K d'abast",         TimelineEventType.POST),
            (date(2026, 6, 9), "Revisió setmanal de KPI: ROAS 5.32x ✓",          TimelineEventType.REVIEW),
        ]
        for ev_date, desc, ev_type in timeline:
            CampaignTimelineEvent.objects.create(
                campaign=campaign, event_date=ev_date, description=desc, event_type=ev_type,
            )

        # ── 4. Social Posts ───────────────────────────────────────────────────

        self.stdout.write('Creating social posts...')
        post_defs = [
            dict(
                account=accounts['instagram'], platform='instagram',
                title="Rebaixes Estiu 2026 🌊 Fins al 40% en moda d'estiu",
                content_type=PostContentType.REEL, published_at=date(2026, 6, 1),
                likes=3200, comments=184, shares=420, saves=890, views=38000,
                reach=38000, impressions=52000, clicks=1240, engagement_rate=6.8,
            ),
            dict(
                account=accounts['tiktok'], platform='tiktok',
                title="Haul de rebaixes d'estiu — fins al 40% off 🛍️",
                content_type=PostContentType.VIDEO, published_at=date(2026, 6, 2),
                likes=7200, comments=312, shares=1800, saves=2400, views=94000,
                reach=58000, impressions=94000, clicks=2800, engagement_rate=9.4,
            ),
            dict(
                account=accounts['instagram'], platform='instagram',
                title="10 peces estrella de les rebaixes d'estiu ☀️",
                content_type=PostContentType.CAROUSEL, published_at=date(2026, 6, 3),
                likes=1840, comments=96, shares=280, saves=520, views=0,
                reach=24000, impressions=31000, clicks=680, engagement_rate=5.1,
            ),
            dict(
                account=accounts['instagram'], platform='instagram',
                title="48h d'ofertes exclusives per a seguidors 🔥",
                content_type=PostContentType.STORY, published_at=date(2026, 6, 4),
                likes=0, comments=0, shares=0, saves=0, views=14000,
                reach=14000, impressions=14000, clicks=540, engagement_rate=3.9,
            ),
            dict(
                account=accounts['youtube'], platform='youtube',
                title="REBAIXES ESTIU 2026 | Haul complet amb preus reals",
                content_type=PostContentType.VIDEO, published_at=date(2026, 6, 5),
                likes=720, comments=98, shares=45, saves=0, views=9200,
                reach=9200, impressions=9200, clicks=380, engagement_rate=5.3,
            ),
            dict(
                account=accounts['twitter'], platform='twitter',
                title="🌊 Rebaixes d'estiu de fins al 40%! Entra ara 👉",
                content_type=PostContentType.TWEET, published_at=date(2026, 6, 7),
                likes=187, comments=23, shares=134, saves=0, views=8400,
                reach=6100, impressions=8400, clicks=245, engagement_rate=3.7,
            ),
            dict(
                account=accounts['instagram'], platform='instagram',
                title="Nous vestits d'estiu afegits a les rebaixes 👙",
                content_type=PostContentType.REEL, published_at=date(2026, 6, 9),
                likes=1920, comments=108, shares=340, saves=620, views=22000,
                reach=22000, impressions=28000, clicks=680, engagement_rate=6.5,
            ),
        ]
        posts = []
        for d in post_defs:
            p = SocialPost.objects.create(company=company, campaign=campaign, **d)
            posts.append(p)

        # ── 5. Tracked Links ──────────────────────────────────────────────────

        self.stdout.write('Creating tracked links...')
        marta_presence = InfluencerPlatformPresence.objects.get(influencer=marta, platform='tiktok')
        ana_presence   = InfluencerPlatformPresence.objects.get(influencer=ana,   platform='instagram')
        clara_presence = InfluencerPlatformPresence.objects.get(influencer=clara, platform='instagram')

        link_marta = TrackedLink.objects.create(
            company=company, campaign=campaign,
            name='Enllaç TikTok Marta Domínguez - Rebaixes Estiu',
            destination_url=DESTINATION_URL,
            origin_platform='tiktok',
            utm_source='tiktok', utm_medium='influencer',
            utm_campaign='rebaixes2026', utm_content='marta-moda',
            clicks=3200, sessions=2900, carts=640, purchases=98, revenue=4200,
        )
        link_ana = TrackedLink.objects.create(
            company=company, campaign=campaign,
            name='Enllaç Instagram Ana García - Rebaixes Estiu',
            destination_url=DESTINATION_URL,
            origin_platform='instagram',
            utm_source='instagram', utm_medium='influencer',
            utm_campaign='rebaixes2026', utm_content='ana-garcia',
            clicks=1800, sessions=1620, carts=310, purchases=67, revenue=2900,
        )
        link_clara = TrackedLink.objects.create(
            company=company, campaign=campaign,
            name='Enllaç Instagram Clara Puig - Rebaixes Estiu',
            destination_url=DESTINATION_URL,
            origin_platform='instagram',
            utm_source='instagram', utm_medium='influencer',
            utm_campaign='rebaixes2026', utm_content='clara-puig',
            clicks=320, sessions=290, carts=42, purchases=0, revenue=0,
        )
        link_organic = TrackedLink.objects.create(
            company=company, campaign=campaign,
            name='Enllaç general Rebaixes Estiu (bio + orgànic)',
            destination_url=DESTINATION_URL,
            origin_platform='instagram',
            utm_source='instagram', utm_medium='organic',
            utm_campaign='rebaixes2026', utm_content='bio-organic',
            clicks=980, sessions=840, carts=168, purchases=52, revenue=2200,
        )

        # ── 6. Collaborations ─────────────────────────────────────────────────

        self.stdout.write('Creating collaborations...')

        collab_marta = Collaboration.objects.create(
            company=company, campaign=campaign,
            influencer=marta, platform_presence=marta_presence,
            content_format='2 TikToks + Reel Instagram',
            publish_date=date(2026, 6, 5),
            agreed_cost=2800, discount_code='MARTA30',
            status=CollaborationStatus.ACTIVE,
            deliverables_description='2 TikToks de 60s + 1 Reel d\'Instagram. TikTok #1 i #2 publicats. Reel pendent.',
            expected_reach=100000, expected_clicks=5000, expected_conversions=200,
            actual_reach=112000, actual_impressions=142000, actual_views=180000,
            actual_likes=9800, actual_comments=420, actual_shares=2400,
            observations='Dos TikToks publicats amb molt bon rendiment. El primer va superar les 180K visualitzacions.',
            recommendation='',
        )
        collab_marta.tracked_links.add(link_marta)

        collab_ana = Collaboration.objects.create(
            company=company, campaign=campaign,
            influencer=ana, platform_presence=ana_presence,
            content_format='Reel + 4 Stories',
            publish_date=date(2026, 6, 7),
            agreed_cost=2000, discount_code='ANA30',
            status=CollaborationStatus.ACTIVE,
            deliverables_description='1 Reel + 4 Stories amb swipe up a la pàgina de rebaixes. Reel publicat. Stories en curs.',
            expected_reach=50000, expected_clicks=1500, expected_conversions=80,
            actual_reach=54000, actual_impressions=71000, actual_views=0,
            actual_likes=3800, actual_comments=198, actual_shares=320,
            observations='Molt bon inici. Per sobre del reach esperat als 2 dies de publicació.',
            recommendation='',
        )
        collab_ana.tracked_links.add(link_ana)

        collab_clara = Collaboration.objects.create(
            company=company, campaign=campaign,
            influencer=clara, platform_presence=clara_presence,
            content_format='Reel + 3 Stories',
            publish_date=date(2026, 6, 9),
            agreed_cost=1200, discount_code='CLARA20',
            status=CollaborationStatus.ACTIVE,
            deliverables_description='1 Reel + 3 Stories. Reel publicat avui. Stories pendents.',
            expected_reach=28000, expected_clicks=800, expected_conversions=30,
            actual_reach=8400, actual_impressions=11000, actual_views=8400,
            actual_likes=620, actual_comments=42, actual_shares=89,
            observations='Publicació d\'avui. Massa d\'hora per avaluar el rendiment.',
            recommendation='',
        )
        collab_clara.tracked_links.add(link_clara)

        marc_presence = InfluencerPlatformPresence.objects.get(influencer=marc, platform='instagram')
        Collaboration.objects.create(
            company=company, campaign=campaign,
            influencer=marc, platform_presence=marc_presence,
            content_format='Post + 2 Stories',
            publish_date=date(2026, 6, 12),
            agreed_cost=800, discount_code='MARC15',
            status=CollaborationStatus.PENDING,
            deliverables_description='1 post imatge + 2 stories. Publicació prevista el 12/06.',
            expected_reach=14000, expected_clicks=380, expected_conversions=15,
            actual_reach=0, actual_impressions=0, actual_views=0,
            actual_likes=0, actual_comments=0, actual_shares=0,
            observations='Col·laboració acordada. Briefing enviat. Pendent de publicació.',
            recommendation='',
        )

        # CollaborationPublications for published deliverables
        CollaborationPublication.objects.create(
            collaboration=collab_marta,
            content_type=PostContentType.VIDEO, description='TikTok #1 - Rebaixes Estiu',
            publication_date=date(2026, 6, 5),
            reach=68000, impressions=88000, views=112000, likes=6200, comments=280, shares=1600,
            metrics_status=MetricsEntryStatus.VALIDATED,
        )
        CollaborationPublication.objects.create(
            collaboration=collab_marta,
            content_type=PostContentType.VIDEO, description='TikTok #2 - Rebaixes Estiu (continuació)',
            publication_date=date(2026, 6, 7),
            reach=44000, impressions=54000, views=68000, likes=3600, comments=140, shares=800,
            metrics_status=MetricsEntryStatus.VALIDATED,
        )
        CollaborationPublication.objects.create(
            collaboration=collab_ana,
            content_type=PostContentType.REEL, description='Reel Instagram - Rebaixes Estiu',
            publication_date=date(2026, 6, 7),
            reach=54000, impressions=71000, views=0, likes=3800, comments=198, shares=320,
            metrics_status=MetricsEntryStatus.VALIDATED,
        )
        CollaborationPublication.objects.create(
            collaboration=collab_clara,
            content_type=PostContentType.REEL, description='Reel Instagram - Rebaixes Estiu',
            publication_date=date(2026, 6, 9),
            reach=8400, impressions=11000, views=8400, likes=620, comments=42, shares=89,
            metrics_status=MetricsEntryStatus.PENDING,
        )

        # ── 7. Paid Ad Sets ───────────────────────────────────────────────────

        self.stdout.write('Creating paid ad sets...')
        ad_defs = [
            dict(ad_platform='facebook', name='Rebaixes Estiu · Catàleg dinàmic',
                 start_date=date(2026, 6, 1), end_date=date(2026, 7, 31),
                 budget_amount=2000, spend_amount=820,
                 impressions=72000, clicks=2800, conversions=86, sales_revenue=3800),
            dict(ad_platform='google',   name='Rebaixes Estiu · Shopping + Search',
                 start_date=date(2026, 6, 1), end_date=date(2026, 7, 31),
                 budget_amount=1800, spend_amount=680,
                 impressions=48000, clicks=2300, conversions=72, sales_revenue=3200),
            dict(ad_platform='tiktok',   name='Rebaixes Estiu · Spark Ads',
                 start_date=date(2026, 6, 2), end_date=date(2026, 7, 31),
                 budget_amount=1000, spend_amount=380,
                 impressions=84000, clicks=1900, conversions=48, sales_revenue=2100),
            dict(ad_platform='instagram',name='Rebaixes Estiu · Reels Promotion',
                 start_date=date(2026, 6, 4), end_date=date(2026, 7, 31),
                 budget_amount=600, spend_amount=240,
                 impressions=32000, clicks=1100, conversions=28, sales_revenue=1200),
        ]
        for d in ad_defs:
            PaidAdSet.objects.create(company=company, campaign=campaign, status=CampaignStatus.ACTIVE, **d)

        # ── 8. Alerts ─────────────────────────────────────────────────────────

        self.stdout.write('Creating alerts...')
        Alert.objects.create(
            company=company, campaign=campaign,
            alert_date=date(2026, 6, 9),
            alert_type=AlertType.MISSING_METRICS,
            severity=AlertSeverity.LOW,
            status=AlertStatus.PENDING,
            description='Reel de Clara Puig publicat avui. Mètriques inicials carregades, Stories pendents de publicació.',
        )
        Alert.objects.create(
            company=company, campaign=campaign,
            alert_date=date(2026, 6, 8),
            alert_type=AlertType.HIGH_COST,
            severity=AlertSeverity.LOW,
            status=AlertStatus.PENDING,
            responsible=responsible,
            description='CPM pujant als últims 2 dies (+18%) als TikTok Spark Ads. Monitoritzar si supera el benchmark setmanal.',
        )

        self.stdout.write(self.style.SUCCESS(
            '\nRebaixes Estiu 2026 seeded OK for Sazed:\n'
            f'  Campaign id={campaign.id}\n'
            f'  {len(inf_defs)} influencers\n'
            f'  {len(posts)} social posts\n'
            f'  4 collaborations (3 active/published, 1 pending)\n'
            f'  4 paid ad sets\n'
            f'  4 tracked links\n'
            f'  2 alerts\n'
        ))
