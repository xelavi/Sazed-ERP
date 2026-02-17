<template>
  <div class="customers-view">
    <div class="view-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="view-title">Customers</h1>
          <span class="count-badge">{{ customers.length }}</span>
        </div>
        <div class="header-actions">
          <button class="btn btn-secondary">
            <Download :size="18" />
            <span>Export</span>
          </button>
          <button class="btn btn-primary" @click="openCustomerForm()">
            <Plus :size="18" />
            <span>Add customer</span>
          </button>
        </div>
      </div>
    </div>

    <div class="content-wrapper">
      <div class="filters-bar">
        <div class="search-box">
          <Search :size="18" class="search-icon" />
          <input
            type="text"
            class="input search-input"
            placeholder="Search by name, email..."
            v-model="searchQuery"
          />
        </div>
        <div class="filter-actions">
          <div class="type-toggle">
            <button
              :class="['toggle-btn', { active: typeFilter === 'all' }]"
              @click="typeFilter = 'all'"
            >All</button>
            <button
              :class="['toggle-btn', { active: typeFilter === 'company' }]"
              @click="typeFilter = 'company'"
            >
              <Building2 :size="14" />
              Company
            </button>
            <button
              :class="['toggle-btn', { active: typeFilter === 'person' }]"
              @click="typeFilter = 'person'"
            >
              <User :size="14" />
              Person
            </button>
          </div>
          <select class="select filter-select" v-model="statusFilter">
            <option value="all">All statuses</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
          <select class="select filter-select" v-model="cityFilter">
            <option value="all">All cities</option>
            <option v-for="city in cities" :key="city" :value="city">{{ city }}</option>
          </select>
          <button class="btn btn-secondary" @click="sortCustomers">
            <ArrowUpDown :size="18" />
            <span>Sort</span>
          </button>
        </div>
      </div>

      <div class="card table-card">
        <div class="table-wrapper">
          <table class="table customers-table">
            <thead>
              <tr>
                <th class="col-checkbox">
                  <input type="checkbox" class="checkbox" @change="toggleSelectAll" :checked="allSelected" />
                </th>
                <th class="col-avatar"></th>
                <th class="col-name">Name</th>
                <th class="col-type">Type</th>
                <th class="col-email">Email</th>
                <th class="col-city">City</th>
                <th class="col-linked">Linked</th>
                <th class="col-status">Status</th>
                <th class="col-actions"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="customer in filteredCustomers" :key="customer.id" class="table-row" @click="openDetail(customer)">
                <td class="col-checkbox" @click.stop>
                  <input type="checkbox" class="checkbox" v-model="selectedCustomers" :value="customer.id" />
                </td>
                <td class="col-avatar">
                  <div class="customer-avatar" :style="{ background: customer.avatarColor }">
                    {{ customer.initials }}
                  </div>
                </td>
                <td class="col-name">
                  <span class="customer-name">{{ customer.name }}</span>
                  <span v-if="customer.type === 'Company' && customer.vatId" class="vat-hint">{{ customer.vatId }}</span>
                </td>
                <td class="col-type">
                  <span :class="['type-badge', customer.type === 'Company' ? 'type-company' : 'type-person']">
                    <Building2 v-if="customer.type === 'Company'" :size="12" />
                    <User v-else :size="12" />
                    {{ customer.type }}
                  </span>
                </td>
                <td class="col-email">
                  <span class="email-text">{{ customer.email }}</span>
                </td>
                <td class="col-city">
                  <span class="city-text">{{ customer.city }}</span>
                </td>
                <td class="col-linked">
                  <div v-if="customer.linked.length" class="linked-list">
                    <span class="linked-tag" v-for="link in customer.linked.slice(0, 2)" :key="link">{{ link }}</span>
                    <span v-if="customer.linked.length > 2" class="linked-more">+{{ customer.linked.length - 2 }}</span>
                  </div>
                  <span v-else class="text-tertiary">—</span>
                </td>
                <td class="col-status">
                  <span :class="['badge', statusBadgeClass(customer.status)]">
                    {{ customer.status }}
                  </span>
                </td>
                <td class="col-actions" @click.stop>
                  <button class="btn-icon" @click="openCustomerForm(customer)">
                    <Pencil :size="16" />
                  </button>
                  <button class="btn-icon">
                    <MoreVertical :size="18" />
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="table-footer">
          <span class="table-footer-info">
            Showing <strong>{{ filteredCustomers.length }}</strong> of <strong>{{ customers.length }}</strong> customers
          </span>
        </div>
      </div>
    </div>

    <!-- ===================== CUSTOMER DETAIL DRAWER ===================== -->
    <CustomerDetailDrawer
      v-if="selectedCustomer"
      :customer="selectedCustomer"
      :open="detailOpen"
      @close="closeDetail"
      @edit="(c) => { closeDetail(); openCustomerForm(c) }"
      @new-invoice="handleNewInvoice"
    />

    <!-- ===================== CREATE / EDIT MODAL ===================== -->
    <CustomerFormModal
      :open="formModalOpen"
      :customer="formCustomer"
      @close="closeCustomerForm"
      @save="handleCustomerSave"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  Plus, Search, ArrowUpDown, MoreVertical, Download,
  Building2, User, Pencil
} from 'lucide-vue-next'
import CustomerDetailDrawer from '@/components/CustomerDetailDrawer.vue'
import CustomerFormModal from '@/components/CustomerFormModal.vue'

