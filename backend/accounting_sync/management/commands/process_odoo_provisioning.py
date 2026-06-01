"""
Worker que procesa OdooProvisioningJob pendientes.

Diseñado para ejecutarse periódicamente desde Windows Task Scheduler
o cron cada 30-60 segundos:

    python manage.py process_odoo_provisioning
    python manage.py process_odoo_provisioning --max 5
    python manage.py process_odoo_provisioning --job 17

Toma jobs con `select_for_update(skip_locked=True)` para soportar
ejecuciones concurrentes sin colisiones.
"""
from __future__ import annotations

import sys

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounting_sync import provisioning_service
from accounting_sync.models import OdooProvisioningJob


class Command(BaseCommand):
    help = 'Procesa OdooProvisioningJob pendientes (crea BDs Odoo + OdooConnection).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--max', type=int, default=3,
            help='Máximo de jobs a procesar en esta ejecución (default 3).',
        )
        parser.add_argument(
            '--job', type=int, default=None,
            help='ID concreto de un job a procesar (ignora la cola).',
        )

    def handle(self, *args, **options):
        # En Windows la consola usa cp1252 y peta con cualquier carácter
        # fuera de ese set (→, ─, emojis…). Forzamos UTF-8 con reemplazo
        # para que el worker nunca muera por un problema de codificación.
        for stream in (sys.stdout, sys.stderr):
            reconfigure = getattr(stream, 'reconfigure', None)
            if reconfigure:
                try:
                    reconfigure(encoding='utf-8', errors='replace')
                except Exception:  # noqa: BLE001
                    pass

        if options['job']:
            self._process_single(options['job'])
            return

        processed = 0
        max_jobs = options['max']
        while processed < max_jobs:
            job = self._claim_next_pending()
            if job is None:
                break
            self._run(job)
            processed += 1

        if processed == 0:
            self.stdout.write('No hay jobs pendientes.')
        else:
            self.stdout.write(self.style.SUCCESS(f'Procesados {processed} job(s).'))

    def _claim_next_pending(self) -> OdooProvisioningJob | None:
        """Toma 1 job pending y lo bloquea para esta transacción."""
        with transaction.atomic():
            qs = (
                OdooProvisioningJob.objects
                .select_for_update(skip_locked=True)
                .filter(status=OdooProvisioningJob.Status.PENDING)
                .order_by('created_at')
            )
            job = qs.first()
            if job is None:
                return None
            # Marcar como running dentro del lock para que otro worker no lo coja
            job.status = OdooProvisioningJob.Status.RUNNING
            job.save(update_fields=['status'])
            return job

    def _process_single(self, job_id: int) -> None:
        try:
            job = OdooProvisioningJob.objects.get(pk=job_id)
        except OdooProvisioningJob.DoesNotExist:
            self.stderr.write(self.style.ERROR(f'Job {job_id} no existe.'))
            return
        self._run(job)

    def _run(self, job: OdooProvisioningJob) -> None:
        self.stdout.write(f'> Procesando job {job.pk} - {job.company} -> {job.database_name}')
        try:
            ok = provisioning_service.provision_for_company(job)
        except Exception as exc:  # noqa: BLE001
            # provision_for_company ya captura sus errores; esto cubre un
            # fallo totalmente inesperado para que el job no quede colgado
            # en estado RUNNING para siempre.
            job.refresh_from_db()
            job.status = OdooProvisioningJob.Status.FAILED
            job.error_message = f'Crash inesperado del worker: {type(exc).__name__}: {exc}'
            job.finished_at = timezone.now()
            job.save(update_fields=['status', 'error_message', 'finished_at'])
            self.stdout.write(self.style.ERROR(f'  [ERROR] crash: {exc}'))
            return

        if ok:
            self.stdout.write(self.style.SUCCESS('  [OK] done'))
        else:
            self.stdout.write(self.style.ERROR(f'  [ERROR] failed: {job.error_message[:200]}'))
            if job.attempts < job.max_attempts:
                # Vuelve a pending para que la próxima pasada lo reintente
                job.status = OdooProvisioningJob.Status.PENDING
                job.save(update_fields=['status'])
                self.stdout.write(f'    re-encolado (attempt {job.attempts}/{job.max_attempts})')
