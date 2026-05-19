<template>
  <div class="inventory-view">
    <!-- ── Header ──────────────────────────────────── -->
    <header class="view-header">
      <div class="header-left">
        <h1 class="view-title">Inventory</h1>
        <p class="view-subtitle">Manage stock, warehouses &amp; movements</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-secondary" @click="openAdjustModal(null)">
          <SlidersHorizontal :size="16" />
          <span class="btn-label">Adjust</span>
        </button>
        <button class="btn btn-secondary" @click="openTransferModal(null)">
          <ArrowLeftRight :size="16" />
          <span class="btn-label">Transfer</span>
        </button>
        <button class="btn btn-primary" @click="openRestockModal(null)">
          <PackagePlus :size="16" />
          <span class="btn-label">Restock</span>
        </button>
      </div>
    </header>

    <!-- ── Loading ─────────────────────────────────── -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading inventory data…</p>
    </div>

    <template v-else>
      <!-- ── KPI Row ─────────────────────────────── -->
      <section class="kpi-row">
        <div class="kpi-card">
          <div class="kpi-icon kpi-blue"><Package :size="22" /></div>
          <div class="kpi-info">
            <span class="kpi-value">{{ stats.total_products ?? 0 }}</span>
            <span class="kpi-label">Products</span>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon kpi-green"><Boxes :size="22" /></div>
          <div class="kpi-info">
            <span class="kpi-value">{{ fmt(stats.total_stock) }}</span>
            <span class="kpi-label">Total Units</span>
          </div>
        </div>
        <div class="kpi-card clickable" @click="goStockFiltered('low')">
          <div class="kpi-icon kpi-amber"><AlertTriangle :size="22" /></div>
          <div class="kpi-info">
            <span class="kpi-value">{{ stats.low_stock_count ?? 0 }}</span>
            <span class="kpi-label">Low Stock</span>
          </div>
        </div>
        <div class="kpi-card clickable" @click="goStockFiltered('out_of_stock')">
          <div class="kpi-icon kpi-red"><PackageX :size="22" /></div>
          <div class="kpi-info">
            <span class="kpi-value">{{ stats.out_of_stock_count ?? 0 }}</span>
            <span class="kpi-label">Out of Stock</span>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon kpi-purple"><Euro :size="22" /></div>
          <div class="kpi-info">
            <span class="kpi-value">{{ fmtCur(stats.total_value) }}</span>
            <span class="kpi-label">Inventory Value</span>
          </div>
        </div>
      </section>

      <!-- ── Tab Bar ─────────────────────────────── -->
      <nav class="tab-bar">
        <button
          v-for="t in tabs"
          :key="t.id"
          class="tab-btn"
          :class="{ active: activeTab === t.id }"
          @click="switchTab(t.id)"
        >
          <component :is="t.icon" :size="16" />
          <span>{{ t.label }}</span>
          <span v-if="t.badge" class="tab-badge" :class="t.badgeClass">{{ t.badge }}</span>
        </button>
      </nav>

      <!-- ════════════════════════════════════════════
           TAB: Warehouses (overview)
           ════════════════════════════════════════════ -->
      <div v-show="activeTab === 'warehouses'" class="tab-pane">
        <div class="inventory-grid">
          <!-- Warehouse Cards -->
          <section class="warehouses-panel">
            <div class="section-header">
              <h2 class="section-title"><Warehouse :size="20" /> Warehouses</h2>
              <button v-if="isAdmin" class="btn btn-primary btn-sm" @click="openWarehouseModal">
                <Plus :size="14" /> New Warehouse
              </button>
            </div>
            <div v-if="warehouses.length === 0" class="empty-state small">
              <Warehouse :size="40" />
              <p>No warehouses configured yet</p>
              <button v-if="isAdmin" class="btn btn-primary btn-sm" @click="openWarehouseModal">
                <Plus :size="14" /> Create Warehouse
              </button>
            </div>
            <div v-else class="warehouse-cards">
              <div
                v-for="wh in warehouses"
                :key="wh.id ?? 'unassigned'"
                class="warehouse-card"
                :class="{ 'has-alert': wh.low_stock > 0 }"
                @click="goWarehouseStock(wh)"
              >
                <div class="wh-header">
                  <div class="wh-name">
                    <div class="wh-avatar" :style="{ background: whColor(wh.id) }">
                      {{ wh.name.charAt(0).toUpperCase() }}
                    </div>
                    <div>
                      <h3>{{ wh.name }}</h3>
                      <span class="wh-address">{{ wh.address || 'No address' }}</span>
                    </div>
                  </div>
                  <div class="wh-actions">
                    <button
                      v-if="isAdmin && wh.id !== null"
                      class="btn-icon btn-danger-ghost"
                      title="Delete warehouse"
                      @click.stop="confirmDeleteWarehouse(wh)"
                    >
                      <Trash2 :size="15" />
                    </button>
                    <ChevronRight :size="16" class="wh-arrow" />
                  </div>
                </div>
                <div class="wh-stats">
                  <div class="wh-stat">
                    <span class="wh-stat-val">{{ wh.product_count }}</span>
                    <span class="wh-stat-lbl">Products</span>
                  </div>
                  <div class="wh-stat">
                    <span class="wh-stat-val">{{ fmt(wh.total_stock) }}</span>
                    <span class="wh-stat-lbl">Units</span>
                  </div>
                  <div class="wh-stat">
                    <span class="wh-stat-val" :class="{ 'text-warning': wh.low_stock > 0 }">{{ wh.low_stock }}</span>
                    <span class="wh-stat-lbl">Low Stock</span>
                  </div>
                  <div class="wh-stat">
                    <span class="wh-stat-val">{{ fmtCur(wh.value) }}</span>
                    <span class="wh-stat-lbl">Value</span>
                  </div>
                </div>
                <div class="wh-capacity">
                  <div class="capacity-bar">
                    <div class="capacity-fill" :style="{ width: whCapPct(wh) + '%' }" :class="capClass(wh)"></div>
                  </div>
                  <span class="capacity-label">{{ whCapPct(wh) }}% of total stock</span>
                </div>
              </div>
            </div>
          </section>

          <!-- Charts Column -->
          <div class="charts-column">
            <section class="chart-card">
              <h2 class="section-title"><BarChart3 :size="20" /> Stock by Category</h2>
              <div v-if="stockByCategory.length === 0" class="empty-state small">
                <p>No category data</p>
              </div>
              <div v-else class="bar-chart">
                <div v-for="cat in stockByCategory" :key="cat.category_name" class="bar-row">
                  <span class="bar-label">{{ cat.category_name }}</span>
                  <div class="bar-track">
                    <div class="bar-fill" :style="{ width: catPct(cat.total_stock) + '%', background: catColor(cat.category_name) }"></div>
                  </div>
                  <span class="bar-value">{{ fmt(cat.total_stock) }}</span>
                </div>
              </div>
            </section>
            <section class="chart-card">
              <h2 class="section-title"><ArrowUpDown :size="20" /> Movements (30 days)</h2>
              <div v-if="movementSummary.length === 0" class="empty-state small">
                <p>No movements recorded</p>
              </div>
              <div v-else class="movement-rings">
                <div v-for="mv in movementSummary" :key="mv.movement_type" class="ring-stat">
                  <div class="ring" :class="'ring-' + mv.movement_type.toLowerCase()">
                    <svg viewBox="0 0 36 36" class="ring-svg">
                      <path class="ring-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                      <path class="ring-fg" :stroke-dasharray="ringPct(mv) + ', 100'" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                    </svg>
                    <span class="ring-number">{{ mv.count }}</span>
                  </div>
                  <span class="ring-label">{{ mvLabel(mv.movement_type) }}</span>
                  <span class="ring-qty">{{ fmt(mv.total_qty) }} units</span>
                </div>
              </div>
            </section>
          </div>
        </div>
      </div>

      <!-- ════════════════════════════════════════════
           TAB: Stock (table)
           ════════════════════════════════════════════ -->
      <div v-show="activeTab === 'stock'" class="tab-pane">
        <div class="filters-bar">
          <div class="search-box">
            <Search :size="16" class="search-icon" />
            <input v-model="stockSearch" type="text" class="input search-input" placeholder="Search by name or SKU…" />
          </div>
          <select v-model="stockWarehouseFilter" class="input filter-select" @change="loadStock">
            <option value="all">All warehouses</option>
            <option v-for="wh in warehouses.filter(w => w.id)" :key="wh.id" :value="String(wh.id)">{{ wh.name }}</option>
            <option value="0">Unassigned</option>
          </select>
          <select v-model="stockStatusFilter" class="input filter-select" @change="loadStock">
            <option value="all">All statuses</option>
            <option value="ok">In Stock</option>
            <option value="low">Low Stock</option>
            <option value="out_of_stock">Out of Stock</option>
          </select>
        </div>

        <div class="card table-card">
          <div class="table-wrapper">
            <table class="table stock-table">
              <thead>
                <tr>
                  <th class="col-sku">SKU</th>
                  <th class="col-name">Product</th>
                  <th class="col-wh">Warehouse</th>
                  <th class="col-num">Stock</th>
                  <th class="col-num">Reserved</th>
                  <th class="col-num">Available</th>
                  <th class="col-num">Min</th>
                  <th class="col-status">Status</th>
                  <th class="col-num">Value</th>
                  <th class="col-actions">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="filteredStock.length === 0">
                  <td colspan="10" class="empty-row">
                    <PackageOpen :size="32" />
                    <span>No products match your filters</span>
                  </td>
                </tr>
                <tr v-for="p in filteredStock" :key="p.id" class="table-row">
                  <td class="col-sku"><span class="sku-text">{{ p.sku }}</span></td>
                  <td class="col-name">{{ p.name }}</td>
                  <td class="col-wh">{{ p.warehouse__name || 'Unassigned' }}</td>
                  <td class="col-num">
                    <span :class="stockNumClass(p)">{{ p.stock ?? 0 }}</span>
                  </td>
                  <td class="col-num">{{ p.reserved ?? 0 }}</td>
                  <td class="col-num"><strong>{{ (p.stock ?? 0) - (p.reserved ?? 0) }}</strong></td>
                  <td class="col-num">{{ p.min_stock ?? '—' }}</td>
                  <td class="col-status">
                    <span class="badge" :class="'badge-' + p.stock_status">{{ statusLabel(p.stock_status) }}</span>
                  </td>
                  <td class="col-num">{{ fmtCur((p.stock ?? 0) * (p.cost ?? 0)) }}</td>
                  <td class="col-actions">
                    <button class="btn-icon" title="Adjust stock" @click="openAdjustModal(p)">
                      <SlidersHorizontal :size="15" />
                    </button>
                    <button class="btn-icon" title="Transfer" @click="openTransferModal(p)">
                      <ArrowLeftRight :size="15" />
                    </button>
                    <button class="btn-icon primary" title="Restock" @click="openRestockModal(p)">
                      <PackagePlus :size="15" />
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="table-footer">
            Showing <strong>{{ filteredStock.length }}</strong> of <strong>{{ stockItems.length }}</strong> products
          </div>
        </div>
      </div>

      <!-- ════════════════════════════════════════════
           TAB: Movements
           ════════════════════════════════════════════ -->
      <div v-show="activeTab === 'movements'" class="tab-pane">
        <div class="filters-bar">
          <div class="search-box">
            <Search :size="16" class="search-icon" />
            <input v-model="mvSearch" type="text" class="input search-input" placeholder="Search product…" />
          </div>
          <select v-model="mvTypeFilter" class="input filter-select">
            <option value="all">All types</option>
            <option value="In">Entries</option>
            <option value="Out">Exits</option>
            <option value="Adjust">Adjustments</option>
            <option value="Return">Returns</option>
          </select>
        </div>

        <div class="card table-card">
          <div class="table-wrapper">
            <table class="table movements-table">
              <thead>
                <tr>
                  <th class="col-type">Type</th>
                  <th class="col-name">Product</th>
                  <th class="col-num">Qty</th>
                  <th class="col-ref">Reference</th>
                  <th class="col-user">User</th>
                  <th class="col-notes">Notes</th>
                  <th class="col-date">Date</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="filteredMovements.length === 0">
                  <td colspan="7" class="empty-row">
                    <ArrowUpDown :size="32" />
                    <span>No movements match your filters</span>
                  </td>
                </tr>
                <tr v-for="m in filteredMovements" :key="m.id" class="table-row">
                  <td class="col-type">
                    <span class="mv-badge" :class="'mv-' + m.movement_type.toLowerCase()">
                      <ArrowDownToLine v-if="m.movement_type === 'In'" :size="12" />
                      <ArrowUpFromLine v-else-if="m.movement_type === 'Out'" :size="12" />
                      <RefreshCw v-else-if="m.movement_type === 'Adjust'" :size="12" />
                      <CornerDownLeft v-else :size="12" />
                      {{ mvLabel(m.movement_type) }}
                    </span>
                  </td>
                  <td class="col-name">
                    <strong>{{ m.product_name }}</strong>
                    <span class="text-muted">{{ m.product_sku }}</span>
                  </td>
                  <td class="col-num">
                    <span :class="m.movement_type === 'Out' ? 'text-error' : 'text-success'">
                      {{ m.movement_type === 'Out' ? '−' : '+' }}{{ m.quantity }}
                    </span>
                  </td>
                  <td class="col-ref">{{ m.document_ref || '—' }}</td>
                  <td class="col-user">{{ m.user || '—' }}</td>
                  <td class="col-notes"><span class="notes-text">{{ m.notes || '—' }}</span></td>
                  <td class="col-date">{{ fmtRelTime(m.created_at) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="table-footer">
            Showing <strong>{{ filteredMovements.length }}</strong> movements
          </div>
        </div>
      </div>

      <!-- ════════════════════════════════════════════
           TAB: Reorder Rules
           ════════════════════════════════════════════ -->
      <div v-show="activeTab === 'rules'" class="tab-pane">
        <div class="rules-header">
          <p class="text-muted">Automatic reorder alerts when stock falls below the minimum threshold.</p>
          <button class="btn btn-primary btn-sm" @click="showNewRuleForm = true">
            <Plus :size="14" /> New Rule
          </button>
        </div>

        <div v-if="reorderRulesList.length === 0 && !showNewRuleForm" class="empty-state">
          <Settings :size="48" />
          <p>No reorder rules configured</p>
          <button class="btn btn-primary btn-sm" @click="showNewRuleForm = true">Create Rule</button>
        </div>

        <div v-else class="rules-grid">
          <div
            v-for="rule in reorderRulesList"
            :key="rule.id"
            class="rule-card"
            :class="{ 'needs-reorder': rule.needs_reorder }"
          >
            <div class="rule-top">
              <div>
                <h4>{{ rule.product_name }}</h4>
                <span class="rule-sku">{{ rule.product_sku }} · {{ rule.warehouse_name }}</span>
              </div>
              <span class="rule-toggle" :class="{ active: rule.enabled }">{{ rule.enabled ? 'Active' : 'Off' }}</span>
            </div>
            <div class="rule-params">
              <div class="rule-param">
                <span>Current</span>
                <strong :class="{ 'text-warning': rule.needs_reorder }">{{ rule.product_stock ?? 0 }}</strong>
              </div>
              <div class="rule-param">
                <span>Min</span>
                <strong>{{ rule.min_stock }}</strong>
              </div>
              <div class="rule-param">
                <span>Reorder</span>
                <strong>+{{ rule.reorder_qty }}</strong>
              </div>
              <div class="rule-param">
                <span>Max</span>
                <strong>{{ rule.max_stock ?? '—' }}</strong>
              </div>
            </div>
            <button
              v-if="rule.needs_reorder"
              class="btn btn-primary btn-sm rule-action"
              @click="quickRestock(rule)"
            >
              <PackagePlus :size="14" /> Restock {{ rule.reorder_qty }} units
            </button>
          </div>
        </div>

        <!-- New Rule Form -->
        <div v-if="showNewRuleForm" class="new-rule-form card">
          <h3>New Reorder Rule</h3>
          <div class="form-group">
            <label>Product</label>
            <select v-model="newRule.product_id" class="input">
              <option value="">Select product…</option>
              <option v-for="p in allProducts" :key="p.id" :value="p.id">{{ p.sku }} — {{ p.name }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>Warehouse</label>
            <select v-model="newRule.warehouse_id" class="input">
              <option value="">Select warehouse…</option>
              <option v-for="wh in warehouses.filter(w => w.id)" :key="wh.id" :value="wh.id">{{ wh.name }}</option>
            </select>
          </div>
          <div class="form-row-3">
            <div class="form-group">
              <label>Min Stock</label>
              <input v-model.number="newRule.min_stock" type="number" class="input" min="0" />
            </div>
            <div class="form-group">
              <label>Reorder Qty</label>
              <input v-model.number="newRule.reorder_qty" type="number" class="input" min="1" />
            </div>
            <div class="form-group">
              <label>Max Stock</label>
              <input v-model.number="newRule.max_stock" type="number" class="input" min="0" placeholder="Optional" />
            </div>
          </div>
          <div class="form-actions">
            <button class="btn btn-secondary btn-sm" @click="showNewRuleForm = false">Cancel</button>
            <button class="btn btn-primary btn-sm" @click="saveReorderRule" :disabled="!canSaveRule">Save Rule</button>
          </div>
        </div>
      </div>
    </template>

    <!-- ════════════════════════════════════════════════
         MODAL: New Warehouse
         ════════════════════════════════════════════════ -->
    <div v-if="deleteWarehouseModal" class="modal-overlay" @click.self="deleteWarehouseModal = false">
      <div class="modal-box modal-sm">
        <div class="modal-header">
          <h2>Delete Warehouse</h2>
          <button class="btn-icon" @click="deleteWarehouseModal = false"><X :size="18" /></button>
        </div>
        <div class="modal-body">
          <p>Are you sure you want to delete <strong>{{ warehouseToDelete?.name }}</strong>?</p>
          <p class="text-muted" style="font-size:0.85rem; margin-top:0.5rem;">Products assigned to this warehouse will become unassigned.</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="deleteWarehouseModal = false">Cancel</button>
          <button class="btn btn-danger" @click="doDeleteWarehouse">
            <Trash2 :size="16" /> Delete
          </button>
        </div>
      </div>
    </div>

    <div v-if="warehouseModal" class="modal-overlay" @click.self="warehouseModal = false">
      <div class="modal-box modal-sm">
        <div class="modal-header">
          <h2>New Warehouse</h2>
          <button class="btn-icon" @click="warehouseModal = false"><X :size="18" /></button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Name</label>
            <input v-model="warehouseData.name" type="text" class="input" placeholder="e.g. Main Warehouse" autofocus />
          </div>
          <div class="form-group">
            <label>Address <span class="optional">(optional)</span></label>
            <input v-model="warehouseData.address" type="text" class="input" placeholder="e.g. Calle Mayor 1, Madrid" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="warehouseModal = false">Cancel</button>
          <button class="btn btn-primary" @click="doCreateWarehouse" :disabled="!warehouseData.name.trim()">
            <Plus :size="16" /> Create
          </button>
        </div>
      </div>
    </div>

    <!-- ════════════════════════════════════════════════
         MODAL: Restock
         ════════════════════════════════════════════════ -->
    <div v-if="restockModal" class="modal-overlay" @click.self="restockModal = false">
      <div class="modal-box">
        <div class="modal-header">
          <h2>Restock Product</h2>
          <button class="btn-icon" @click="restockModal = false"><X :size="18" /></button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Product</label>
            <select v-if="!restockData.product_id" v-model="restockData.product_id" class="input" @change="onRestockProductChange">
              <option value="">Select product…</option>
              <option v-for="p in allProducts" :key="p.id" :value="p.id">{{ p.sku }} — {{ p.name }} ({{ p.stock ?? 0 }} units)</option>
            </select>
            <div v-else class="selected-product-info">
              <Package :size="18" />
              <div>
                <strong>{{ restockData.product_name }}</strong>
                <span>Current stock: {{ restockData.current_stock ?? 0 }}</span>
              </div>
            </div>
          </div>
          <div class="form-group">
            <label>Quantity to add</label>
            <input v-model.number="restockData.quantity" type="number" class="input" min="1" placeholder="e.g. 50" />
          </div>
          <div v-if="restockData.product_id && restockData.quantity > 0" class="preview-result">
            New stock: <strong>{{ (restockData.current_stock ?? 0) + restockData.quantity }}</strong> units
          </div>
          <div class="form-group">
            <label>Notes <span class="optional">(optional)</span></label>
            <input v-model="restockData.notes" type="text" class="input" placeholder="e.g. Supplier delivery #1234" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="restockModal = false">Cancel</button>
          <button class="btn btn-primary" @click="doRestock" :disabled="!restockData.product_id || !restockData.quantity || restockData.quantity <= 0">
            <PackagePlus :size="16" /> Restock
          </button>
        </div>
      </div>
    </div>

    <!-- ════════════════════════════════════════════════
         MODAL: Adjust Stock
         ════════════════════════════════════════════════ -->
    <div v-if="adjustModal" class="modal-overlay" @click.self="adjustModal = false">
      <div class="modal-box">
        <div class="modal-header">
          <h2>Adjust Stock</h2>
          <button class="btn-icon" @click="adjustModal = false"><X :size="18" /></button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Product</label>
            <select v-if="!adjustData.product_id" v-model="adjustData.product_id" class="input" @change="onAdjustProductChange">
              <option value="">Select product…</option>
              <option v-for="p in allProducts" :key="p.id" :value="p.id">{{ p.sku }} — {{ p.name }} ({{ p.stock ?? 0 }} units)</option>
            </select>
            <div v-else class="selected-product-info">
              <Package :size="18" />
              <div>
                <strong>{{ adjustData.product_name }}</strong>
                <span>Current stock: {{ adjustData.current_stock ?? 0 }}</span>
              </div>
            </div>
          </div>
          <div class="form-group">
            <label>Adjustment</label>
            <div class="adjust-row">
              <select v-model="adjustData.type" class="input adjust-type-select">
                <option value="add">Add (+)</option>
                <option value="remove">Remove (−)</option>
                <option value="set">Set to</option>
              </select>
              <input v-model.number="adjustData.quantity" type="number" class="input" min="0" placeholder="Quantity" />
            </div>
          </div>
          <div v-if="adjustData.product_id && adjustData.quantity >= 0" class="preview-result" :class="adjustPreviewClass">
            New stock: <strong>{{ adjustPreview }}</strong> units
            <span v-if="adjustDiff !== 0" class="diff">
              ({{ adjustDiff > 0 ? '+' : '' }}{{ adjustDiff }})
            </span>
          </div>
          <div class="form-group">
            <label>Reason</label>
            <select v-model="adjustData.reason" class="input">
              <option value="">Select reason…</option>
              <option value="Recount">Physical recount</option>
              <option value="Damage">Damage / breakage</option>
              <option value="Loss">Loss / shrinkage</option>
              <option value="Correction">Data correction</option>
              <option value="Return">Customer return</option>
              <option value="Other">Other</option>
            </select>
          </div>
          <div class="form-group">
            <label>Notes <span class="optional">(optional)</span></label>
            <input v-model="adjustData.notes" type="text" class="input" placeholder="Additional details…" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="adjustModal = false">Cancel</button>
          <button class="btn btn-primary" @click="doAdjust" :disabled="!canAdjust">
            <SlidersHorizontal :size="16" /> Apply Adjustment
          </button>
        </div>
      </div>
    </div>

    <!-- ════════════════════════════════════════════════
         MODAL: Transfer
         ════════════════════════════════════════════════ -->
    <div v-if="transferModal" class="modal-overlay" @click.self="transferModal = false">
      <div class="modal-box">
        <div class="modal-header">
          <h2>Transfer Stock</h2>
          <button class="btn-icon" @click="transferModal = false"><X :size="18" /></button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Product</label>
            <select v-if="!transferData.product_id" v-model="transferData.product_id" class="input" @change="onTransferProductChange">
              <option value="">Select product…</option>
              <option v-for="p in allProducts" :key="p.id" :value="p.id">{{ p.sku }} — {{ p.name }} ({{ p.stock ?? 0 }} units)</option>
            </select>
            <div v-else class="selected-product-info">
              <Package :size="18" />
              <div>
                <strong>{{ transferData.product_name }}</strong>
                <span>Current stock: {{ transferData.current_stock ?? 0 }}</span>
              </div>
            </div>
          </div>
          <div class="transfer-flow">
            <div class="form-group transfer-wh">
              <label>From</label>
              <select v-model="transferData.from_warehouse_id" class="input">
                <option value="">Select origin…</option>
                <option v-for="wh in warehouses.filter(w => w.id)" :key="wh.id" :value="wh.id">{{ wh.name }}</option>
              </select>
            </div>
            <div class="transfer-arrow"><ArrowRight :size="20" /></div>
            <div class="form-group transfer-wh">
              <label>To</label>
              <select v-model="transferData.to_warehouse_id" class="input">
                <option value="">Select destination…</option>
                <option
                  v-for="wh in warehouses.filter(w => w.id && w.id !== transferData.from_warehouse_id)"
                  :key="wh.id"
                  :value="wh.id"
                >{{ wh.name }}</option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <label>Quantity</label>
            <input v-model.number="transferData.quantity" type="number" class="input" min="1" :max="transferData.current_stock" placeholder="Units to transfer" />
          </div>
          <div class="form-group">
            <label>Notes <span class="optional">(optional)</span></label>
            <input v-model="transferData.notes" type="text" class="input" placeholder="e.g. Seasonal redistribution" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="transferModal = false">Cancel</button>
          <button class="btn btn-primary" @click="doTransfer" :disabled="!canTransfer">
            <ArrowLeftRight :size="16" /> Transfer
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import {
  Package, Boxes, AlertTriangle, PackageX, Euro,
  Warehouse, ChevronRight, BarChart3, ArrowUpDown,
  ClipboardList, X, PackagePlus, PackageOpen, Settings, Plus,
  ArrowDownToLine, ArrowUpFromLine, RefreshCw, CornerDownLeft,
  Search, SlidersHorizontal, ArrowLeftRight, ArrowRight, Trash2,
} from 'lucide-vue-next'
import inventoryApi from '@/services/inventory'
import productsApi from '@/services/products'
import coreApi from '@/services/core'
import { useToast } from '@/composables/useToast'

const toast = useToast()

// ── State ──────────────────────────────────────────
const loading = ref(true)
const activeTab = ref('warehouses')

// Overview data
const stats = ref({})
const warehouses = ref([])
const stockByCategory = ref([])
const movementSummary = ref([])

// Stock tab
const stockItems = ref([])
const stockSearch = ref('')
const stockWarehouseFilter = ref('all')
const stockStatusFilter = ref('all')

// Movements tab
const movements = ref([])
const mvSearch = ref('')
const mvTypeFilter = ref('all')

// Rules tab
const reorderRulesList = ref([])
const showNewRuleForm = ref(false)
const newRule = ref({ product_id: '', warehouse_id: '', min_stock: 10, reorder_qty: 25, max_stock: null })

// Product list for modals
const allProducts = ref([])

// Modals
const restockModal = ref(false)
const restockData = ref({ product_id: '', product_name: '', current_stock: 0, quantity: null, notes: '' })

const adjustModal = ref(false)
const adjustData = ref({ product_id: '', product_name: '', current_stock: 0, type: 'add', quantity: 0, reason: '', notes: '' })

const transferModal = ref(false)
const transferData = ref({ product_id: '', product_name: '', current_stock: 0, from_warehouse_id: '', to_warehouse_id: '', quantity: null, notes: '' })

// Warehouse modal
const warehouseModal = ref(false)
const warehouseData = ref({ name: '', address: '' })
const deleteWarehouseModal = ref(false)
const warehouseToDelete = ref(null)

// User role (admin check)
const isAdmin = ref(true) // defaults true; will be set from membership data

// ── Tabs Config ────────────────────────────────────
const tabs = computed(() => [
  { id: 'warehouses', label: 'Warehouses', icon: Warehouse },
  { id: 'stock', label: 'Stock', icon: ClipboardList },
  {
    id: 'movements', label: 'Movements', icon: ArrowUpDown,
    badge: movements.value.length || null,
  },
  {
    id: 'rules', label: 'Reorder Rules', icon: Settings,
    badge: reorderRulesList.value.filter(r => r.needs_reorder).length || null,
    badgeClass: reorderRulesList.value.some(r => r.needs_reorder) ? 'badge-warn' : '',
  },
])

// ── Computed ───────────────────────────────────────
const maxCatStock = computed(() => Math.max(...stockByCategory.value.map(c => c.total_stock), 1))
const totalMv = computed(() => Math.max(movementSummary.value.reduce((s, m) => s + m.count, 0), 1))

const filteredStock = computed(() => {
  const q = stockSearch.value.toLowerCase()
  return stockItems.value.filter(p => {
    if (q && !p.name.toLowerCase().includes(q) && !p.sku.toLowerCase().includes(q)) return false
    return true
  })
})

const filteredMovements = computed(() => {
  let list = movements.value
  const q = mvSearch.value.toLowerCase()
  if (q) list = list.filter(m => m.product_name.toLowerCase().includes(q) || m.product_sku.toLowerCase().includes(q))
  if (mvTypeFilter.value !== 'all') list = list.filter(m => m.movement_type === mvTypeFilter.value)
  return list
})

const canSaveRule = computed(() =>
  newRule.value.product_id && newRule.value.warehouse_id
  && newRule.value.min_stock >= 0 && newRule.value.reorder_qty > 0
)

const adjustPreview = computed(() => {
  const cur = adjustData.value.current_stock ?? 0
  const qty = adjustData.value.quantity ?? 0
  if (adjustData.value.type === 'add') return cur + qty
  if (adjustData.value.type === 'remove') return Math.max(cur - qty, 0)
  return Math.max(qty, 0) // 'set'
})

const adjustDiff = computed(() => adjustPreview.value - (adjustData.value.current_stock ?? 0))

const adjustPreviewClass = computed(() => {
  if (adjustDiff.value > 0) return 'preview-positive'
  if (adjustDiff.value < 0) return 'preview-negative'
  return ''
})

const canAdjust = computed(() =>
  adjustData.value.product_id && adjustData.value.quantity >= 0 && adjustData.value.reason
)

const canTransfer = computed(() =>
  transferData.value.product_id && transferData.value.from_warehouse_id
  && transferData.value.to_warehouse_id && transferData.value.quantity > 0
  && transferData.value.from_warehouse_id !== transferData.value.to_warehouse_id
)

// ── Lifecycle ──────────────────────────────────────
onMounted(async () => {
  loadUserRole()
  await loadOverview()
})

// Lazy-load tab data
watch(activeTab, (tab) => {
  if (tab === 'stock' && stockItems.value.length === 0) loadStock()
  if (tab === 'movements' && movements.value.length === 0) loadMovements()
  if (tab === 'rules' && reorderRulesList.value.length === 0) { loadReorderRules(); loadAllProducts() }
})

// Auto-load products when any modal opens
watch([restockModal, adjustModal, transferModal], () => { loadAllProducts() })

// ── Data Loading ───────────────────────────────────
async function loadOverview() {
  loading.value = true
  try {
    const data = await inventoryApi.getOverview()
    stats.value = data.global_stats
    warehouses.value = data.warehouses
    stockByCategory.value = data.stock_by_category
    movementSummary.value = data.movement_summary
  } catch {
    toast.error('Failed to load inventory data')
  } finally {
    loading.value = false
  }
}

async function loadStock() {
  try {
    const params = {}
    if (stockWarehouseFilter.value !== 'all') params.warehouse = stockWarehouseFilter.value
    if (stockStatusFilter.value !== 'all') params.stock_status = stockStatusFilter.value
    stockItems.value = await inventoryApi.getAllStock(params)
  } catch {
    toast.error('Failed to load stock data')
  }
}

async function loadMovements() {
  try {
    movements.value = await inventoryApi.getMovements(100)
  } catch {
    toast.error('Failed to load movements')
  }
}

async function loadReorderRules() {
  try {
    reorderRulesList.value = await inventoryApi.getReorderRules()
  } catch {
    toast.error('Failed to load reorder rules')
  }
}

async function loadAllProducts() {
  if (allProducts.value.length) return
  try {
    const res = await productsApi.getAll({ page_size: 500, status: 'Active', product_type: 'Product' })
    allProducts.value = res.results || res
  } catch (e) {
    console.error(e)
  }
}

function loadUserRole() {
  try {
    const stored = localStorage.getItem('membership')
    if (stored) {
      const membership = JSON.parse(stored)
      isAdmin.value = ['owner', 'admin'].includes(membership.role)
    }
  } catch { /* keep default */ }
}

// ── Tab / Navigation ───────────────────────────────
function switchTab(id) {
  activeTab.value = id
}

function goStockFiltered(status) {
  stockStatusFilter.value = status
  stockWarehouseFilter.value = 'all'
  activeTab.value = 'stock'
  loadStock()
}

function goWarehouseStock(wh) {
  stockWarehouseFilter.value = wh.id ? String(wh.id) : '0'
  stockStatusFilter.value = 'all'
  activeTab.value = 'stock'
  loadStock()
}

// ── Modal Openers ──────────────────────────────────
function openRestockModal(product) {
  restockData.value = {
    product_id: product?.id || '',
    product_name: product?.name || '',
    current_stock: product?.stock ?? 0,
    quantity: null,
    notes: '',
  }
  restockModal.value = true
}

function openAdjustModal(product) {
  adjustData.value = {
    product_id: product?.id || '',
    product_name: product?.name || '',
    current_stock: product?.stock ?? 0,
    type: 'add',
    quantity: 0,
    reason: '',
    notes: '',
  }
  adjustModal.value = true
}

function openTransferModal(product) {
  transferData.value = {
    product_id: product?.id || '',
    product_name: product?.name || '',
    current_stock: product?.stock ?? 0,
    from_warehouse_id: product?.warehouse__id || '',
    to_warehouse_id: '',
    quantity: null,
    notes: '',
  }
  transferModal.value = true
}

function onRestockProductChange() {
  const p = allProducts.value.find(x => x.id === restockData.value.product_id)
  if (p) { restockData.value.product_name = p.name; restockData.value.current_stock = p.stock ?? 0 }
}

function onAdjustProductChange() {
  const p = allProducts.value.find(x => x.id === adjustData.value.product_id)
  if (p) { adjustData.value.product_name = p.name; adjustData.value.current_stock = p.stock ?? 0 }
}

function onTransferProductChange() {
  const p = allProducts.value.find(x => x.id === transferData.value.product_id)
  if (p) { transferData.value.product_name = p.name; transferData.value.current_stock = p.stock ?? 0 }
}

// ── Actions ────────────────────────────────────────
async function doRestock() {
  try {
    await inventoryApi.restockProduct({
      product_id: restockData.value.product_id,
      quantity: restockData.value.quantity,
      notes: restockData.value.notes,
    })
    toast.success(`Restocked ${restockData.value.quantity} units`)
    restockModal.value = false
    await refreshAll()
  } catch {
    toast.error('Restock failed')
  }
}

async function doAdjust() {
  try {
    const res = await inventoryApi.adjustStock({
      product_id: adjustData.value.product_id,
      adjustment_type: adjustData.value.type,
      quantity: adjustData.value.quantity,
      reason: adjustData.value.reason,
      notes: adjustData.value.notes,
    })
    const diff = res.new_stock - res.old_stock
    toast.success(`Stock adjusted: ${res.old_stock} → ${res.new_stock} (${diff >= 0 ? '+' : ''}${diff})`)
    adjustModal.value = false
    await refreshAll()
  } catch {
    toast.error('Adjustment failed')
  }
}

async function doTransfer() {
  try {
    const res = await inventoryApi.transferStock({
      product_id: transferData.value.product_id,
      from_warehouse_id: transferData.value.from_warehouse_id,
      to_warehouse_id: transferData.value.to_warehouse_id,
      quantity: transferData.value.quantity,
      notes: transferData.value.notes,
    })
    toast.success(`Transferred ${res.quantity} units: ${res.from_warehouse} → ${res.to_warehouse}`)
    transferModal.value = false
    await refreshAll()
  } catch {
    toast.error('Transfer failed')
  }
}

async function saveReorderRule() {
  try {
    await inventoryApi.createReorderRule(newRule.value)
    toast.success('Reorder rule saved')
    showNewRuleForm.value = false
    newRule.value = { product_id: '', warehouse_id: '', min_stock: 10, reorder_qty: 25, max_stock: null }
    await loadReorderRules()
  } catch {
    toast.error('Failed to save rule')
  }
}

// ── Warehouse Delete ───────────────────────────────
function confirmDeleteWarehouse(wh) {
  warehouseToDelete.value = wh
  deleteWarehouseModal.value = true
}

async function doDeleteWarehouse() {
  const wh = warehouseToDelete.value
  if (!wh) return
  try {
    await coreApi.warehouses.delete(wh.id)
    toast.success(`Warehouse "${wh.name}" deleted`)
    deleteWarehouseModal.value = false
    warehouseToDelete.value = null
    await loadOverview()
  } catch {
    toast.error('Failed to delete warehouse')
  }
}

// ── Warehouse Creation ─────────────────────────────
function openWarehouseModal() {
  warehouseData.value = { name: '', address: '' }
  warehouseModal.value = true
}

async function doCreateWarehouse() {
  const name = warehouseData.value.name.trim()
  if (!name) return
  try {
    await coreApi.warehouses.create({ name, address: warehouseData.value.address.trim() })
    toast.success(`Warehouse "${name}" created`)
    warehouseModal.value = false
    await loadOverview()
  } catch {
    toast.error('Failed to create warehouse')
  }
}

async function quickRestock(rule) {
  try {
    await inventoryApi.restockProduct({
      product_id: rule.product_id,
      quantity: rule.reorder_qty,
      notes: `Auto-restock via rule #${rule.id}`,
    })
    toast.success(`Restocked ${rule.reorder_qty} units of ${rule.product_name}`)
    await refreshAll()
    await loadReorderRules()
  } catch {
    toast.error('Restock failed')
  }
}

async function refreshAll() {
  await loadOverview()
  if (stockItems.value.length) await loadStock()
  if (movements.value.length) await loadMovements()
}

// ── Helpers ────────────────────────────────────────
function fmt(n) { return (n ?? 0).toLocaleString('es-ES') }
function fmtCur(n) { return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(n ?? 0) }

const WH_COLORS = ['#667eea', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#ef4444', '#06b6d4']
function whColor(id) { return id === null ? '#94a3b8' : WH_COLORS[(id - 1) % WH_COLORS.length] }

function whCapPct(wh) {
  const total = stats.value.total_stock || 1
  return Math.min(Math.round((wh.total_stock / total) * 100), 100)
}
function capClass(wh) {
  const p = whCapPct(wh)
  return p >= 80 ? 'cap-high' : p >= 50 ? 'cap-med' : 'cap-low'
}

function catPct(stock) { return Math.round((stock / maxCatStock.value) * 100) }
const CAT_COLORS = ['#667eea', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#ef4444', '#06b6d4', '#84cc16']
function catColor(name) {
  let h = 0
  for (const c of name) h = c.charCodeAt(0) + ((h << 5) - h)
  return CAT_COLORS[Math.abs(h) % CAT_COLORS.length]
}

function ringPct(mv) { return Math.round((mv.count / totalMv.value) * 100) }
function mvLabel(t) { return { In: 'Entries', Out: 'Exits', Adjust: 'Adjustments', Return: 'Returns' }[t] || t }
function statusLabel(s) { return { ok: 'In Stock', low: 'Low Stock', out_of_stock: 'Out of Stock' }[s] || s }

function stockNumClass(p) {
  if (p.stock_status === 'out_of_stock') return 'text-error font-bold'
  if (p.stock_status === 'low') return 'text-warning font-bold'
  return 'font-bold'
}

function fmtRelTime(iso) {
  const d = Date.now() - new Date(iso).getTime()
  const m = Math.floor(d / 60000)
  if (m < 1) return 'just now'
  if (m < 60) return `${m}m ago`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}h ago`
  return `${Math.floor(h / 24)}d ago`
}
</script>

<style scoped>
/* ── Layout ─────────────────────────────────────── */
.inventory-view {
  width: 100%;
}

.view-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: var(--spacing-lg);
  flex-wrap: wrap;
  gap: var(--spacing-md);
}
.view-title { font-size: var(--font-size-2xl); font-weight: 700; color: var(--text-primary); }
.view-subtitle { font-size: var(--font-size-sm); color: var(--text-secondary); margin-top: 2px; }
.header-actions { display: flex; gap: var(--spacing-sm); flex-wrap: wrap; }
.header-actions .btn { display: inline-flex; align-items: center; gap: 6px; }

/* ── Loading ────────────────────────────────────── */
.loading-state {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 80px 0; color: var(--text-secondary); gap: var(--spacing-md);
}
.spinner {
  width: 36px; height: 36px; border: 3px solid var(--border-color);
  border-top-color: var(--primary-color); border-radius: 50%; animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── KPI Row ────────────────────────────────────── */
.kpi-row {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}
.kpi-card {
  background: var(--bg-primary); border: 1px solid var(--border-color);
  border-radius: var(--border-radius); padding: var(--spacing-md) var(--spacing-lg);
  display: flex; align-items: center; gap: var(--spacing-md);
  transition: box-shadow var(--transition-fast);
}
.kpi-card:hover { box-shadow: var(--shadow-md); }
.kpi-card.clickable { cursor: pointer; }
.kpi-card.clickable:hover { border-color: var(--primary-color); }
.kpi-icon {
  width: 44px; height: 44px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.kpi-blue { background: var(--info-light); color: var(--info-color); }
.kpi-green { background: var(--success-light); color: var(--success-color); }
.kpi-amber { background: var(--warning-light); color: var(--warning-color); }
.kpi-red { background: var(--error-light); color: var(--error-color); }
.kpi-purple { background: #ede9fe; color: var(--accent-purple); }
.kpi-info { display: flex; flex-direction: column; }
.kpi-value { font-size: var(--font-size-xl); font-weight: 700; color: var(--text-primary); line-height: 1.2; }
.kpi-label { font-size: var(--font-size-xs); color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px; }

/* ── Tabs ───────────────────────────────────────── */
.tab-bar {
  display: flex; gap: 2px; border-bottom: 2px solid var(--border-color);
  margin-bottom: var(--spacing-lg); overflow-x: auto;
}
.tab-btn {
  display: flex; align-items: center; gap: 6px;
  padding: 0.625rem 1rem; border: none; background: none;
  font-size: var(--font-size-sm); font-weight: 500; font-family: var(--font-family);
  color: var(--text-secondary); cursor: pointer; white-space: nowrap;
  border-bottom: 2px solid transparent; margin-bottom: -2px;
  transition: all var(--transition-fast);
}
.tab-btn:hover { color: var(--text-primary); background: var(--bg-hover); }
.tab-btn.active { color: var(--primary-color); border-bottom-color: var(--primary-color); }
.tab-badge {
  font-size: 10px; font-weight: 700; padding: 1px 6px; border-radius: 999px;
  background: var(--bg-secondary); color: var(--text-secondary);
}
.tab-badge.badge-warn { background: var(--warning-light); color: var(--warning-color); }

/* ── Warehouses Tab ─────────────────────────────── */
.inventory-grid {
  display: grid; grid-template-columns: 1fr 380px; gap: var(--spacing-lg);
}
.section-title {
  font-size: var(--font-size-base); font-weight: 600; color: var(--text-primary);
  display: flex; align-items: center; gap: 8px; margin-bottom: var(--spacing-md);
}

/* Warehouse section header */
.section-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: var(--spacing-md);
}
.section-header .section-title { margin-bottom: 0; }

/* Warehouse Cards */
.warehouse-cards { display: flex; flex-direction: column; gap: var(--spacing-sm); }
.warehouse-card {
  background: var(--bg-primary); border: 1px solid var(--border-color);
  border-radius: var(--border-radius); padding: var(--spacing-md);
  cursor: pointer; transition: all var(--transition-fast);
}
.warehouse-card:hover { box-shadow: var(--shadow-md); border-color: var(--primary-color); }
.warehouse-card.has-alert { border-left: 3px solid var(--warning-color); }
.wh-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--spacing-sm); }
.wh-name { display: flex; align-items: center; gap: var(--spacing-sm); }
.wh-avatar {
  width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center;
  justify-content: center; font-weight: 700; font-size: var(--font-size-sm); color: white; flex-shrink: 0;
}
.wh-name h3 { font-size: var(--font-size-sm); font-weight: 600; }
.wh-address { font-size: var(--font-size-xs); color: var(--text-tertiary); }
.wh-actions { display: flex; align-items: center; gap: 4px; }
.wh-arrow { color: var(--text-tertiary); transition: transform var(--transition-fast); }
.warehouse-card:hover .wh-arrow { transform: translateX(3px); color: var(--primary-color); }
.btn-danger { background: #ef4444; color: #fff; border: none; }
.btn-danger:hover { background: #dc2626; }
.btn-danger-ghost { background: transparent; border: none; cursor: pointer; padding: 4px; border-radius: var(--radius-sm); color: var(--text-tertiary); display: flex; align-items: center; transition: color var(--transition-fast), background var(--transition-fast); }
.btn-danger-ghost:hover { color: var(--danger-color, #ef4444); background: rgba(239,68,68,0.1); }
.wh-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--spacing-xs); margin-bottom: var(--spacing-sm); }
.wh-stat { text-align: center; }
.wh-stat-val { display: block; font-size: var(--font-size-sm); font-weight: 700; color: var(--text-primary); }
.wh-stat-lbl { font-size: 10px; color: var(--text-tertiary); text-transform: uppercase; letter-spacing: 0.3px; }
.text-warning { color: var(--warning-color) !important; }
.wh-capacity { margin-top: 4px; }
.capacity-bar { height: 4px; background: var(--bg-secondary); border-radius: 2px; overflow: hidden; }
.capacity-fill { height: 100%; border-radius: 2px; transition: width 0.6s ease; }
.cap-low { background: var(--success-color); }
.cap-med { background: var(--warning-color); }
.cap-high { background: var(--error-color); }
.capacity-label { font-size: 10px; color: var(--text-tertiary); margin-top: 2px; display: block; }

/* Charts Column */
.charts-column { display: flex; flex-direction: column; gap: var(--spacing-lg); }
.chart-card {
  background: var(--bg-primary); border: 1px solid var(--border-color);
  border-radius: var(--border-radius); padding: var(--spacing-md);
}
.bar-chart { display: flex; flex-direction: column; gap: 10px; }
.bar-row { display: grid; grid-template-columns: 100px 1fr 50px; align-items: center; gap: 8px; }
.bar-label { font-size: var(--font-size-xs); color: var(--text-secondary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.bar-track { height: 20px; background: var(--bg-secondary); border-radius: 4px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 4px; transition: width 0.6s ease; min-width: 4px; }
.bar-value { font-size: var(--font-size-xs); font-weight: 600; color: var(--text-primary); text-align: right; }

/* Movement rings */
.movement-rings { display: grid; grid-template-columns: repeat(auto-fit, minmax(80px, 1fr)); gap: var(--spacing-md); text-align: center; }
.ring { position: relative; width: 70px; height: 70px; margin: 0 auto; }
.ring-svg { width: 100%; height: 100%; transform: rotate(-90deg); }
.ring-svg .ring-bg { fill: none; stroke: var(--bg-secondary); stroke-width: 3; }
.ring-svg .ring-fg { fill: none; stroke-width: 3; stroke-linecap: round; transition: stroke-dasharray 0.6s ease; }
.ring-in .ring-fg { stroke: var(--success-color); }
.ring-out .ring-fg { stroke: var(--error-color); }
.ring-adjust .ring-fg { stroke: var(--warning-color); }
.ring-return .ring-fg { stroke: var(--info-color); }
.ring-number { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: var(--font-size-base); font-weight: 700; color: var(--text-primary); }
.ring-label { display: block; font-size: var(--font-size-xs); color: var(--text-secondary); margin-top: 6px; }
.ring-qty { display: block; font-size: 10px; color: var(--text-tertiary); }

/* ── Stock & Movements Tabs ─────────────────────── */
.filters-bar {
  display: flex; align-items: center; gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md); flex-wrap: wrap;
}
.search-box { position: relative; flex: 1; min-width: 200px; max-width: 360px; }
.search-box .search-icon { position: absolute; left: 10px; top: 50%; transform: translateY(-50%); color: var(--text-tertiary); pointer-events: none; }
.search-input { padding-left: 2rem !important; }
.filter-select { width: auto; min-width: 150px; max-width: 200px; }

.table-card { overflow: hidden; }
.table-wrapper { overflow-x: auto; }
.table { width: 100%; border-collapse: collapse; font-size: var(--font-size-sm); }
.table thead { background: var(--bg-secondary); }
.table th {
  padding: 0.625rem 0.75rem; text-align: left; font-weight: 600;
  color: var(--text-secondary); font-size: var(--font-size-xs);
  text-transform: uppercase; letter-spacing: 0.3px; white-space: nowrap;
}
.table td { padding: 0.625rem 0.75rem; border-bottom: 1px solid var(--bg-secondary); }
.table-row { transition: background var(--transition-fast); }
.table-row:hover { background: var(--bg-hover); }
.table-footer {
  padding: 0.5rem 0.75rem; font-size: var(--font-size-xs);
  color: var(--text-secondary); border-top: 1px solid var(--border-color);
}

.col-sku { min-width: 80px; }
.col-name { min-width: 160px; }
.col-wh { min-width: 120px; }
.col-num { min-width: 70px; white-space: nowrap; }
.col-status { min-width: 100px; }
.col-actions { min-width: 100px; white-space: nowrap; }
.col-type { min-width: 110px; }
.col-ref { min-width: 110px; }
.col-user { min-width: 90px; }
.col-notes { min-width: 140px; max-width: 240px; }
.col-date { min-width: 80px; white-space: nowrap; }

.sku-text { font-family: monospace; font-size: var(--font-size-xs); color: var(--text-secondary); }
.notes-text { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; display: block; max-width: 240px; }

.empty-row {
  text-align: center; padding: 2rem !important; color: var(--text-tertiary);
}
.empty-row span { display: block; margin-top: var(--spacing-sm); }

/* Stock actions */
.btn-icon {
  background: none; border: 1px solid var(--border-color); border-radius: 6px;
  width: 28px; height: 28px; display: inline-flex; align-items: center; justify-content: center;
  color: var(--text-secondary); cursor: pointer; transition: all var(--transition-fast); margin-right: 2px;
}
.btn-icon:hover { background: var(--bg-hover); color: var(--text-primary); border-color: var(--text-tertiary); }
.btn-icon.primary:hover { background: var(--primary-light); color: var(--primary-color); border-color: var(--primary-color); }

/* Badges */
.badge {
  display: inline-block; font-size: 10px; font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.5px; padding: 2px 8px; border-radius: 999px; white-space: nowrap;
}
.badge-ok { background: var(--success-light); color: var(--success-color); }
.badge-low { background: var(--warning-light); color: var(--warning-color); }
.badge-out_of_stock { background: var(--error-light); color: var(--error-color); }

/* Movement badges */
.mv-badge {
  display: inline-flex; align-items: center; gap: 4px; font-size: 10px; font-weight: 600;
  padding: 3px 8px; border-radius: 999px; white-space: nowrap;
}
.mv-in { background: var(--success-light); color: var(--success-color); }
.mv-out { background: var(--error-light); color: var(--error-color); }
.mv-adjust { background: var(--warning-light); color: var(--warning-color); }
.mv-return { background: var(--info-light); color: var(--info-color); }
.text-muted { display: block; font-size: var(--font-size-xs); color: var(--text-tertiary); }
.text-error { color: var(--error-color); }
.text-success { color: var(--success-color); }
.font-bold { font-weight: 700; }

/* ── Reorder Rules Tab ──────────────────────────── */
.rules-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: var(--spacing-md); flex-wrap: wrap; gap: var(--spacing-sm);
}
.rules-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: var(--spacing-md); }
.rule-card {
  background: var(--bg-secondary); border-radius: var(--border-radius-sm);
  padding: var(--spacing-sm) var(--spacing-md);
}
.rule-card.needs-reorder { background: #fff7ed; border: 1px solid #fed7aa; }
.rule-top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px; }
.rule-top h4 { font-size: var(--font-size-sm); font-weight: 600; }
.rule-sku { font-size: var(--font-size-xs); color: var(--text-tertiary); }
.rule-toggle {
  font-size: 10px; font-weight: 600; text-transform: uppercase;
  padding: 2px 8px; border-radius: 999px; background: var(--bg-primary); color: var(--text-tertiary);
}
.rule-toggle.active { background: var(--success-light); color: var(--success-color); }
.rule-params { display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px; text-align: center; margin-bottom: 6px; }
.rule-param span { display: block; font-size: 10px; color: var(--text-tertiary); }
.rule-param strong { font-size: var(--font-size-xs); }
.rule-action { width: 100%; margin-top: 4px; }

/* New rule form */
.new-rule-form { padding: var(--spacing-md); margin-top: var(--spacing-md); }
.new-rule-form h3 { font-size: var(--font-size-sm); font-weight: 600; margin-bottom: var(--spacing-sm); }
.form-row-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--spacing-sm); }
.form-actions { display: flex; justify-content: flex-end; gap: var(--spacing-sm); margin-top: var(--spacing-sm); }

/* ── Empty State ────────────────────────────────── */
.empty-state {
  text-align: center; padding: 48px 20px; color: var(--text-tertiary);
  display: flex; flex-direction: column; align-items: center; gap: var(--spacing-sm);
}
.empty-state.small { padding: 24px 12px; }

/* ── Modals ─────────────────────────────────────── */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0, 0, 0, 0.4);
  display: flex; align-items: center; justify-content: center;
  z-index: 1200; backdrop-filter: blur(2px);
}
.modal-box {
  background: var(--bg-primary); border-radius: var(--border-radius-lg);
  width: 100%; max-width: 520px; box-shadow: var(--shadow-lg);
  overflow: hidden; max-height: 90vh; display: flex; flex-direction: column;
  margin: var(--spacing-md);
}
.modal-box.modal-sm { max-width: 420px; }
.modal-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: var(--spacing-md) var(--spacing-lg); border-bottom: 1px solid var(--border-color);
}
.modal-header h2 { font-size: var(--font-size-lg); font-weight: 700; }
.modal-body { padding: var(--spacing-lg); overflow-y: auto; }
.modal-footer {
  display: flex; justify-content: flex-end; gap: var(--spacing-sm);
  padding: var(--spacing-md) var(--spacing-lg); border-top: 1px solid var(--border-color);
}

/* Form elements */
.form-group { margin-bottom: var(--spacing-md); }
.form-group label {
  display: block; font-size: var(--font-size-xs); font-weight: 600;
  color: var(--text-secondary); margin-bottom: 4px;
}
.optional { font-weight: 400; color: var(--text-tertiary); }
.input {
  width: 100%; padding: 8px 12px; border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm); font-size: var(--font-size-sm);
  font-family: var(--font-family); color: var(--text-primary); background: var(--bg-primary);
  transition: border-color var(--transition-fast);
}
.input:focus { outline: none; border-color: var(--primary-color); box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.15); }
select.input { appearance: none; cursor: pointer; background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2394a3b8' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E"); background-repeat: no-repeat; background-position: right 10px center; padding-right: 28px; }

.selected-product-info {
  display: flex; align-items: center; gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md); background: var(--bg-secondary);
  border-radius: var(--border-radius-sm);
}
.selected-product-info div { display: flex; flex-direction: column; }
.selected-product-info strong { font-size: var(--font-size-sm); }
.selected-product-info span { font-size: var(--font-size-xs); color: var(--text-secondary); }

.preview-result {
  padding: var(--spacing-sm) var(--spacing-md); border-radius: var(--border-radius-sm);
  background: var(--bg-secondary); font-size: var(--font-size-sm);
  margin-bottom: var(--spacing-md); color: var(--text-primary);
}
.preview-result .diff { font-weight: 600; margin-left: 4px; }
.preview-positive { background: var(--success-light); }
.preview-positive .diff { color: var(--success-color); }
.preview-negative { background: var(--error-light); }
.preview-negative .diff { color: var(--error-color); }

.adjust-row { display: grid; grid-template-columns: 140px 1fr; gap: var(--spacing-sm); }
.adjust-type-select { min-width: 0; }

/* Transfer flow */
.transfer-flow {
  display: flex; align-items: flex-end; gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
}
.transfer-wh { flex: 1; margin-bottom: 0; }
.transfer-arrow {
  display: flex; align-items: center; justify-content: center;
  color: var(--primary-color); padding-bottom: 8px; flex-shrink: 0;
}

/* ── Buttons ────────────────────────────────────── */
.btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 8px 16px; border-radius: var(--border-radius-sm);
  font-size: var(--font-size-sm); font-weight: 500; cursor: pointer;
  border: none; transition: all var(--transition-fast); font-family: var(--font-family);
}
.btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
.btn-primary:hover { opacity: 0.9; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-secondary { background: var(--bg-primary); color: var(--text-primary); border: 1px solid var(--border-color); }
.btn-secondary:hover { background: var(--bg-hover); }
.btn-sm { padding: 6px 12px; font-size: var(--font-size-xs); }

.card {
  background: var(--bg-primary); border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
}

/* ── Responsive ─────────────────────────────────── */
@media (max-width: 1200px) {
  .inventory-grid { grid-template-columns: 1fr; }
  .charts-column { display: grid; grid-template-columns: 1fr 1fr; }
}

@media (max-width: 768px) {
  .kpi-row { grid-template-columns: repeat(2, 1fr); }
  .kpi-row .kpi-card:last-child { grid-column: span 2; }
  .charts-column { grid-template-columns: 1fr; }
  .header-actions .btn-label { display: none; }
  .wh-stats { grid-template-columns: repeat(2, 1fr); }
  .filters-bar { flex-direction: column; align-items: stretch; }
  .search-box { max-width: 100%; }
  .filter-select { max-width: 100%; }
  .rules-grid { grid-template-columns: 1fr; }
  .form-row-3 { grid-template-columns: 1fr; }
  .adjust-row { grid-template-columns: 1fr; }
  .transfer-flow { flex-direction: column; align-items: stretch; }
  .transfer-arrow { transform: rotate(90deg); padding: 0; }
}

@media (max-width: 480px) {
  .kpi-row { grid-template-columns: 1fr; }
  .kpi-row .kpi-card:last-child { grid-column: span 1; }
  .kpi-card { padding: var(--spacing-sm) var(--spacing-md); }
  .tab-btn span { display: none; }
  .tab-btn { padding: 0.5rem 0.75rem; }
  .modal-box { max-width: 100%; margin: var(--spacing-sm); }
}
</style>