const router = useRouter()

/* ── Drawer state ── */
const detailOpen = ref(false)
const selectedCustomer = ref(null)

function openDetail(customer) {
  selectedCustomer.value = customer
  detailOpen.value = true
}

function closeDetail() {
  detailOpen.value = false
}

/* ── Form modal state ── */
const formModalOpen = ref(false)
const formCustomer = ref(null)

function openCustomerForm(customer = null) {
  formCustomer.value = customer
  formModalOpen.value = true
}

function closeCustomerForm() {
  formModalOpen.value = false
  formCustomer.value = null
}

function handleCustomerSave(formData) {
  if (formCustomer.value) {
    // Editing existing customer
    const c = formCustomer.value
    c.name = formData.name
    c.email = formData.email
    c.type = formData.type
    c.status = formData.status
    c.city = formData.city || c.city
    c.vatId = formData.vatId || null
    c.initials = formData.initials
    c.avatarColor = formData.avatarColor
    c.detail.phone = formData.phone
    c.detail.website = formData.website
    c.detail.address = formData.address
    c.detail.province = formData.province
    c.detail.postalCode = formData.postalCode
    c.detail.country = formData.country
    c.detail.legalName = formData.legalName
    c.detail.paymentMethod = formData.paymentMethod
    c.detail.bankAccount = formData.bankAccount
    c.detail.internalNotes = formData.internalNotes
    c.detail.tags = [...formData.tags]
    c.detail.isCustomer = formData.isCustomer
    c.detail.isSupplier = formData.isSupplier
  } else {
    // Creating new customer
    const newId = Math.max(...customers.value.map(c => c.id)) + 1
    customers.value.push({
      id: newId,
      name: formData.name,
      type: formData.type,
      email: formData.email,
      city: formData.city || '',
      status: formData.status,
      vatId: formData.vatId || null,
      avatarColor: formData.avatarColor,
      initials: formData.initials,
      linked: [],
      detail: {
        phone: formData.phone,
        website: formData.website,
        address: formData.address,
        province: formData.province,
        postalCode: formData.postalCode,
        country: formData.country,
        legalName: formData.legalName,
        paymentMethod: formData.paymentMethod,
        bankAccount: formData.bankAccount,
        internalNotes: formData.internalNotes,
        tags: [...formData.tags],
        isCustomer: formData.isCustomer,
        isSupplier: formData.isSupplier,
        totalInvoiced: 0,
        pendingBalance: 0,
        totalDocuments: 0,
        notes: [],
        quotes: [],
        invoices: [],
        activities: [],
        purchases: []
      }
    })
  }
}

function handleNewInvoice(customer) {
  closeDetail()
  router.push({ name: 'Invoices', query: { newInvoice: 'true', customerId: customer.id } })
}

/* ── Table state ── */
const searchQuery = ref('')
const statusFilter = ref('all')
const typeFilter = ref('all')
const cityFilter = ref('all')
const selectedCustomers = ref([])
const sortAsc = ref(true)

