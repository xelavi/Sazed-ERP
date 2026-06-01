# Worker de aprovisionamiento Odoo.
# Lo invoca la tarea programada "Odoo Provisioning Worker" cada minuto.
# Procesa hasta 3 OdooProvisioningJob pendientes y termina.
$ErrorActionPreference = 'Stop'
$backend = Join-Path $PSScriptRoot '..\backend'
Set-Location $backend
& python manage.py process_odoo_provisioning --max 3 *>> (Join-Path $backend 'odoo_provisioning.log')
