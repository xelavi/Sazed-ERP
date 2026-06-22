import django
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'
django.setup()

from accounting_sync.models import OdooProvisioningJob, OdooConnection
from accounts.models import Company

print("=== OdooProvisioningJobs ===")
jobs = list(OdooProvisioningJob.objects.all().order_by('-created_at')[:10])
if not jobs:
    print("  (cap job trobat)")
for j in jobs:
    print(f"  ID:{j.pk} company:{j.company} status:{j.status} attempts:{j.attempts}")
    if j.error_message:
        print(f"    ERROR: {j.error_message[:200]}")

print()
print("=== OdooConnections ===")
conns = list(OdooConnection.objects.all())
if not conns:
    print("  (cap connexió trobada)")
for c in conns:
    print(f"  ID:{c.pk} company:{c.company} is_active:{c.is_active} base_url:{c.base_url}")

print()
print("=== Companies ===")
companies = list(Company.objects.all())
if not companies:
    print("  (cap empresa trobada)")
for co in companies:
    print(f"  ID:{co.pk} name:{co.name}")