/* ── Customers data ── */
const customers = ref([
  {
    id: 1,
    name: 'Acme Corp.',
    type: 'Company',
    email: 'contact@acmecorp.com',
    city: 'Madrid',
    status: 'Active',
    vatId: 'B-12345678',
    avatarColor: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    initials: 'AC',
    linked: ['María López', 'Pedro Ruiz'],
    detail: {
      phone: '+34 911 234 567',
      website: 'https://acmecorp.com',
      address: 'Calle Gran Vía 42, 3ºA',
      province: 'Madrid',
      postalCode: '28013',
      country: 'España',
      legalName: 'Acme Corporation S.L.',
      paymentMethod: 'Transferencia 30 días',
      bankAccount: 'ES12 0049 1234 5678 9012 3456',
      internalNotes: 'Cliente preferente. Descuento negociado del 5%.',
      tags: ['Preferente', 'Tecnología'],
      isCustomer: true,
      isSupplier: false,
      totalInvoiced: 24850.00,
      pendingBalance: 3200.00,
      totalDocuments: 12,
      notes: [
        { id: 1, date: '2026-02-10', author: 'Admin', content: 'Reunión de seguimiento trimestral completada. Satisfechos con el servicio.' },
        { id: 2, date: '2026-01-15', author: 'Admin', content: 'Solicitan ampliación de línea de crédito.' }
      ],
      quotes: [
        { id: 1, number: 'PRES-001', concept: 'Migración infraestructura cloud', amount: 12500, date: '2026-02-05', validDays: 30, notes: '', status: 'Enviado' },
        { id: 2, number: 'PRES-002', concept: 'Mantenimiento anual servidores', amount: 4800, date: '2026-01-20', validDays: 15, notes: '', status: 'Aceptado' }
      ],
      invoices: [
        { id: 1, number: 'FAC-2026-001', date: '2026-02-01', amount: 4800, status: 'Pagada' },
        { id: 2, number: 'FAC-2026-005', date: '2026-02-12', amount: 3200, status: 'Aprobada' }
      ],
      activities: [
        { id: 1, type: 'Reunión', date: '2026-02-10', subject: 'Revisión trimestral Q1', notes: 'Asistieron el CEO y el CTO. Contentos con resultados.' },
        { id: 2, type: 'Email', date: '2026-02-03', subject: 'Envío propuesta migración cloud', notes: '' },
        { id: 3, type: 'Llamada', date: '2026-01-28', subject: 'Seguimiento factura pendiente', notes: 'Confirman pago para la semana que viene.' }
      ],
      purchases: [
        { id: 1, product: 'Licencia ERP Premium', amount: 4800, date: '2026-02-01', quantity: 1, status: 'Completada' },
        { id: 2, product: 'Pack soporte 50h', amount: 2500, date: '2026-01-10', quantity: 1, status: 'Completada' }
      ]
    }
  },
  {
    id: 2,
    name: 'María López',
    type: 'Person',
    email: 'maria.lopez@email.com',
    city: 'Madrid',
    status: 'Active',
    vatId: null,
    avatarColor: 'linear-gradient(135deg, #EC4899 0%, #F59E0B 100%)',
    initials: 'ML',
    linked: ['Acme Corp.'],
    detail: {
      phone: '+34 612 345 678', website: '', address: 'Calle Serrano 15', province: 'Madrid', postalCode: '28001', country: 'España',
      legalName: '', paymentMethod: 'Transferencia', bankAccount: '', internalNotes: '', tags: ['Contacto Acme'],
      isCustomer: true, isSupplier: false, totalInvoiced: 1200, pendingBalance: 0, totalDocuments: 2,
      notes: [], quotes: [], invoices: [
        { id: 3, number: 'FAC-2025-042', date: '2025-12-10', amount: 1200, status: 'Pagada' }
      ], activities: [
        { id: 4, type: 'Llamada', date: '2026-01-20', subject: 'Consulta sobre renovación', notes: '' }
      ], purchases: []
    }
  },
  {
    id: 3,
    name: 'Oficinas Modernas S.L.',
    type: 'Company',
    email: 'admin@oficinasmodernas.es',
    city: 'Barcelona',
    status: 'Active',
    vatId: 'B-87654321',
    avatarColor: 'linear-gradient(135deg, #10B981 0%, #3B82F6 100%)',
    initials: 'OM',
    linked: ['Carlos Méndez', 'Laura Martín', 'Elena Vidal'],
    detail: {
      phone: '+34 933 456 789', website: 'https://oficinasmodernas.es', address: 'Avinguda Diagonal 520', province: 'Barcelona', postalCode: '08006', country: 'España',
      legalName: 'Oficinas Modernas S.L.', paymentMethod: 'Domiciliación', bankAccount: 'ES98 2100 0813 6101 2345 6789', internalNotes: 'Facturación mensual. Revisar tarifa en abril.',
      tags: ['Mobiliario', 'B2B'], isCustomer: true, isSupplier: true, totalInvoiced: 18400, pendingBalance: 2100, totalDocuments: 8,
      notes: [
        { id: 3, date: '2026-01-30', author: 'Admin', content: 'Negociación nuevo contrato mobiliario Q2.' }
      ],
      quotes: [
        { id: 3, number: 'PRES-003', concept: 'Equipamiento sala reuniones', amount: 6200, date: '2026-01-25', validDays: 30, notes: '', status: 'Borrador' }
      ],
      invoices: [
        { id: 4, number: 'FAC-2026-003', date: '2026-01-15', amount: 2100, status: 'Vencida' },
        { id: 5, number: 'FAC-2025-098', date: '2025-12-01', amount: 5400, status: 'Pagada' }
      ],
      activities: [
        { id: 5, type: 'Visita', date: '2026-01-30', subject: 'Presentación catálogo nuevo', notes: 'Interesados en la línea premium.' }
      ],
      purchases: [
        { id: 3, product: 'Escritorio Ergonómico Pro', amount: 890, date: '2025-12-01', quantity: 6, status: 'Completada' }
      ]
    }
  },
  {
    id: 4,
    name: 'Pedro Ruiz',
    type: 'Person',
    email: 'pruiz@gmail.com',
    city: 'Valencia',
    status: 'Active',
    vatId: null,
    avatarColor: 'linear-gradient(135deg, #F59E0B 0%, #EF4444 100%)',
    initials: 'PR',
    linked: ['Acme Corp.'],
    detail: {
      phone: '+34 645 678 901', website: '', address: 'Calle Colón 28', province: 'Valencia', postalCode: '46004', country: 'España',
      legalName: '', paymentMethod: 'Transferencia', bankAccount: '', internalNotes: '', tags: [],
      isCustomer: true, isSupplier: false, totalInvoiced: 850, pendingBalance: 0, totalDocuments: 1,
      notes: [], quotes: [], invoices: [], activities: [], purchases: []
    }
  },
  {
    id: 5,
    name: 'Carlos Méndez',
    type: 'Person',
    email: 'carlos.mendez@oficinasmodernas.es',
    city: 'Barcelona',
    status: 'Active',
    vatId: null,
    avatarColor: 'linear-gradient(135deg, #8B5CF6 0%, #EC4899 100%)',
    initials: 'CM',
    linked: ['Oficinas Modernas S.L.'],
    detail: {
      phone: '+34 654 321 098', website: '', address: '', province: 'Barcelona', postalCode: '', country: 'España',
      legalName: '', paymentMethod: 'Transferencia', bankAccount: '', internalNotes: '', tags: [],
      isCustomer: true, isSupplier: false, totalInvoiced: 0, pendingBalance: 0, totalDocuments: 0,
      notes: [], quotes: [], invoices: [], activities: [], purchases: []
    }
  },
  {
    id: 6,
    name: 'Laura Martín',
    type: 'Person',
    email: 'laura.martin@email.com',
    city: 'Sevilla',
    status: 'Inactive',
    vatId: null,
    avatarColor: 'linear-gradient(135deg, #06B6D4 0%, #8B5CF6 100%)',
    initials: 'LM',
    linked: ['Oficinas Modernas S.L.'],
    detail: {
      phone: '', website: '', address: '', province: 'Sevilla', postalCode: '', country: 'España',
      legalName: '', paymentMethod: 'Transferencia', bankAccount: '', internalNotes: '', tags: [],
      isCustomer: true, isSupplier: false, totalInvoiced: 0, pendingBalance: 0, totalDocuments: 0,
      notes: [], quotes: [], invoices: [], activities: [], purchases: []
    }
  },
  {
    id: 7,
    name: 'Café Molino',
    type: 'Company',
    email: 'info@cafemolino.es',
    city: 'Sevilla',
    status: 'Active',
    vatId: 'B-11223344',
    avatarColor: 'linear-gradient(135deg, #F59E0B 0%, #10B981 100%)',
    initials: 'CM',
    linked: ['Jorge Pérez'],
    detail: {
      phone: '+34 955 123 456', website: 'https://cafemolino.es', address: 'Plaza Nueva 6', province: 'Sevilla', postalCode: '41001', country: 'España',
      legalName: 'Café Molino S.L.', paymentMethod: 'Efectivo', bankAccount: '', internalNotes: 'Pago al contado.',
      tags: ['Hostelería'], isCustomer: true, isSupplier: false, totalInvoiced: 3600, pendingBalance: 600, totalDocuments: 4,
      notes: [], quotes: [],
      invoices: [
        { id: 6, number: 'FAC-2026-008', date: '2026-02-14', amount: 600, status: 'Aprobada' }
      ],
      activities: [
        { id: 6, type: 'Visita', date: '2026-02-14', subject: 'Entrega de producto', notes: '' }
      ],
      purchases: [
        { id: 4, product: 'Cafetera Industrial X200', amount: 2400, date: '2025-11-20', quantity: 1, status: 'Completada' }
      ]
    }
  },
  {
    id: 8,
    name: 'Jorge Pérez',
    type: 'Person',
    email: 'jorge.perez@cafemolino.es',
    city: 'Sevilla',
    status: 'Active',
    vatId: null,
    avatarColor: 'linear-gradient(135deg, #3B82F6 0%, #06B6D4 100%)',
    initials: 'JP',
    linked: ['Café Molino'],
    detail: {
      phone: '+34 678 901 234', website: '', address: '', province: 'Sevilla', postalCode: '', country: 'España',
      legalName: '', paymentMethod: 'Transferencia', bankAccount: '', internalNotes: '', tags: [],
      isCustomer: true, isSupplier: false, totalInvoiced: 0, pendingBalance: 0, totalDocuments: 0,
      notes: [], quotes: [], invoices: [], activities: [], purchases: []
    }
  },
  {
    id: 9,
    name: 'Luis Fernández',
    type: 'Person',
    email: 'lfernandez@outlook.com',
    city: 'Bilbao',
    status: 'Active',
    vatId: null,
    avatarColor: 'linear-gradient(135deg, #EF4444 0%, #F59E0B 100%)',
    initials: 'LF',
    linked: [],
    detail: {
      phone: '+34 699 876 543', website: '', address: 'Alameda Mazarredo 12', province: 'Vizcaya', postalCode: '48001', country: 'España',
      legalName: '', paymentMethod: 'Transferencia', bankAccount: '', internalNotes: '', tags: ['Freelance'],
      isCustomer: true, isSupplier: false, totalInvoiced: 2200, pendingBalance: 0, totalDocuments: 3,
      notes: [
        { id: 4, date: '2026-02-01', author: 'Admin', content: 'Interesado en servicios de consultoría.' }
      ],
      quotes: [], invoices: [], activities: [], purchases: []
    }
  },
  {
    id: 10,
    name: 'TechParts Ibérica S.A.',
    type: 'Company',
    email: 'ventas@techparts.es',
    city: 'Madrid',
    status: 'Active',
    vatId: 'A-99887766',
    avatarColor: 'linear-gradient(135deg, #667eea 0%, #10B981 100%)',
    initials: 'TI',
    linked: ['Ana García'],
    detail: {
      phone: '+34 914 567 890', website: 'https://techparts.es', address: 'Polígono Industrial Sur, Nave 14', province: 'Madrid', postalCode: '28906', country: 'España',
      legalName: 'TechParts Ibérica S.A.', paymentMethod: 'Transferencia 30 días', bankAccount: 'ES55 0182 2345 6789 0123 4567', internalNotes: 'Proveedor principal de componentes electrónicos.',
      tags: ['Proveedor', 'Electrónica'], isCustomer: false, isSupplier: true, totalInvoiced: 0, pendingBalance: 0, totalDocuments: 5,
      notes: [], quotes: [],
      invoices: [],
      activities: [
        { id: 7, type: 'Email', date: '2026-02-08', subject: 'Solicitud catálogo actualizado 2026', notes: '' }
      ],
      purchases: []
    }
  },
  {
    id: 11,
    name: 'Ana García',
    type: 'Person',
    email: 'ana.garcia@techparts.es',
    city: 'Madrid',
    status: 'Active',
    vatId: null,
    avatarColor: 'linear-gradient(135deg, #EC4899 0%, #8B5CF6 100%)',
    initials: 'AG',
    linked: ['TechParts Ibérica S.A.'],
    detail: {
      phone: '+34 622 333 444', website: '', address: '', province: 'Madrid', postalCode: '', country: 'España',
      legalName: '', paymentMethod: 'Transferencia', bankAccount: '', internalNotes: '', tags: [],
      isCustomer: true, isSupplier: false, totalInvoiced: 0, pendingBalance: 0, totalDocuments: 0,
      notes: [], quotes: [], invoices: [], activities: [], purchases: []
    }
  },
  {
    id: 12,
    name: 'Elena Vidal',
    type: 'Person',
    email: 'elena.vidal@email.com',
    city: 'Zaragoza',
    status: 'Inactive',
    vatId: null,
    avatarColor: 'linear-gradient(135deg, #06B6D4 0%, #10B981 100%)',
    initials: 'EV',
    linked: ['Oficinas Modernas S.L.'],
    detail: {
      phone: '', website: '', address: '', province: 'Zaragoza', postalCode: '', country: 'España',
      legalName: '', paymentMethod: 'Transferencia', bankAccount: '', internalNotes: '', tags: [],
      isCustomer: true, isSupplier: false, totalInvoiced: 0, pendingBalance: 0, totalDocuments: 0,
      notes: [], quotes: [], invoices: [], activities: [], purchases: []
    }
  }
])

/* ── Computed ── */
const cities = computed(() => {
  const c = [...new Set(customers.value.map(cu => cu.city))]
  return c.sort()
})

const allSelected = computed(() => {
  return filteredCustomers.value.length > 0 && selectedCustomers.value.length === filteredCustomers.value.length
})

const filteredCustomers = computed(() => {
  let result = customers.value

  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(c =>
      c.name.toLowerCase().includes(q) ||
      c.email.toLowerCase().includes(q) ||
      (c.vatId && c.vatId.toLowerCase().includes(q))
    )
  }

  if (statusFilter.value !== 'all') {
    result = result.filter(c => c.status.toLowerCase() === statusFilter.value)
  }

  if (typeFilter.value !== 'all') {
    result = result.filter(c => c.type.toLowerCase() === typeFilter.value)
  }

  if (cityFilter.value !== 'all') {
    result = result.filter(c => c.city === cityFilter.value)
  }

  return result
})

/* ── Actions ── */
function toggleSelectAll() {
  if (allSelected.value) {
    selectedCustomers.value = []
  } else {
    selectedCustomers.value = filteredCustomers.value.map(c => c.id)
  }
}

function sortCustomers() {
  sortAsc.value = !sortAsc.value
  customers.value.sort((a, b) => {
    return sortAsc.value
      ? a.name.localeCompare(b.name)
      : b.name.localeCompare(a.name)
  })
}

/* ── Helpers ── */
function statusBadgeClass(status) {
  const map = { Active: 'badge-success', Inactive: 'badge-warning' }
  return map[status] || 'badge-gray'
}
</script>

<style scoped>
.customers-view {
  width: 100%;
}

.view-header {
  margin-bottom: 2rem;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 0.875rem;
}

.view-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
}

.count-badge {
  background: linear-gradient(135deg, #f0f2f5 0%, #e8eaed 100%);
  color: var(--text-secondary);
  padding: 0.375rem 0.875rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

/* ============================
   FILTERS
   ============================ */
.filters-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.search-box {
  position: relative;
  flex: 1;
  max-width: 360px;
}

.search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-tertiary);
}

.search-input {
  padding-left: 3rem;
}

.filter-actions {
  display: flex;
  gap: 0.625rem;
  align-items: center;
  flex-wrap: wrap;
}

.filter-select {
  width: auto;
  min-width: 140px;
  padding: 0.5rem 0.75rem;
  font-size: var(--font-size-xs);
}

/* ============================
   TYPE TOGGLE (Company / Person)
   ============================ */
.type-toggle {
  display: inline-flex;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  overflow: hidden;
  background: white;
}

.toggle-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.875rem;
  font-size: var(--font-size-xs);
  font-weight: 500;
  font-family: var(--font-family);
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
}

.toggle-btn:not(:last-child) {
  border-right: 1px solid var(--border-color);
}

.toggle-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.toggle-btn.active {
  background: var(--primary-light);
  color: var(--primary-color);
  font-weight: 600;
}

/* ============================
   TABLE LAYOUT
   ============================ */
.table-card {
  padding: 0;
  overflow: hidden;
}

.table-wrapper {
  overflow-x: auto;
}

.customers-table {
  min-width: 860px;
}

.customers-table th {
  font-size: 0.6875rem;
  padding: 0.625rem 0.75rem;
  white-space: nowrap;
  user-select: none;
}

.customers-table td {
  padding: 0.625rem 0.75rem;
  vertical-align: middle;
  white-space: nowrap;
}

.col-checkbox { width: 40px; text-align: center; }
.col-avatar { width: 48px; }
.col-name { min-width: 180px; white-space: normal !important; }
.col-type { width: 110px; }
.col-email { min-width: 180px; }
.col-city { width: 120px; }
.col-linked { min-width: 180px; }
.col-status { width: 90px; }
.col-actions { width: 40px; }

.table-row {
  transition: background var(--transition-fast);
  cursor: pointer;
}

.table-row:hover {
  background: var(--bg-hover);
}

/* ============================
   CELL STYLES
   ============================ */
.customer-avatar {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: var(--font-size-xs);
  font-weight: 700;
  flex-shrink: 0;
  letter-spacing: 0.02em;
}

.customer-name {
  font-weight: 500;
  color: var(--text-primary);
  font-size: var(--font-size-sm);
  display: block;
  line-height: 1.3;
}

.vat-hint {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  display: block;
  margin-top: 1px;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
}

.type-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.25rem 0.625rem;
  font-size: var(--font-size-xs);
  font-weight: 500;
  border-radius: 9999px;
  white-space: nowrap;
}

.type-company {
  background: var(--primary-light);
  color: var(--primary-color);
}

.type-person {
  background: #fdf2f8;
  color: #db2777;
}

.email-text {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.city-text {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.linked-list {
  display: flex;
  gap: 0.375rem;
  align-items: center;
  flex-wrap: wrap;
}

.linked-tag {
  display: inline-flex;
  align-items: center;
  padding: 0.125rem 0.5rem;
  font-size: var(--font-size-xs);
  font-weight: 500;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  border-radius: 6px;
  white-space: nowrap;
}

.linked-more {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  font-weight: 600;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.375rem;
  color: var(--text-tertiary);
  border-radius: 6px;
  transition: all var(--transition-base);
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-icon:hover {
  background: #f0f2f5;
  color: var(--text-primary);
}

.table-footer {
  padding: 0.75rem 1rem;
  border-top: 1px solid var(--border-color);
}

.table-footer-info {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

/* ============================
   RESPONSIVE
   ============================ */
@media (max-width: 768px) {
  .header-content {
    flex-wrap: wrap;
    gap: 1rem;
  }
  .view-title {
    font-size: 1.5rem;
  }
  .filters-bar {
    flex-direction: column;
    align-items: stretch;
  }
  .search-box {
    max-width: 100%;
  }
  .filter-actions {
    flex-wrap: wrap;
  }
  .table-card {
    border-radius: 8px;
  }
}

@media (max-width: 480px) {
  .view-title {
    font-size: 1.25rem;
  }
  .header-actions .btn span {
    display: none;
  }
  .filter-actions .btn span {
    display: none;
  }
}
</style>
