<template>
  <SocialHubLayout
    title="Campanyes"
    subtitle="Planificació, rendiment i cronologia de les campanyes a les xarxes socials."
    :tabs="tabs"
    v-model="activeTab"
  >
    <template #actions>
      <button class="hub-btn hub-btn-primary" @click="openCreateModal">
        <Plus :size="15" />
        <span>Nova campanya</span>
      </button>
    </template>

    <!-- ── KPI strip ─────────────────────────────────────────── -->
    <div class="kpi-strip">
      <div class="kpi-tile">
        <div class="kpi-key">Actives</div>
        <div class="kpi-val">{{ kpis.active }}<span class="kpi-suffix">/{{ kpis.total }}</span></div>
        <div class="kpi-sub">{{ kpis.draft }} en esborrany · {{ kpis.completed }} tancades</div>
      </div>
      <div class="kpi-tile">
        <div class="kpi-key">Pressupost actiu</div>
        <div class="kpi-val">{{ formatCurrency(kpis.activeBudget) }}</div>
        <div class="kpi-sub">{{ formatCurrency(kpis.activeSpent) }} gastat</div>
      </div>
      <div class="kpi-tile">
        <div class="kpi-key">Vendes atribuïdes</div>
        <div class="kpi-val">{{ formatCurrency(kpis.totalSales) }}</div>
        <div class="kpi-sub">en {{ kpis.totalConversions }} conversions</div>
      </div>
      <div class="kpi-tile">
        <div class="kpi-key">ROAS mitjà</div>
        <div class="kpi-val">
          <span :class="roasClass(kpis.avgRoas)">{{ kpis.avgRoas.toFixed(2) }}x</span>
        </div>
        <div class="kpi-sub">{{ kpis.bestCampaign?.name || '—' }} top</div>
      </div>
    </div>

    <!-- ════════════════════════════════════════════════════════════
         TAB 1 · LISTA
       ════════════════════════════════════════════════════════════ -->
    <section v-if="activeTab === 'list'" class="tab-section">
      <div class="filters-row">
        <div class="search-input-wrap">
          <Search :size="15" class="search-icon" />
          <input
            v-model="searchQ"
            class="filter-input search-input"
            placeholder="Cerca una campanya..."
          />
        </div>
        <select v-model="statusFilter" class="filter-input">
          <option value="all">Tots els estats</option>
          <option v-for="(s, k) in CAMPAIGN_STATUSES" :key="k" :value="k">{{ s.label }}</option>
        </select>
        <select v-model="objectiveFilter" class="filter-input">
          <option value="all">Tots els objectius</option>
          <option v-for="o in CAMPAIGN_OBJECTIVES" :key="o" :value="o">{{ o }}</option>
        </select>
        <select v-model="sortKey" class="filter-input">
          <option value="recent">Més recents</option>
          <option value="sales">Més vendes</option>
          <option value="roas">Millor ROAS</option>
          <option value="budget">Més pressupost</option>
        </select>
        <div class="result-count">{{ filteredCampaigns.length }} campanyes</div>
        <div class="view-toggle">
          <button class="vt-btn" :class="{ active: viewMode === 'table' }" title="Vista taula" @click="viewMode = 'table'">
            <List :size="14" />
          </button>
          <button class="vt-btn" :class="{ active: viewMode === 'cards' }" title="Vista targetes" @click="viewMode = 'cards'">
            <LayoutGrid :size="14" />
          </button>
        </div>
      </div>

      <!-- Vista tabla -->
      <div v-if="viewMode === 'table'" class="data-card">
        <div class="data-head head-campaigns">
          <div class="th">Campanya</div>
          <div class="th">Estat</div>
          <div class="th">Objectiu</div>
          <div class="th">Període</div>
          <div class="th th-num">Pressupost</div>
          <div class="th th-num">Vendes</div>
          <div class="th th-num">ROAS</div>
        </div>
        <div class="data-rows">
          <div
            v-for="c in filteredCampaigns"
            :key="c.id"
            class="data-row row-campaign"
            role="button"
            tabindex="0"
            @click="openCampaign(c.id)"
            @keydown.enter="openCampaign(c.id)"
          >
            <div class="cell cell-campaign">
              <div class="camp-name-block">
                <div class="row-name">{{ c.name }}</div>
                <div class="row-alias">{{ c.description || '—' }}</div>
              </div>
            </div>
            <div class="cell">
              <span class="badge" :class="CAMPAIGN_STATUSES[c.status].cls">
                {{ CAMPAIGN_STATUSES[c.status].label }}
              </span>
            </div>
            <div class="cell muted">{{ c.objective }}</div>
            <div class="cell muted font-mono">
              {{ formatDateShort(c.startDate) }} → {{ formatDateShort(c.endDate) }}
            </div>
            <div class="cell cell-num">
              <div class="budget-cell">
                <span class="font-mono">{{ formatCurrency(c.cost) }}<span class="budget-of"> / {{ formatCurrency(c.budget) }}</span></span>
                <div class="budget-bar-wrap">
                  <div class="budget-bar" :style="{ width: Math.min(budgetPct(c), 100) + '%' }" :class="{ 'cb-warn': budgetPct(c) > 90 && budgetPct(c) <= 100, 'cb-over': budgetPct(c) > 100 }"></div>
                </div>
              </div>
            </div>
            <div class="cell cell-num font-mono">{{ formatCurrency(c.sales) }}</div>
            <div class="cell cell-num">
              <span class="roas-pill" :class="roasClass(c.roas)">{{ c.roas.toFixed(2) }}x</span>
            </div>
            <button class="row-del-btn" title="Esborrar campanya" @click.stop="confirmDelete(c)">
              <Trash2 :size="15" />
            </button>
          </div>
          <div v-if="!filteredCampaigns.length" class="empty-grid">
            <Frown :size="20" />
            <span>No hi ha campanyes amb aquests filtres.</span>
          </div>
        </div>
      </div>

      <div v-if="viewMode === 'cards'">
      <div class="campaigns-grid">
        <article
          v-for="c in filteredCampaigns"
          :key="c.id"
          class="campaign-card"
          :class="{ ['st-' + c.status]: true }"
          @click="openCampaign(c.id)"
        >
          <header class="cc-head">
            <span class="badge" :class="CAMPAIGN_STATUSES[c.status].cls">
              {{ CAMPAIGN_STATUSES[c.status].label }}
            </span>
            <span class="objective-tag">{{ c.objective }}</span>
            <button class="cc-del-btn" title="Esborrar campanya" @click.stop="confirmDelete(c)">
              <Trash2 :size="14" />
            </button>
          </header>

          <h3 class="cc-name">{{ c.name }}</h3>

          <div class="cc-period">
            <Calendar :size="12" />
            <span>{{ formatDateShort(c.startDate) }} → {{ formatDateShort(c.endDate) }}</span>
          </div>

          <p v-if="c.description" class="cc-desc">{{ c.description }}</p>

          <!-- Mini KPIs -->
          <div class="cc-stats">
            <div class="cc-stat">
              <div class="cs-val font-mono">{{ c.posts }}</div>
              <div class="cs-key">Posts</div>
            </div>
            <div class="cc-stat">
              <div class="cs-val font-mono">{{ c.influencers }}</div>
              <div class="cs-key">Influencers</div>
            </div>
            <div class="cc-stat">
              <div class="cs-val font-mono">{{ formatCurrency(c.sales) }}</div>
              <div class="cs-key">Vendes</div>
            </div>
            <div class="cc-stat">
              <div class="cs-val">
                <span class="roas-pill" :class="roasClass(c.roas)">{{ c.roas.toFixed(2) }}x</span>
              </div>
              <div class="cs-key">ROAS</div>
            </div>
          </div>

          <!-- Budget bar -->
          <div class="cc-budget">
            <div class="cb-row">
              <span class="cb-label">Pressupost</span>
              <span class="cb-val font-mono">
                {{ formatCurrency(c.cost) }}
                <span class="cb-of">/ {{ formatCurrency(c.budget) }}</span>
              </span>
            </div>
            <div class="cb-bar-wrap">
              <div
                class="cb-bar"
                :style="{ width: budgetPct(c) + '%' }"
                :class="{
                  'cb-warn': budgetPct(c) > 90 && budgetPct(c) <= 100,
                  'cb-over': budgetPct(c) > 100,
                }"
              ></div>
            </div>
          </div>

          <div class="cc-arrow">
            <ArrowUpRight :size="14" />
          </div>
        </article>

        <div v-if="!filteredCampaigns.length" class="empty-grid">
          <Frown :size="20" />
          <span>No hi ha campanyes amb aquests filtres.</span>
        </div>
      </div>
      </div>
    </section>

    <!-- ════════════════════════════════════════════════════════════
         TAB 2 · CALENDARIO (Gantt)
       ════════════════════════════════════════════════════════════ -->
    <section v-if="activeTab === 'timeline'" class="tab-section timeline-tab">
      <div class="timeline-card">
        <header class="tl-header">
          <div>
            <h3 class="tl-title">Cronograma de campanyes</h3>
            <p class="tl-sub">{{ timelineMonths.length }} mesos · {{ filteredCampaigns.length }} campanyes</p>
          </div>
          <div class="tl-legend">
            <span class="leg-item leg-active">
              <span class="leg-dot"></span> Activa
            </span>
            <span class="leg-item leg-completed">
              <span class="leg-dot"></span> Completada
            </span>
            <span class="leg-item leg-draft">
              <span class="leg-dot"></span> Esborrany
            </span>
          </div>
        </header>

        <!-- Month grid -->
        <div class="gantt">
          <!-- Month headers -->
          <div class="gantt-months">
            <div
              v-for="m in timelineMonths"
              :key="m.key"
              class="gantt-month"
              :class="{ 'gantt-month-current': m.isCurrent }"
            >
              <span class="gm-name">{{ m.label }}</span>
            </div>
            <div
              v-if="todayPos !== null"
              class="gantt-today"
              :style="{ left: todayPos + '%' }"
              title="Avui"
            >
              <span class="today-dot"></span>
              <span class="today-label">Avui</span>
            </div>
          </div>

          <!-- Campaign rows -->
          <div class="gantt-rows">
            <button
              v-for="c in timelineCampaigns"
              :key="c.id"
              class="gantt-row"
              @click="openCampaign(c.id)"
            >
              <div class="gr-name-col">
                <span class="gr-name">{{ c.name }}</span>
                <span class="gr-meta">{{ c.objective }}</span>
              </div>
              <div class="gr-track">
                <!-- Background grid -->
                <div
                  v-for="m in timelineMonths"
                  :key="m.key"
                  class="track-cell"
                  :class="{ 'track-cell-current': m.isCurrent }"
                ></div>
                <!-- Campaign bar -->
                <div
                  class="gr-bar"
                  :class="['st-' + c.status]"
                  :style="{
                    left: c._barLeft + '%',
                    width: c._barWidth + '%',
                  }"
                  :title="`${c.name} · ${formatDate(c.startDate)} → ${formatDate(c.endDate)}`"
                >
                  <span class="bar-label">
                    <span class="bar-status-dot"></span>
                    {{ c.name }}
                  </span>
                </div>
              </div>
            </button>

            <div v-if="!timelineCampaigns.length" class="empty-grid">
              <Frown :size="20" />
              <span>No hi ha campanyes en el rang visible.</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════════════════════════════════════════════════════
         CREATE MODAL — 2-step wizard
         Step 1: basic info   |   Step 2: methods config
       ═══════════════════════════════════════════════════════ -->
    <Teleport to="body">
      <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
        <div class="modal wizard-modal">

          <!-- ── Wizard header ── -->
          <header class="wizard-header">
            <div class="wizard-meta">
              <span class="wizard-eyebrow">Nova campanya</span>
              <h2 class="wizard-title">{{ wizardStep === 1 ? 'Informació general' : 'Mètodes i canals' }}</h2>
              <p class="wizard-sub">{{ wizardStep === 1 ? 'Defineix les dades bàsiques de la campanya.' : 'Tria com difondràs la campanya i afegeix-hi els elements.' }}</p>
            </div>
            <button class="modal-close" @click="showCreateModal = false"><X :size="18" /></button>
          </header>

          <!-- ── Step indicator ── -->
          <div class="wizard-steps">
            <div class="ws-step" :class="{ active: wizardStep === 1, done: wizardStep > 1 }">
              <div class="ws-dot">{{ wizardStep > 1 ? '✓' : '1' }}</div>
              <span>Informació</span>
            </div>
            <div class="ws-line" :class="{ done: wizardStep > 1 }"></div>
            <div class="ws-step" :class="{ active: wizardStep === 2 }">
              <div class="ws-dot">2</div>
              <span>Mètodes</span>
            </div>
          </div>

          <!-- ────────────────────────────────────────────────────
               STEP 1 · Basic info
             ──────────────────────────────────────────────────── -->
          <div v-if="wizardStep === 1" class="wizard-body">

            <!-- Name (prominent) -->
            <div class="wf-name-block">
              <label class="field-label">Nom de la campanya <span class="req">*</span></label>
              <input
                v-model="form.name"
                class="field-input name-input"
                placeholder="p. ex. Primavera 2026"
                autofocus
              />
            </div>

            <div class="field">
              <label class="field-label">Objectiu</label>
              <select v-model="form.objective" class="field-input">
                <option v-for="o in CAMPAIGN_OBJECTIVES" :key="o" :value="o">{{ o }}</option>
              </select>
            </div>

            <div class="wf-row wf-row-3">
              <div class="field">
                <label class="field-label">Inici</label>
                <input v-model="form.startDate" type="date" class="field-input" />
              </div>
              <div class="field">
                <label class="field-label">Fi</label>
                <input v-model="form.endDate" type="date" class="field-input" />
              </div>
              <div class="field">
                <label class="field-label">Pressupost (€)</label>
                <input v-model.number="form.budget" type="number" class="field-input" placeholder="0" min="0" />
              </div>
            </div>

            <div class="field">
              <label class="field-label">Descripció <span class="opt">(opcional)</span></label>
              <textarea v-model="form.description" class="field-input field-textarea" rows="3" placeholder="Objectiu i context de la campanya..."></textarea>
            </div>

            <!-- Targets -->
            <div class="targets-block">
              <div class="targets-title">
                <Target :size="13" />
                Objectius de rendiment <span class="opt">(opcional)</span>
              </div>
              <div class="targets-grid">
                <div class="tg-field">
                  <span class="tg-label">Abast</span>
                  <input v-model.number="form.targets.reach" type="number" class="field-input" placeholder="—" />
                </div>
                <div class="tg-field">
                  <span class="tg-label">Clics</span>
                  <input v-model.number="form.targets.clicks" type="number" class="field-input" placeholder="—" />
                </div>
                <div class="tg-field">
                  <span class="tg-label">Conversions</span>
                  <input v-model.number="form.targets.conversions" type="number" class="field-input" placeholder="—" />
                </div>
                <div class="tg-field">
                  <span class="tg-label">Vendes (€)</span>
                  <input v-model.number="form.targets.sales" type="number" class="field-input" placeholder="—" />
                </div>
              </div>
            </div>
          </div>

          <!-- ────────────────────────────────────────────────────
               STEP 2 · Methods
             ──────────────────────────────────────────────────── -->
          <div v-if="wizardStep === 2" class="wizard-body wizard-methods">

            <!-- ── Productes globals de la campanya ── -->
            <div class="camp-prods-block">
              <div class="cpb-header">
                <Package :size="14" class="cpb-icon" />
                <span class="cpb-title">Productes de la campanya</span>
                <span class="opt cpb-opt">opcional</span>
              </div>
              <p class="cpb-hint">Els productes afegits aquí s'assignaran automàticament a totes les publicacions, influencers i anuncis.</p>

              <div class="prod-picker-wrap">
                <div class="search-input-wrap">
                  <Search :size="14" class="search-icon" />
                  <input
                    v-model="pickerQ"
                    class="filter-input search-input"
                    placeholder="Cerca un producte per nom, SKU o categoria…"
                    @focus="openPicker('campaign')"
                    @input="openPicker('campaign')"
                  />
                  <button v-if="activePicker === 'campaign'" class="picker-close-btn" @click.stop="closePicker()">
                    <X :size="13" />
                  </button>
                </div>
                <div v-if="activePicker === 'campaign'" class="prod-dropdown">
                  <button
                    v-for="p in pickerResults"
                    :key="p.id"
                    class="prod-option"
                    :class="{ 'prod-option-added': isInKey(p.id, 'campaign') }"
                    @click.prevent="pickProduct(p)"
                  >
                    <span class="prod-opt-icon"><Package :size="13" /></span>
                    <span class="prod-opt-info">
                      <span class="prod-opt-name">{{ p.name }}</span>
                      <span class="prod-opt-meta">{{ p.sku }} · {{ p.category }}</span>
                    </span>
                    <span class="prod-opt-price">{{ formatCurrency(p.price) }}</span>
                    <Check v-if="isInKey(p.id, 'campaign')" :size="12" class="prod-opt-check" />
                  </button>
                  <div v-if="!pickerResults.length" class="prod-dropdown-empty">Sense resultats.</div>
                </div>
              </div>

              <div v-if="form.campaignProducts.length" class="prod-chips-list">
                <div v-for="p in form.campaignProducts" :key="p.id" class="prod-chip">
                  <Package :size="11" class="pchip-icon" />
                  <span class="pchip-name">{{ p.name }}</span>
                  <span class="pchip-sku">{{ p.sku }}</span>
                  <span class="pchip-price">{{ formatCurrency(p.price) }}</span>
                  <button class="pchip-remove" @click.stop="removeItemProduct('campaign', p.id)"><X :size="11" /></button>
                </div>
              </div>
            </div>

            <!-- Channel tabs -->
            <div class="ch-tabs">
              <button
                v-for="ch in CHANNELS_LIST"
                :key="ch.key"
                class="ch-tab"
                :class="{ active: methodTab === ch.key }"
                :style="methodTab === ch.key ? { color: ch.color, borderBottomColor: ch.color } : {}"
                @click="methodTab = ch.key"
              >
                <span class="ch-tab-icon" :style="{ color: methodTab === ch.key ? ch.color : 'inherit' }">
                  <component :is="channelIcon(ch.icon)" :size="15" />
                </span>
                {{ ch.key === 'owned' ? 'Contingut' : ch.label }}
                <span v-if="methodCounts[ch.key]" class="ch-tab-badge" :style="{ background: ch.color }">
                  {{ methodCounts[ch.key] }}
                </span>
                <span class="ch-tab-src" :class="ch.source === 'auto' ? 'src-auto' : 'src-manual'">
                  {{ ch.source === 'auto' ? 'auto' : 'manual' }}
                </span>
              </button>
            </div>

            <!-- ── TAB: Contenido (own posts) ── -->
            <div v-if="methodTab === 'owned'" class="method-pane">
              <div class="method-pane-head">
                <p class="method-pane-desc">Tria quines publicacions dels teus comptes s'inclouen en aquesta campanya.</p>
                <div class="mp-filters">
                  <div class="search-input-wrap">
                    <Search :size="14" class="search-icon" />
                    <input v-model="postSearch" class="filter-input search-input" placeholder="Cerca una publicació..." />
                  </div>
                  <div class="platform-filters">
                    <button
                      class="pf-btn"
                      :class="{ active: postPlatformFilter === 'all' }"
                      @click="postPlatformFilter = 'all'"
                    >Totes</button>
                    <button
                      v-for="plt in availablePlatforms"
                      :key="plt"
                      class="pf-btn"
                      :class="{ active: postPlatformFilter === plt }"
                      :style="postPlatformFilter === plt ? { background: getPlatform(plt).color, borderColor: getPlatform(plt).color, color: 'white' } : {}"
                      @click="postPlatformFilter = plt"
                    >{{ getPlatform(plt).label }}</button>
                  </div>
                </div>
              </div>

              <div class="posts-grid">
                <label
                  v-for="p in filteredPostsForPicker"
                  :key="p.id"
                  class="post-pick"
                  :class="{ selected: form.selectedPostIds.includes(p.id) }"
                >
                  <input
                    type="checkbox"
                    class="post-pick-check"
                    :checked="form.selectedPostIds.includes(p.id)"
                    @change="togglePost(p.id)"
                  />
                  <div class="post-pick-thumb" :style="postThumbStyle(p)">
                    <component :is="typeIcon(p.type)" :size="14" />
                  </div>
                  <div class="post-pick-info">
                    <div class="post-pick-title">{{ p.title }}</div>
                    <div class="post-pick-meta">
                      <span class="platform-pill" :style="platformStyle(p.platform)">{{ getPlatform(p.platform).label }}</span>
                      <span class="muted-sm">{{ formatDateShort(p.date) }}</span>
                      <span class="eng-badge">{{ p.engagement }}%</span>
                    </div>
                  </div>
                  <div v-if="form.selectedPostIds.includes(p.id)" class="post-pick-selected-mark">
                    <Check :size="13" />
                  </div>
                </label>
                <div v-if="!filteredPostsForPicker.length" class="pick-empty">
                  No hi ha publicacions que coincideixin.
                </div>
              </div>

              <div v-if="form.selectedPostIds.length" class="pick-summary">
                <Check :size="13" />
                {{ form.selectedPostIds.length }} publicaci{{ form.selectedPostIds.length !== 1 ? 'ons' : 'ó' }} seleccionad{{ form.selectedPostIds.length !== 1 ? 'es' : 'a' }}
              </div>

              <!-- Products per post -->
              <div v-if="form.selectedPostIds.length" class="per-item-prods">
                <div class="pip-section-title">
                  <Package :size="13" />
                  Productes per publicació
                </div>
                <div v-for="postId in form.selectedPostIds" :key="postId" class="pip-row">
                  <div class="pip-row-header">
                    <div class="pip-thumb" :style="postThumbStyle(getPostById(postId))">
                      <component :is="typeIcon(getPostById(postId)?.type)" :size="9" />
                    </div>
                    <span class="pip-post-title">{{ getPostById(postId)?.title }}</span>
                    <span class="platform-pill" :style="platformStyle(getPostById(postId)?.platform)">
                      {{ getPlatform(getPostById(postId)?.platform).label }}
                    </span>
                  </div>
                  <div class="pip-products-row">
                    <span
                      v-for="p in (form.postProducts[postId] || [])"
                      :key="p.id"
                      class="prod-chip-sm"
                    >
                      <span class="pcsm-name">{{ p.name }}</span>
                      <span class="pcsm-sku">{{ p.sku }}</span>
                      <button class="pcsm-rm" @click.stop="removeItemProduct(`post-${postId}`, p.id)"><X :size="9" /></button>
                    </span>
                    <div class="prod-picker-wrap pip-picker">
                      <button class="pip-add-btn" @click.stop="openPicker(`post-${postId}`)">
                        <Plus :size="11" /> Afegir
                      </button>
                      <div v-if="activePicker === `post-${postId}`" class="prod-dd-small">
                        <div class="pdd-search-row">
                          <Search :size="12" class="pdd-search-icon" />
                          <input v-model="pickerQ" class="pdd-input" placeholder="Cerca producte…" />
                          <button class="pdd-close" @click.stop="closePicker()"><X :size="12" /></button>
                        </div>
                        <div class="pdd-list">
                          <button
                            v-for="p in pickerResults"
                            :key="p.id"
                            class="pdd-item"
                            :class="{ 'pdd-added': isInKey(p.id, `post-${postId}`) }"
                            @click.stop="pickProduct(p)"
                          >
                            <span class="pdd-name">{{ p.name }}</span>
                            <span class="pdd-sku">{{ p.sku }}</span>
                            <Check v-if="isInKey(p.id, `post-${postId}`)" :size="10" class="pdd-check" />
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- ── TAB: Influencers ── -->
            <div v-if="methodTab === 'influencers'" class="method-pane">
              <p class="method-pane-desc">Afegeix els influencers que participaran en aquesta campanya. Els pots gestionar després des de la pestanya de Col·laboracions.</p>

              <!-- Combobox search -->
              <div class="inf-search-wrap" ref="infSearchRef">
                <div class="search-input-wrap">
                  <Search :size="14" class="search-icon" />
                  <input
                    v-model="infSearch"
                    class="filter-input search-input"
                    placeholder="Cerca un influencer per nom o àlies..."
                    @focus="infDropdownOpen = true"
                    @input="infDropdownOpen = true"
                  />
                </div>
                <!-- Dropdown -->
                <div v-if="infDropdownOpen && (infSearchResults.length || infSearch)" class="inf-dropdown">
                  <button
                    v-for="inf in infSearchResults"
                    :key="inf.id"
                    class="inf-option"
                    :disabled="form.selectedInfluencerIds.includes(inf.id)"
                    @click.prevent="addInfluencer(inf)"
                  >
                    <div class="inf-opt-avatar" :style="infAvatarStyle(inf)">{{ inf.name[0] }}</div>
                    <div class="inf-opt-info">
                      <span class="inf-opt-name">{{ inf.name }}</span>
                      <span class="inf-opt-alias">{{ inf.alias }}</span>
                    </div>
                    <span v-if="form.selectedInfluencerIds.includes(inf.id)" class="inf-opt-added">Afegit</span>
                    <div v-else class="inf-opt-stats">
                      <span>{{ formatNumber(inf.followers) }} seg.</span>
                    </div>
                  </button>
                  <button
                    v-if="infSearch && !infSearchResults.length"
                    class="inf-option inf-option-empty"
                    disabled
                  >Sense resultats per a "{{ infSearch }}"</button>
                  <!-- Inline "add new influencer" -->
                  <button class="inf-option inf-option-new" @click.prevent="openNewInfluencerForm">
                    <Plus :size="14" />
                    Afegir un influencer nou…
                  </button>
                </div>
              </div>

              <!-- Selected influencers chips -->
              <div v-if="form.selectedInfluencerIds.length" class="inf-selected-list">
                <div
                  v-for="infId in form.selectedInfluencerIds"
                  :key="infId"
                  class="inf-chip inf-chip-expanded"
                >
                  <div class="inf-chip-top">
                    <div class="inf-chip-avatar" :style="infAvatarStyleById(infId)">
                      {{ getInfluencerById(infId)?.name[0] }}
                    </div>
                    <span class="inf-chip-name">{{ getInfluencerById(infId)?.name }}</span>
                    <span class="inf-chip-alias">{{ getInfluencerById(infId)?.alias }}</span>
                    <button class="inf-chip-remove" @click="removeInfluencer(infId)">
                      <X :size="12" />
                    </button>
                  </div>
                  <!-- Products for this influencer -->
                  <div class="pip-products-row pip-products-inf">
                    <span
                      v-for="p in (form.influencerProducts[infId] || [])"
                      :key="p.id"
                      class="prod-chip-sm"
                    >
                      <span class="pcsm-name">{{ p.name }}</span>
                      <span class="pcsm-sku">{{ p.sku }}</span>
                      <button class="pcsm-rm" @click.stop="removeItemProduct(`inf-${infId}`, p.id)"><X :size="9" /></button>
                    </span>
                    <div class="prod-picker-wrap pip-picker">
                      <button class="pip-add-btn" @click.stop="openPicker(`inf-${infId}`)">
                        <Plus :size="11" /> Producte
                      </button>
                      <div v-if="activePicker === `inf-${infId}`" class="prod-dd-small">
                        <div class="pdd-search-row">
                          <Search :size="12" class="pdd-search-icon" />
                          <input v-model="pickerQ" class="pdd-input" placeholder="Cerca producte…" />
                          <button class="pdd-close" @click.stop="closePicker()"><X :size="12" /></button>
                        </div>
                        <div class="pdd-list">
                          <button
                            v-for="p in pickerResults"
                            :key="p.id"
                            class="pdd-item"
                            :class="{ 'pdd-added': isInKey(p.id, `inf-${infId}`) }"
                            @click.stop="pickProduct(p)"
                          >
                            <span class="pdd-name">{{ p.name }}</span>
                            <span class="pdd-sku">{{ p.sku }}</span>
                            <Check v-if="isInKey(p.id, `inf-${infId}`)" :size="10" class="pdd-check" />
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="pick-empty">Encara no s'ha afegit cap influencer.</div>
            </div>

            <!-- ── TAB: Anuncios de pago ── -->
            <div v-if="methodTab === 'paid'" class="method-pane">
              <p class="method-pane-desc">Defineix els conjunts d'anuncis per plataforma. Les mètriques se sincronitzen automàticament.</p>

              <div class="ads-list">
                <div v-for="(ad, i) in form.adSets" :key="ad.id || i" class="ad-set-group">
                  <div class="ad-set-row">
                    <div class="ad-set-platform">
                      <select v-model="ad.platform" class="field-input">
                        <option v-for="(p, k) in AD_PLATFORMS" :key="k" :value="k">{{ p.label }}</option>
                      </select>
                    </div>
                    <button class="ad-set-remove" @click="removeAdSet(i)"><X :size="14" /></button>
                  </div>
                  <!-- Products for this ad set -->
                  <div class="pip-products-row pip-products-ad">
                    <span
                      v-for="p in (form.adProducts[ad.id] || [])"
                      :key="p.id"
                      class="prod-chip-sm"
                    >
                      <span class="pcsm-name">{{ p.name }}</span>
                      <span class="pcsm-sku">{{ p.sku }}</span>
                      <button class="pcsm-rm" @click.stop="removeItemProduct(`ad-${ad.id}`, p.id)"><X :size="9" /></button>
                    </span>
                    <div class="prod-picker-wrap pip-picker">
                      <button class="pip-add-btn" @click.stop="openPicker(`ad-${ad.id}`)">
                        <Plus :size="11" /> Producte
                      </button>
                      <div v-if="activePicker === `ad-${ad.id}`" class="prod-dd-small">
                        <div class="pdd-search-row">
                          <Search :size="12" class="pdd-search-icon" />
                          <input v-model="pickerQ" class="pdd-input" placeholder="Cerca producte…" />
                          <button class="pdd-close" @click.stop="closePicker()"><X :size="12" /></button>
                        </div>
                        <div class="pdd-list">
                          <button
                            v-for="p in pickerResults"
                            :key="p.id"
                            class="pdd-item"
                            :class="{ 'pdd-added': isInKey(p.id, `ad-${ad.id}`) }"
                            @click.stop="pickProduct(p)"
                          >
                            <span class="pdd-name">{{ p.name }}</span>
                            <span class="pdd-sku">{{ p.sku }}</span>
                            <Check v-if="isInKey(p.id, `ad-${ad.id}`)" :size="10" class="pdd-check" />
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <button class="add-adset-btn" @click="addAdSet">
                  <Plus :size="14" />
                  Afegir un conjunt d'anuncis
                </button>
              </div>
            </div>

          </div>

          <!-- ── Wizard footer ── -->
          <footer class="wizard-footer">
            <div class="wf-left">
              <button v-if="wizardStep > 1" class="hub-btn hub-btn-ghost" @click="wizardStep--">
                <ChevronLeft :size="15" /> Anterior
              </button>
              <button v-else class="hub-btn hub-btn-ghost" @click="showCreateModal = false">Cancel·lar</button>
            </div>
            <div class="wf-right">
              <button v-if="wizardStep === 1" class="hub-btn hub-btn-primary" :disabled="!form.name" @click="wizardStep = 2">
                Següent <ChevronRight :size="15" />
              </button>
              <button v-else class="hub-btn hub-btn-primary" :disabled="saving" @click="saveCampaign">
                <Check :size="15" /> {{ saving ? 'Creant…' : 'Crear campanya' }}
              </button>
            </div>
          </footer>

        </div>
      </div>
    </Teleport>

    <!-- Inline new influencer mini-modal -->
    <Teleport to="body">
      <div v-if="showNewInfluencerModal" class="modal-overlay" @click.self="showNewInfluencerModal = false">
        <div class="modal" style="max-width: 440px">
          <header class="modal-header">
            <h2 class="modal-title">Influencer nou</h2>
            <button class="modal-close" @click="showNewInfluencerModal = false"><X :size="18" /></button>
          </header>
          <div class="modal-body">
            <div class="form-grid">
              <div class="field field-full">
                <label class="field-label">Nom complet <span class="req">*</span></label>
                <input v-model="newInfForm.name" class="field-input" placeholder="p. ex. Maria López" />
              </div>
              <div class="field">
                <label class="field-label">Àlies / usuari</label>
                <input v-model="newInfForm.alias" class="field-input" placeholder="@usuari" />
              </div>
              <div class="field">
                <label class="field-label">Plataforma principal</label>
                <select v-model="newInfForm.platform" class="field-input">
                  <option v-for="(p, k) in PLATFORMS" :key="k" :value="k">{{ p.label }}</option>
                </select>
              </div>
              <div class="field">
                <label class="field-label">Seguidors</label>
                <input v-model.number="newInfForm.followers" type="number" class="field-input" placeholder="0" />
              </div>
              <div class="field">
                <label class="field-label">Nínxol</label>
                <input v-model="newInfForm.niche" class="field-input" placeholder="Moda, fitness, lifestyle…" />
              </div>
              <div class="field">
                <label class="field-label">Contacte</label>
                <input v-model="newInfForm.contact" class="field-input" placeholder="correu o enllaç" />
              </div>
            </div>
          </div>
          <footer class="modal-footer">
            <button class="hub-btn hub-btn-ghost" @click="showNewInfluencerModal = false">Cancel·lar</button>
            <button class="hub-btn hub-btn-primary" :disabled="!newInfForm.name" @click="saveNewInfluencer">Desar l'influencer</button>
          </footer>
        </div>
      </div>
    </Teleport>

  </SocialHubLayout>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Search, Plus, Frown, ArrowUpRight, Calendar, X, Check,
  ChevronLeft, ChevronRight, Target,
  Megaphone, Users, List, LayoutGrid,
  Image as ImageIcon, Film, Layers, MessageSquare, FileText,
  Package, Trash2,
} from 'lucide-vue-next'
import SocialHubLayout from './SocialHubLayout.vue'
import {
  erpProducts,
  CAMPAIGN_STATUSES, CAMPAIGN_OBJECTIVES, CAMPAIGN_CHANNELS,
  AD_PLATFORMS, PLATFORMS,
  formatNumber, formatCurrency, formatDate, getPlatform,
} from '@/services/socialCrmData'
import socialCrmApi, {
  OBJECTIVE_LABEL_TO_KEY, targetsToArray, enrichWithBreakdown,
} from '@/services/socialCrm'
import { useToast } from '@/composables/useToast'

const route  = useRoute()
const router = useRouter()
const toast  = useToast()

// ── Dades carregades del backend (social_crm) ─────────────────
const campaigns      = ref([])
const allPosts       = ref([])
const allInfluencers = ref([])
const loading        = ref(false)
const saving         = ref(false)

async function loadCampaigns() {
  loading.value = true
  try {
    const list = await socialCrmApi.listCampaigns()
    // Enriquim cada campanya amb els totals derivats (cost/vendes/ROAS/posts…),
    // que el backend calcula a /channel-breakdown/ i mai no emmagatzema.
    await Promise.all(list.map(async (c) => {
      try { enrichWithBreakdown(c, await socialCrmApi.channelBreakdown(c.id)) }
      catch { /* mantenim els zeros per defecte si falla el breakdown */ }
    }))
    campaigns.value = list
  } catch (e) {
    toast.error(e.message || 'No s\'han pogut carregar les campanyes.')
  } finally {
    loading.value = false
  }
}

async function loadPickerData() {
  try {
    const [posts, infs] = await Promise.all([
      socialCrmApi.listPosts(),
      socialCrmApi.listInfluencers(),
    ])
    allPosts.value       = posts
    allInfluencers.value = infs
  } catch (e) {
    toast.error(e.message || 'No s\'han pogut carregar les dades del formulari.')
  }
}

onMounted(() => { loadCampaigns(); loadPickerData() })

// ── Tabs ──────────────────────────────────────────────────────
const activeTab = ref('list')

const tabs = computed(() => [
  { key: 'list',     label: 'Llista',     count: campaigns.value.length },
  { key: 'timeline', label: 'Cronograma' },
])

// ── Filters ───────────────────────────────────────────────────
const searchQ          = ref('')
const statusFilter     = ref('all')
const objectiveFilter  = ref('all')
const sortKey          = ref('recent')
const viewMode         = ref('table')

const filteredCampaigns = computed(() => {
  let list = [...campaigns.value]
  if (statusFilter.value !== 'all')    list = list.filter(c => c.status === statusFilter.value)
  if (objectiveFilter.value !== 'all') list = list.filter(c => c.objective === objectiveFilter.value)
  if (searchQ.value) {
    const q = searchQ.value.toLowerCase()
    list = list.filter(c => c.name.toLowerCase().includes(q))
  }
  return list.sort((a, b) => {
    if (sortKey.value === 'sales')  return b.sales - a.sales
    if (sortKey.value === 'roas')   return b.roas - a.roas
    if (sortKey.value === 'budget') return b.budget - a.budget
    return new Date(b.startDate) - new Date(a.startDate)
  })
})

// ── KPIs ──────────────────────────────────────────────────────
const kpis = computed(() => {
  const total = campaigns.value.length
  const active = campaigns.value.filter(c => c.status === 'active').length
  const draft = campaigns.value.filter(c => c.status === 'draft').length
  const completed = campaigns.value.filter(c => c.status === 'completed').length
  const activeCampaigns = campaigns.value.filter(c => c.status === 'active')
  const activeBudget = activeCampaigns.reduce((s, c) => s + c.budget, 0)
  const activeSpent  = activeCampaigns.reduce((s, c) => s + c.cost, 0)
  const totalSales = campaigns.value.reduce((s, c) => s + c.sales, 0)
  const totalConversions = campaigns.value.reduce((s, c) => s + c.conversions, 0)
  const totalCost = campaigns.value.reduce((s, c) => s + c.cost, 0)
  const avgRoas = totalCost ? totalSales / totalCost : 0
  const bestCampaign = [...campaigns.value]
    .filter(c => c.cost > 0)
    .sort((a, b) => b.roas - a.roas)[0]
  return { total, active, draft, completed, activeBudget, activeSpent, totalSales, totalConversions, avgRoas, bestCampaign }
})

// ── Timeline (gantt) calculations ─────────────────────────────
const today = new Date()
today.setHours(0, 0, 0, 0)

const timelineMonths = computed(() => {
  // Span the union of all campaign date ranges, padded by 1 month
  if (!filteredCampaigns.value.length) return []
  const allStarts = filteredCampaigns.value.map(c => new Date(c.startDate).getTime())
  const allEnds = filteredCampaigns.value.map(c => new Date(c.endDate).getTime())
  const min = new Date(Math.min(...allStarts))
  const max = new Date(Math.max(...allEnds))
  min.setDate(1); min.setHours(0, 0, 0, 0)
  max.setMonth(max.getMonth() + 1, 1)

  const months = []
  const cur = new Date(min)
  while (cur < max) {
    const monthKey = `${cur.getFullYear()}-${cur.getMonth()}`
    const isCurrent = cur.getFullYear() === today.getFullYear() && cur.getMonth() === today.getMonth()
    months.push({
      key: monthKey,
      label: cur.toLocaleDateString('ca-ES', { month: 'short', year: '2-digit' }),
      start: new Date(cur),
      end: new Date(cur.getFullYear(), cur.getMonth() + 1, 1),
      isCurrent,
    })
    cur.setMonth(cur.getMonth() + 1)
  }
  return months
})

const totalSpanMs = computed(() => {
  if (!timelineMonths.value.length) return 1
  const first = timelineMonths.value[0].start
  const last = timelineMonths.value[timelineMonths.value.length - 1].end
  return last.getTime() - first.getTime()
})

const todayPos = computed(() => {
  if (!timelineMonths.value.length) return null
  const first = timelineMonths.value[0].start.getTime()
  const last = timelineMonths.value[timelineMonths.value.length - 1].end.getTime()
  if (today.getTime() < first || today.getTime() > last) return null
  return ((today.getTime() - first) / (last - first)) * 100
})

const timelineCampaigns = computed(() => {
  if (!timelineMonths.value.length) return []
  const firstMs = timelineMonths.value[0].start.getTime()
  return filteredCampaigns.value
    .map(c => {
      const start = new Date(c.startDate).getTime()
      const end = new Date(c.endDate).getTime()
      const left = ((start - firstMs) / totalSpanMs.value) * 100
      const width = ((end - start) / totalSpanMs.value) * 100
      return {
        ...c,
        _barLeft: Math.max(0, left),
        _barWidth: Math.max(width, 2),
      }
    })
    .sort((a, b) => new Date(a.startDate) - new Date(b.startDate))
})

// ── Navegación al detalle ─────────────────────────────────────
function openCampaign(id) {
  router.push(`/social-crm/campaigns/${id}`)
}

// ── Esborrar campanya ─────────────────────────────────────────
async function confirmDelete(c) {
  if (!confirm(`Segur que vols esborrar la campanya "${c.name}"? S'eliminaran les seves col·laboracions, anuncis i enllaços. Les publicacions es conservaran com a contingut orgànic. Aquesta acció no es pot desfer.`)) return
  try {
    await socialCrmApi.deleteCampaign(c.id)
    campaigns.value = campaigns.value.filter(x => x.id !== c.id)
    toast.success('Campanya esborrada.')
  } catch (e) {
    toast.error(e.message || 'No s\'ha pogut esborrar la campanya.')
  }
}

// ── Create wizard ─────────────────────────────────────────────
const CHANNELS_LIST = Object.values(CAMPAIGN_CHANNELS)
const showCreateModal = ref(false)
const wizardStep      = ref(1)
const methodTab       = ref('owned')

function blankForm() {
  return {
    name: '', objective: 'Awareness', budget: 0, startDate: '', endDate: '',
    description: '',
    targets: { reach: 0, clicks: 0, conversions: 0, sales: 0 },
    selectedPostIds:       [],
    selectedInfluencerIds: [],
    adSets:                [],
    campaignProducts:      [],
    postProducts:          {},
    influencerProducts:    {},
    adProducts:            {},
  }
}
const form = reactive(blankForm())

function openCreateModal() {
  Object.assign(form, blankForm())
  form.targets = { reach: 0, clicks: 0, conversions: 0, sales: 0 }
  form.selectedPostIds       = []
  form.selectedInfluencerIds = []
  form.adSets                = []
  form.campaignProducts      = []
  form.postProducts          = {}
  form.influencerProducts    = {}
  form.adProducts            = {}
  wizardStep.value = 1
  methodTab.value  = 'owned'
  infSearch.value  = ''
  infDropdownOpen.value = false
  activePicker.value = null
  pickerQ.value = ''
  showCreateModal.value = true
}

// Derived channels: only include those with items (or always show all 3)
const methodCounts = computed(() => ({
  owned:       form.selectedPostIds.length,
  influencers: form.selectedInfluencerIds.length,
  paid:        form.adSets.length,
}))

async function saveCampaign() {
  if (!form.name || saving.value) return
  saving.value = true
  try {
    // Pressupost del canal de pagament (suma dels conjunts d'anuncis).
    const paidBudget = form.adSets.reduce((s, ad) => s + (Number(ad.budget) || 0), 0)
    const channelBudgets = paidBudget > 0
      ? [{ channel: 'paid', budget_amount: paidBudget }]
      : []

    // 1. Crea la campanya (els objectius es desen com a registres CampaignTarget).
    const created = await socialCrmApi.createCampaign({
      name:         form.name,
      objective:    OBJECTIVE_LABEL_TO_KEY[form.objective] || 'awareness',
      status:       'draft',
      start_date:   form.startDate || null,
      end_date:     form.endDate || null,
      total_budget: Number(form.budget) || 0,
      description:  form.description || '',
      targets:         targetsToArray(form.targets),
      channel_budgets: channelBudgets,
    })
    const id = created.id

    // 2. Canal "propi": vincula les publicacions seleccionades a la campanya.
    // 3. Canal "influencers": crea una col·laboració per cada influencer.
    // 4. Canal "pagament": crea un conjunt d'anuncis per cada ad set.
    await Promise.all([
      ...form.selectedPostIds.map(pid =>
        socialCrmApi.linkPostToCampaign(pid, id)),
      ...form.selectedInfluencerIds.map(infId =>
        socialCrmApi.createCollaboration({
          campaign: id,
          influencer: infId,
          content_format: 'Per definir',
          publish_date: form.startDate || null,
          status: 'draft',
        })),
      ...form.adSets.map(ad =>
        socialCrmApi.createAdSet({
          campaign: id,
          ad_platform: ad.platform,
          name: ad.name || `${AD_PLATFORMS[ad.platform]?.label || ad.platform} · Conjunt d'anuncis`,
          status: 'active',
          start_date: form.startDate || null,
          end_date: form.endDate || null,
          budget_amount: Number(ad.budget) || 0,
        })),
    ])

    showCreateModal.value = false
    toast.success('Campanya creada correctament.')
    router.push(`/social-crm/campaigns/${id}`)
  } catch (e) {
    toast.error(e.message || 'No s\'ha pogut crear la campanya.')
  } finally {
    saving.value = false
  }
}

// ── Posts picker (owned tab) ──────────────────────────────────
const postSearch          = ref('')
const postPlatformFilter  = ref('all')

const availablePlatforms = computed(() =>
  [...new Set(allPosts.value.map(p => p.platform))]
)

const filteredPostsForPicker = computed(() => {
  let list = allPosts.value.filter(p => !p.campaignId)  // unlinked posts first
    .concat(allPosts.value.filter(p => p.campaignId))   // then linked ones
  if (postPlatformFilter.value !== 'all')
    list = list.filter(p => p.platform === postPlatformFilter.value)
  if (postSearch.value) {
    const q = postSearch.value.toLowerCase()
    list = list.filter(p => p.title.toLowerCase().includes(q))
  }
  return list
})

function togglePost(id) {
  const i = form.selectedPostIds.indexOf(id)
  if (i === -1) {
    form.selectedPostIds.push(id)
    if (!form.postProducts[id]) form.postProducts[id] = []
    for (const cp of form.campaignProducts) {
      if (!form.postProducts[id].find(p => p.id === cp.id))
        form.postProducts[id].push({ ...cp })
    }
  } else {
    form.selectedPostIds.splice(i, 1)
  }
}

function getPostById(id) {
  return allPosts.value.find(p => p.id === id)
}

function postThumbStyle(p) {
  const pl = getPlatform(p.platform)
  return { background: `linear-gradient(135deg, ${pl.color}cc, ${pl.color}55)` }
}
function platformStyle(key) { const p = getPlatform(key); return { background: p.bg, color: p.color } }
function typeIcon(type) {
  const map = { 'Imatge': ImageIcon, 'Vídeo': Film, 'Reel': Film, 'Story': Layers, 'Carrusel': Layers, 'Tweet': MessageSquare, 'Fil': MessageSquare, 'Short': Film }
  return map[type] || FileText
}

// ── Influencer picker ─────────────────────────────────────────
const infSearch        = ref('')
const infDropdownOpen  = ref(false)
const infSearchRef     = ref(null)

const infSearchResults = computed(() => {
  if (!infSearch.value) return allInfluencers.value.slice(0, 8)
  const q = infSearch.value.toLowerCase()
  return allInfluencers.value.filter(i =>
    i.name.toLowerCase().includes(q) || i.alias.toLowerCase().includes(q)
  ).slice(0, 8)
})

function addInfluencer(inf) {
  if (!form.selectedInfluencerIds.includes(inf.id)) {
    form.selectedInfluencerIds.push(inf.id)
    if (!form.influencerProducts[inf.id]) form.influencerProducts[inf.id] = []
    for (const cp of form.campaignProducts) {
      if (!form.influencerProducts[inf.id].find(p => p.id === cp.id))
        form.influencerProducts[inf.id].push({ ...cp })
    }
  }
  infSearch.value = ''
  infDropdownOpen.value = false
}
function removeInfluencer(id) {
  const i = form.selectedInfluencerIds.indexOf(id)
  if (i !== -1) form.selectedInfluencerIds.splice(i, 1)
}
function getInfluencerById(id) { return allInfluencers.value.find(i => i.id === id) }

const AVATAR_PALETTE = [
  'linear-gradient(135deg,#667eea,#764ba2)',
  'linear-gradient(135deg,#f093fb,#f5576c)',
  'linear-gradient(135deg,#4facfe,#00f2fe)',
  'linear-gradient(135deg,#43e97b,#38f9d7)',
  'linear-gradient(135deg,#fa709a,#fee140)',
  'linear-gradient(135deg,#30cfd0,#330867)',
]
function infAvatarStyle(inf) {
  const seed = (inf.name.charCodeAt(0) + inf.id) % 6
  return { background: AVATAR_PALETTE[seed] }
}
function infAvatarStyleById(id) {
  const inf = getInfluencerById(id)
  return inf ? infAvatarStyle(inf) : {}
}

// Close dropdown on outside click
function handleOutsideClick(e) {
  if (infSearchRef.value && !infSearchRef.value.contains(e.target)) {
    infDropdownOpen.value = false
  }
  if (activePicker.value && !e.target.closest('.prod-picker-wrap')) {
    closePicker()
  }
}
onMounted(() => document.addEventListener('mousedown', handleOutsideClick))
onBeforeUnmount(() => document.removeEventListener('mousedown', handleOutsideClick))

// ── Inline new-influencer mini-modal ──────────────────────────
const showNewInfluencerModal = ref(false)
const newInfForm = reactive({ name: '', alias: '', platform: 'instagram', followers: 0, niche: '', contact: '' })

function openNewInfluencerForm() {
  infDropdownOpen.value = false
  Object.assign(newInfForm, { name: '', alias: '', platform: 'instagram', followers: 0, niche: '', contact: '' })
  showNewInfluencerModal.value = true
}
async function saveNewInfluencer() {
  if (!newInfForm.name) return
  const alias = newInfForm.alias || '@' + newInfForm.name.split(' ')[0].toLowerCase()
  try {
    const created = await socialCrmApi.createInfluencer({
      name: newInfForm.name,
      alias,
      primary_platform: newInfForm.platform,
      niche: newInfForm.niche || '',
      contact_email: newInfForm.contact || '',
      status: 'prospect',
      platform_presences: [{
        platform: newInfForm.platform,
        username: alias,
        followers: Number(newInfForm.followers) || 0,
      }],
    })
    // Afegeix-lo a la llista local i selecciona'l a la campanya.
    allInfluencers.value.push({
      id: created.id, name: created.name, alias: created.alias,
      platform: created.primary_platform, followers: Number(newInfForm.followers) || 0,
      niche: created.niche || '', status: created.status,
    })
    form.selectedInfluencerIds.push(created.id)
    showNewInfluencerModal.value = false
  } catch (e) {
    toast.error(e.message || 'No s\'ha pogut crear l\'influencer.')
  }
}

// ── Ad sets (paid tab) ────────────────────────────────────────
function addAdSet() {
  const id = `as${Date.now()}`
  form.adSets.push({ id, platform: 'facebook', name: '', budget: 0 })
  if (!form.adProducts[id]) form.adProducts[id] = []
  for (const cp of form.campaignProducts) {
    form.adProducts[id].push({ ...cp })
  }
}
function removeAdSet(i) {
  const id = form.adSets[i]?.id
  if (id) delete form.adProducts[id]
  form.adSets.splice(i, 1)
}

// ── Product picker ────────────────────────────────────────────
// activePicker: null | 'campaign' | 'post-{id}' | 'inf-{id}' | 'ad-{adSetId}'
const activePicker = ref(null)
const pickerQ      = ref('')

const pickerResults = computed(() => {
  const q = pickerQ.value.toLowerCase().trim()
  if (!q) return erpProducts.slice(0, 10)
  return erpProducts.filter(p =>
    p.name.toLowerCase().includes(q) || p.sku.toLowerCase().includes(q) || p.category.toLowerCase().includes(q)
  ).slice(0, 10)
})

function openPicker(key) {
  if (activePicker.value !== key) pickerQ.value = ''
  activePicker.value = key
}
function closePicker() {
  activePicker.value = null
  pickerQ.value = ''
}

function getItemProds(key) {
  if (key === 'campaign') return form.campaignProducts
  if (key?.startsWith('post-'))  { const id = parseInt(key.slice(5)); return form.postProducts[id] || [] }
  if (key?.startsWith('inf-'))   { const id = parseInt(key.slice(4)); return form.influencerProducts[id] || [] }
  if (key?.startsWith('ad-'))    { const id = key.slice(3); return form.adProducts[id] || [] }
  return []
}

function isInKey(productId, key) {
  return getItemProds(key).some(p => p.id === productId)
}

function pickProduct(product) {
  const key = activePicker.value
  if (!key) return
  const list = getItemProds(key)
  if (list.find(p => p.id === product.id)) return
  list.push({ ...product })
  if (key === 'campaign') propagateCampaignProduct(product)
}

function removeItemProduct(key, productId) {
  const list = getItemProds(key)
  const i = list.findIndex(p => p.id === productId)
  if (i !== -1) list.splice(i, 1)
}

function propagateCampaignProduct(product) {
  for (const postId of form.selectedPostIds) {
    if (!form.postProducts[postId]) form.postProducts[postId] = []
    if (!form.postProducts[postId].find(p => p.id === product.id))
      form.postProducts[postId].push({ ...product })
  }
  for (const infId of form.selectedInfluencerIds) {
    if (!form.influencerProducts[infId]) form.influencerProducts[infId] = []
    if (!form.influencerProducts[infId].find(p => p.id === product.id))
      form.influencerProducts[infId].push({ ...product })
  }
  for (const ad of form.adSets) {
    if (!form.adProducts[ad.id]) form.adProducts[ad.id] = []
    if (!form.adProducts[ad.id].find(p => p.id === product.id))
      form.adProducts[ad.id].push({ ...product })
  }
}

// ── Channel icon helper ───────────────────────────────────────
const CHANNEL_ICONS = { Megaphone, Users, Target }
function channelIcon(name) { return CHANNEL_ICONS[name] || Megaphone }

// ── Helpers ───────────────────────────────────────────────────
function formatDateShort(iso) {
  if (!iso) return '—'
  const d = new Date(iso)
  return d.toLocaleDateString('ca-ES', { day: '2-digit', month: 'short' })
}
function budgetPct(c) {
  if (!c.budget) return 0
  return (c.cost / c.budget) * 100
}
function roasClass(v) {
  if (v >= 3) return 'roas-good'
  if (v >= 1) return 'roas-ok'
  return 'roas-bad'
}
</script>

<style scoped>
/* ── View toggle ────────────────────────────────────── */
.view-toggle {
  display: flex;
  border: 1px solid var(--border-color);
  border-radius: 7px;
  overflow: hidden;
  margin-left: 0.25rem;
}
.vt-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: var(--bg-primary);
  border: none;
  cursor: pointer;
  color: var(--text-secondary);
  transition: background 0.15s, color 0.15s;
  font-family: inherit;
}
.vt-btn:first-child { border-right: 1px solid var(--border-color); }
.vt-btn:hover { background: var(--bg-secondary); color: var(--text-primary); }
.vt-btn.active { background: var(--bg-secondary); color: var(--primary-color); }

/* ── Campaigns table ─────────────────────────────────── */
.data-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
}
.data-head {
  display: grid;
  padding: 0.625rem 1.25rem;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-secondary);
}
.head-campaigns { grid-template-columns: 2.5fr 0.9fr 1.1fr 1.4fr 1.4fr 1fr 0.8fr; }
.th-num { text-align: right; }

.data-rows { display: flex; flex-direction: column; }
.data-row {
  position: relative;
  display: grid;
  padding: 0.75rem 1.25rem;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-primary);
  border-left: none; border-right: none; border-top: none;
  cursor: pointer;
  text-align: left;
  font-family: inherit;
  font-size: 0.85rem;
  transition: background 0.12s ease;
  align-items: center;
}
.row-campaign { grid-template-columns: 2.5fr 0.9fr 1.1fr 1.4fr 1.4fr 1fr 0.8fr; }
.data-row:last-child { border-bottom: none; }
.data-row:hover { background: var(--bg-secondary); }
.data-row.active { background: rgba(102,126,234,0.06); position: relative; }
.data-row.active::before {
  content: '';
  position: absolute;
  left: 0; top: 0; bottom: 0; width: 3px;
  background: linear-gradient(180deg, #667eea, #764ba2);
}
.cell { display: flex; align-items: center; min-width: 0; }
.cell-campaign { gap: 0.625rem; }
.cell-num { justify-content: flex-end; text-align: right; }
.camp-name-block { min-width: 0; flex: 1; }
.row-name {
  font-weight: 600; color: var(--text-primary); font-size: 0.875rem;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.row-alias {
  font-size: 0.72rem; color: var(--text-secondary);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.budget-cell { display: flex; flex-direction: column; align-items: flex-end; gap: 3px; width: 100%; }
.budget-of { color: var(--text-secondary); font-weight: 400; }
.budget-bar-wrap { width: 100%; height: 4px; background: var(--bg-secondary); border-radius: 2px; overflow: hidden; }
.budget-bar {
  height: 100%; background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 2px; transition: width 0.4s ease;
}
.budget-bar.cb-warn { background: linear-gradient(90deg, #F59E0B, #D97706); }
.budget-bar.cb-over { background: linear-gradient(90deg, #EF4444, #B91C1C); }
.muted { color: var(--text-secondary); }
.font-mono { font-feature-settings: "tnum"; font-variant-numeric: tabular-nums; }

.hub-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 0.875rem;
  border: 1px solid var(--border-color);
  border-radius: 7px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-family: inherit;
}
.hub-btn-primary {
  border: none;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 2px 6px rgba(102,126,234,0.30);
}
.hub-btn-primary:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(102,126,234,0.4); }
.hub-btn-ghost:hover { background: var(--bg-secondary); }

/* ── KPI strip ──────────────────────────────────────── */
.kpi-strip {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.875rem;
  margin-bottom: 1.5rem;
}
.kpi-tile {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 0.875rem 1rem;
  position: relative;
  overflow: hidden;
}
.kpi-tile::before {
  content: '';
  position: absolute;
  top: 0; left: 0;
  width: 3px; height: 100%;
  background: linear-gradient(180deg, #667eea, #764ba2);
  opacity: 0.55;
}
.kpi-key {
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-secondary);
  margin-bottom: 0.375rem;
}
.kpi-val {
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text-primary);
  line-height: 1.05;
  font-feature-settings: "tnum";
}
.kpi-suffix { font-size: 0.85rem; color: var(--text-secondary); font-weight: 500; margin-left: 2px; }
.kpi-sub { font-size: 0.72rem; color: var(--text-secondary); margin-top: 0.25rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* ── Filters row ────────────────────────────────────── */
.tab-section { display: flex; flex-direction: column; gap: 1rem; }
.filters-row { display: flex; flex-wrap: wrap; align-items: center; gap: 0.5rem; }

.filter-input {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 7px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.85rem;
  cursor: pointer;
}
.filter-input:hover { border-color: var(--primary-color); }
.filter-input:focus { outline: none; border-color: var(--primary-color); box-shadow: 0 0 0 3px rgba(102,126,234,0.15); }

.search-input-wrap { position: relative; flex: 1 1 240px; max-width: 320px; }
.search-icon { position: absolute; left: 0.625rem; top: 50%; transform: translateY(-50%); color: var(--text-secondary); pointer-events: none; }
.search-input { width: 100%; padding-left: 2rem; cursor: text; }
.result-count { margin-left: auto; font-size: 0.78rem; color: var(--text-secondary); font-weight: 500; }

/* ── Campaign cards (list tab) ──────────────────────── */
.campaigns-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 0.875rem;
}

.campaign-card {
  position: relative;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  padding: 1.125rem 1.25rem 1rem;
  cursor: pointer;
  transition: all 0.18s ease;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
}
.campaign-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg, #667eea, #764ba2);
  opacity: 0;
  transition: opacity 0.2s ease;
}
.campaign-card.st-active::before  { background: linear-gradient(90deg, #10B981, #059669); opacity: 0.85; }
.campaign-card.st-draft::before   { background: linear-gradient(90deg, #94A3B8, #64748B); opacity: 0.5; }
.campaign-card.st-completed::before { background: linear-gradient(90deg, #667eea, #764ba2); opacity: 0.6; }
.campaign-card.st-paused::before  { background: linear-gradient(90deg, #F59E0B, #D97706); opacity: 0.85; }

.campaign-card:hover {
  border-color: var(--primary-color);
  box-shadow: 0 8px 22px rgba(102,126,234,0.10);
  transform: translateY(-2px);
}
.campaign-card.active {
  border-color: var(--primary-color);
  background: rgba(102,126,234,0.04);
  box-shadow: 0 0 0 3px rgba(102,126,234,0.08);
}

.cc-head { display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; }
.badge { font-size: 0.7rem; font-weight: 600; padding: 3px 9px; border-radius: 999px; }
.objective-tag {
  font-size: 0.7rem;
  padding: 3px 8px;
  border-radius: 999px;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.cc-name {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  letter-spacing: -0.01em;
  line-height: 1.25;
}

.cc-period {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.78rem;
  color: var(--text-secondary);
  font-feature-settings: "tnum";
}

.cc-desc {
  font-size: 0.8rem;
  color: var(--text-secondary);
  line-height: 1.45;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.cc-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.5rem;
  padding: 0.625rem 0;
  border-top: 1px solid var(--border-color);
  border-bottom: 1px solid var(--border-color);
}
.cc-stat { text-align: center; }
.cs-val { font-size: 0.875rem; font-weight: 700; color: var(--text-primary); font-feature-settings: "tnum"; line-height: 1.1; }
.cs-key { font-size: 0.65rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.05em; margin-top: 2px; }

.font-mono { font-feature-settings: "tnum"; font-variant-numeric: tabular-nums; }

.roas-pill {
  display: inline-block;
  font-size: 0.78rem;
  font-weight: 700;
  padding: 1px 8px;
  border-radius: 999px;
}
.roas-good { background: rgba(16,185,129,0.14); color: #10B981; }
.roas-ok   { background: rgba(245,158,11,0.14); color: #F59E0B; }
.roas-bad  { background: rgba(239,68,68,0.10); color: #EF4444; }

/* Budget bar */
.cc-budget { display: flex; flex-direction: column; gap: 0.3rem; }
.cb-row { display: flex; justify-content: space-between; align-items: baseline; }
.cb-label {
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-secondary);
}
.cb-val { font-size: 0.78rem; color: var(--text-primary); font-weight: 600; }
.cb-of { color: var(--text-secondary); font-weight: 400; }

.cb-bar-wrap { height: 5px; background: var(--bg-secondary); border-radius: 3px; overflow: hidden; }
.cb-bar {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 3px;
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}
.cb-bar.cb-warn { background: linear-gradient(90deg, #F59E0B, #D97706); }
.cb-bar.cb-over { background: linear-gradient(90deg, #EF4444, #B91C1C); }

.cc-arrow {
  position: absolute;
  top: 1rem;
  right: 1rem;
  opacity: 0;
  transform: translate(-4px, 4px);
  transition: all 0.18s ease;
  color: var(--primary-color);
}
.campaign-card:hover .cc-arrow { opacity: 1; transform: translate(0, 0); }

/* ── Delete buttons ───────────────────────────────────── */
/* Table row: delete button appears on hover at the right edge */
.row-del-btn {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border: 1px solid var(--border-color);
  border-radius: 7px;
  background: var(--bg-primary);
  color: var(--text-secondary);
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.12s ease, background 0.12s, color 0.12s, border-color 0.12s;
}
.data-row:hover .row-del-btn,
.data-row:focus-within .row-del-btn { opacity: 1; }
.row-del-btn:hover {
  background: #fdecec;
  border-color: #f0b4b4;
  color: #d11a2a;
}

/* Card: hide the decorative arrow and use a delete button as the hover affordance */
.campaign-card .cc-arrow { display: none; }
.cc-del-btn {
  position: absolute;
  top: 0.85rem;
  right: 0.85rem;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: 1px solid var(--border-color);
  border-radius: 7px;
  background: var(--bg-primary);
  color: var(--text-secondary);
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.12s ease, background 0.12s, color 0.12s, border-color 0.12s;
}
.campaign-card:hover .cc-del-btn,
.campaign-card:focus-within .cc-del-btn { opacity: 1; }
.cc-del-btn:hover {
  background: #fdecec;
  border-color: #f0b4b4;
  color: #d11a2a;
}

.empty-grid {
  grid-column: 1 / -1;
  padding: 3rem 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.625rem;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

/* ── Timeline (gantt) ───────────────────────────────── */
.timeline-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
}

.tl-header {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
}
.tl-title { font-size: 0.95rem; font-weight: 700; color: var(--text-primary); margin: 0; letter-spacing: -0.01em; }
.tl-sub { font-size: 0.72rem; color: var(--text-secondary); margin: 2px 0 0; }

.tl-legend { display: flex; gap: 0.875rem; flex-wrap: wrap; }
.leg-item { display: inline-flex; align-items: center; gap: 0.3rem; font-size: 0.72rem; color: var(--text-secondary); }
.leg-dot { width: 8px; height: 8px; border-radius: 2px; }
.leg-active    .leg-dot { background: linear-gradient(135deg, #10B981, #059669); }
.leg-completed .leg-dot { background: linear-gradient(135deg, #667eea, #764ba2); }
.leg-draft     .leg-dot { background: linear-gradient(135deg, #94A3B8, #64748B); }

/* Gantt grid */
.gantt {
  display: grid;
  grid-template-columns: 220px 1fr;
  overflow-x: auto;
}

/* Months header — first col empty placeholder, second col = months */
.gantt-months {
  grid-column: 2;
  display: flex;
  position: relative;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-secondary);
}
.gantt-month {
  flex: 1;
  padding: 0.5rem 0.5rem;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-secondary);
  text-align: center;
  border-right: 1px solid var(--border-color);
  min-width: 75px;
}
.gantt-month:last-child { border-right: none; }
.gantt-month-current {
  background: rgba(102,126,234,0.08);
  color: var(--primary-color);
  font-weight: 700;
}

.gantt-today {
  position: absolute;
  top: 0; bottom: 0;
  z-index: 4;
  pointer-events: none;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.today-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #EC4899;
  margin-top: -4px;
  box-shadow: 0 0 0 3px rgba(236,72,153,0.2);
}
.today-label {
  font-size: 0.62rem;
  font-weight: 700;
  color: #EC4899;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  background: var(--bg-primary);
  padding: 1px 5px;
  border-radius: 4px;
  margin-top: 2px;
}

/* Today vertical line stretches across rows */
.gantt-rows { grid-column: 1 / -1; display: contents; }

.gantt-row {
  display: grid;
  grid-template-columns: 220px 1fr;
  align-items: center;
  background: transparent;
  border: none;
  border-bottom: 1px solid var(--border-color);
  padding: 0;
  cursor: pointer;
  font-family: inherit;
  text-align: left;
  transition: background 0.12s ease;
  position: relative;
}
.gantt-row:last-child { border-bottom: none; }
.gantt-row:hover { background: var(--bg-secondary); }
.gantt-row.active { background: rgba(102,126,234,0.05); }
.gantt-row.active::before {
  content: '';
  position: absolute;
  left: 0; top: 0; bottom: 0; width: 3px;
  background: linear-gradient(180deg, #667eea, #764ba2);
  z-index: 3;
}

.gr-name-col {
  padding: 0.75rem 1rem;
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}
.gr-name {
  font-size: 0.825rem;
  font-weight: 600;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.gr-meta { font-size: 0.68rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.05em; }

.gr-track {
  position: relative;
  height: 48px;
  display: flex;
}

.track-cell {
  flex: 1;
  border-right: 1px dashed var(--border-color);
  min-width: 75px;
}
.track-cell:last-child { border-right: none; }
.track-cell-current { background: rgba(102,126,234,0.04); }

.gr-bar {
  position: absolute;
  top: 50%;
  height: 24px;
  margin-top: -12px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  padding: 0 0.625rem;
  font-size: 0.72rem;
  font-weight: 600;
  color: white;
  overflow: hidden;
  z-index: 2;
  transition: filter 0.15s ease, transform 0.15s ease;
  cursor: pointer;
}
.gr-bar:hover { filter: brightness(1.1); transform: scaleY(1.1); }

.gr-bar.st-active    { background: linear-gradient(135deg, #10B981, #059669); box-shadow: 0 2px 6px rgba(16,185,129,0.3); }
.gr-bar.st-completed { background: linear-gradient(135deg, #667eea, #764ba2); box-shadow: 0 2px 6px rgba(102,126,234,0.3); }
.gr-bar.st-draft     {
  background: repeating-linear-gradient(45deg, #94A3B8, #94A3B8 6px, #64748B 6px, #64748B 12px);
  box-shadow: 0 2px 4px rgba(100,116,139,0.2);
}
.gr-bar.st-paused    { background: linear-gradient(135deg, #F59E0B, #D97706); box-shadow: 0 2px 6px rgba(245,158,11,0.3); }

.bar-label {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.bar-status-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: rgba(255,255,255,0.8);
  flex-shrink: 0;
}

/* ── Shared modal chrome ────────────────────────────── */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15,23,42,0.6);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  backdrop-filter: blur(6px);
}
.modal {
  background: var(--bg-primary);
  border-radius: 16px;
  width: 100%;
  max-width: 560px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 24px 64px rgba(15,23,42,0.28), 0 0 0 1px rgba(255,255,255,0.06);
  overflow: hidden;
}
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--border-color);
}
.modal-title { font-size: 1rem; font-weight: 700; color: var(--text-primary); margin: 0; letter-spacing: -0.01em; }
.modal-close {
  background: none; border: none;
  width: 32px; height: 32px; border-radius: 8px;
  cursor: pointer; color: var(--text-secondary);
  display: flex; align-items: center; justify-content: center;
  transition: background 0.15s, color 0.15s;
}
.modal-close:hover { background: var(--bg-secondary); color: var(--text-primary); }
.modal-body { padding: 1.25rem; overflow-y: auto; }
.modal-footer {
  padding: 0.875rem 1.25rem;
  border-top: 1px solid var(--border-color);
  display: flex; justify-content: flex-end; gap: 0.5rem;
  background: var(--bg-secondary);
}

/* ── Shared field atoms ─────────────────────────────── */
.field { display: flex; flex-direction: column; gap: 0.3rem; min-width: 0; }
.field-full { grid-column: 1 / -1; }
.field-label {
  font-size: 0.72rem; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.06em;
  color: var(--text-secondary);
}
.req { color: #EF4444; margin-left: 2px; }
.opt { font-weight: 400; text-transform: none; letter-spacing: 0; color: var(--text-secondary); font-size: 0.7rem; }
.field-input {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border-color); border-radius: 8px;
  background: var(--bg-primary); color: var(--text-primary);
  font-size: 0.875rem; font-family: inherit;
  width: 100%; box-sizing: border-box;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.field-input:focus { outline: none; border-color: var(--primary-color); box-shadow: 0 0 0 3px rgba(102,126,234,0.15); }
.field-input:disabled { opacity: 0.5; cursor: not-allowed; }
.field-textarea { resize: vertical; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }

/* ═══════════════════════════════════════════════════
   WIZARD MODAL
   ══════════════════════════════════════════════════ */
.wizard-modal { max-width: 680px; }

/* Header */
.wizard-header {
  display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem;
  padding: 1.375rem 1.5rem 1rem;
  background: linear-gradient(135deg, rgba(102,126,234,0.06), rgba(118,75,162,0.03));
  border-bottom: 1px solid var(--border-color);
}
.wizard-meta { display: flex; flex-direction: column; gap: 0.2rem; }
.wizard-eyebrow {
  font-size: 0.65rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.12em; color: var(--primary-color); opacity: 0.9;
}
.wizard-title { font-size: 1.1rem; font-weight: 800; color: var(--text-primary); margin: 0; letter-spacing: -0.02em; }
.wizard-sub { font-size: 0.8rem; color: var(--text-secondary); margin: 0; }

/* Step indicator */
.wizard-steps {
  display: flex; align-items: center; gap: 0;
  padding: 0.875rem 1.5rem;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-secondary);
}
.ws-step { display: flex; align-items: center; gap: 0.5rem; font-size: 0.78rem; font-weight: 600; color: var(--text-secondary); }
.ws-step.active { color: var(--primary-color); }
.ws-step.done { color: #10B981; }
.ws-dot {
  width: 22px; height: 22px; border-radius: 50%;
  border: 2px solid var(--border-color);
  display: flex; align-items: center; justify-content: center;
  font-size: 0.68rem; font-weight: 700; background: var(--bg-primary);
  color: var(--text-secondary); flex-shrink: 0;
}
.ws-step.active .ws-dot { border-color: var(--primary-color); color: var(--primary-color); background: rgba(102,126,234,0.1); }
.ws-step.done .ws-dot { border-color: #10B981; background: rgba(16,185,129,0.1); color: #10B981; }
.ws-line { flex: 1; height: 2px; background: var(--border-color); margin: 0 0.75rem; border-radius: 1px; }
.ws-line.done { background: linear-gradient(90deg, #10B981, rgba(16,185,129,0.3)); }

/* Wizard body */
.wizard-body { flex: 1; overflow-y: auto; padding: 1.375rem 1.5rem; display: flex; flex-direction: column; gap: 1rem; }

/* Step 1 fields */
.wf-name-block { display: flex; flex-direction: column; gap: 0.35rem; }
.name-input { font-size: 1.05rem; font-weight: 600; padding: 0.625rem 0.875rem; }
.name-input::placeholder { font-weight: 400; font-size: 0.9rem; }
.wf-row { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }
.wf-row-3 { grid-template-columns: 1fr 1fr 1fr; }

.targets-block {
  background: var(--bg-secondary); border-radius: 10px; padding: 0.875rem 1rem;
  display: flex; flex-direction: column; gap: 0.625rem;
}
.targets-title {
  display: flex; align-items: center; gap: 0.4rem;
  font-size: 0.72rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.06em; color: var(--text-secondary);
}
.targets-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.5rem; }
.tg-field { display: flex; flex-direction: column; gap: 0.25rem; }
.tg-label { font-size: 0.64rem; color: var(--text-secondary); font-weight: 600; }

/* Wizard footer */
.wizard-footer {
  padding: 0.875rem 1.5rem;
  border-top: 1px solid var(--border-color);
  display: flex; align-items: center; justify-content: space-between;
  background: var(--bg-secondary);
}
.wf-left, .wf-right { display: flex; gap: 0.5rem; }
.hub-btn:disabled { opacity: 0.45; cursor: not-allowed; }
.hub-btn:disabled:hover { transform: none; box-shadow: none; }

/* ═══════════════════════════════════════════════════
   STEP 2 · METHODS
   ══════════════════════════════════════════════════ */
.wizard-methods { padding: 0; gap: 0; }

/* Channel tabs */
.ch-tabs {
  display: flex; border-bottom: 1px solid var(--border-color);
  padding: 0 1.5rem; background: var(--bg-primary);
  overflow-x: auto; scrollbar-width: none;
}
.ch-tabs::-webkit-scrollbar { display: none; }
.ch-tab {
  display: inline-flex; align-items: center; gap: 0.45rem;
  padding: 0.75rem 1rem; border: none; background: transparent;
  font-size: 0.85rem; font-weight: 500; color: var(--text-secondary);
  cursor: pointer; border-bottom: 2px solid transparent;
  margin-bottom: -1px; white-space: nowrap; font-family: inherit;
  transition: color 0.15s, border-color 0.15s;
}
.ch-tab:hover { color: var(--text-primary); }
.ch-tab.active { font-weight: 700; }
.ch-tab-icon { display: flex; align-items: center; opacity: 0.85; }
.ch-tab-badge {
  font-size: 0.65rem; font-weight: 700; color: white;
  padding: 1px 6px; border-radius: 999px; line-height: 1.5;
}
.ch-tab-src {
  font-size: 0.6rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em;
}
.ch-tab-src.src-auto   { color: #10B981; }
.ch-tab-src.src-manual { color: #F59E0B; }

/* Method pane */
.method-pane { padding: 1.25rem 1.5rem; display: flex; flex-direction: column; gap: 0.875rem; min-height: 320px; }
.method-pane-head { display: flex; flex-direction: column; gap: 0.625rem; }
.method-pane-desc { font-size: 0.82rem; color: var(--text-secondary); margin: 0; line-height: 1.5; }
.mp-filters { display: flex; flex-direction: column; gap: 0.5rem; }
/* In this flex column, the shared `flex: 1 1 240px` would turn flex-basis into
   a 240px height, leaving a tall empty box with the search icon floating in the
   middle. Reset it so the wrap hugs its content height. */
.mp-filters .search-input-wrap { flex: 0 0 auto; }

/* Platform filter buttons */
.platform-filters { display: flex; flex-wrap: wrap; gap: 0.35rem; }
.pf-btn {
  padding: 0.3rem 0.75rem; border: 1px solid var(--border-color);
  border-radius: 999px; background: var(--bg-primary); color: var(--text-secondary);
  font-size: 0.72rem; font-weight: 600; cursor: pointer; font-family: inherit;
  transition: all 0.15s ease;
}
.pf-btn:hover { border-color: var(--primary-color); color: var(--primary-color); }
.pf-btn.active { background: var(--primary-color); border-color: var(--primary-color); color: white; }

/* Posts grid picker */
.posts-grid {
  display: flex; flex-direction: column; gap: 0.35rem;
  max-height: 320px; overflow-y: auto;
  border: 1px solid var(--border-color); border-radius: 10px; padding: 0.375rem;
}
.post-pick {
  display: grid; grid-template-columns: auto auto 1fr auto;
  gap: 0.625rem; align-items: center;
  padding: 0.5rem 0.625rem; border-radius: 8px; cursor: pointer;
  transition: background 0.12s; position: relative;
}
.post-pick:hover { background: var(--bg-secondary); }
.post-pick.selected { background: rgba(102,126,234,0.06); }
.post-pick-check { display: none; }
.post-pick-thumb {
  width: 32px; height: 32px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  color: white; flex-shrink: 0;
}
.post-pick-info { min-width: 0; }
.post-pick-title { font-size: 0.82rem; font-weight: 600; color: var(--text-primary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.post-pick-meta { display: flex; align-items: center; gap: 0.4rem; margin-top: 2px; flex-wrap: wrap; }
.platform-pill { font-size: 0.62rem; font-weight: 600; padding: 1px 6px; border-radius: 999px; }
.muted-sm { font-size: 0.7rem; color: var(--text-secondary); }
.eng-badge { font-size: 0.68rem; font-weight: 700; color: var(--text-secondary); }
.post-pick-selected-mark {
  width: 20px; height: 20px; border-radius: 50%;
  background: var(--primary-color); color: white;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.pick-empty { padding: 2rem; text-align: center; color: var(--text-secondary); font-size: 0.82rem; }
.pick-summary {
  display: inline-flex; align-items: center; gap: 0.4rem;
  font-size: 0.78rem; font-weight: 600; color: #10B981;
  background: rgba(16,185,129,0.08); padding: 0.35rem 0.75rem; border-radius: 999px;
  align-self: flex-start;
}

/* Influencer combobox */
.inf-search-wrap { position: relative; }
.inf-dropdown {
  position: absolute; top: calc(100% + 4px); left: 0; right: 0; z-index: 50;
  background: var(--bg-primary); border: 1px solid var(--border-color);
  border-radius: 10px; box-shadow: 0 8px 24px rgba(15,23,42,0.12);
  overflow: hidden; max-height: 260px; overflow-y: auto;
}
.inf-option {
  display: flex; align-items: center; gap: 0.625rem;
  padding: 0.625rem 0.875rem; width: 100%; text-align: left;
  border: none; background: transparent; cursor: pointer; font-family: inherit;
  transition: background 0.1s;
}
.inf-option:hover:not(:disabled) { background: var(--bg-secondary); }
.inf-option:disabled { opacity: 0.5; cursor: default; }
.inf-opt-avatar {
  width: 30px; height: 30px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  color: white; font-weight: 700; font-size: 0.8rem; flex-shrink: 0;
}
.inf-opt-info { display: flex; flex-direction: column; gap: 1px; flex: 1; min-width: 0; }
.inf-opt-name { font-size: 0.85rem; font-weight: 600; color: var(--text-primary); }
.inf-opt-alias { font-size: 0.72rem; color: var(--text-secondary); }
.inf-opt-added { font-size: 0.7rem; font-weight: 600; color: #10B981; }
.inf-opt-stats { font-size: 0.72rem; color: var(--text-secondary); }
.inf-option-empty { color: var(--text-secondary); font-size: 0.82rem; justify-content: center; }
.inf-option-new {
  color: var(--primary-color); font-size: 0.82rem; font-weight: 600;
  border-top: 1px solid var(--border-color); gap: 0.4rem; padding: 0.625rem 0.875rem;
}
.inf-option-new:hover { background: rgba(102,126,234,0.06) !important; }

/* Selected influencer chips */
.inf-selected-list { display: flex; flex-direction: column; gap: 0.375rem; }
.inf-chip {
  display: flex; align-items: center; gap: 0.625rem;
  padding: 0.5rem 0.75rem; border-radius: 9px;
  background: var(--bg-secondary); border: 1px solid var(--border-color);
}
.inf-chip-avatar {
  width: 28px; height: 28px; border-radius: 7px;
  display: flex; align-items: center; justify-content: center;
  color: white; font-weight: 700; font-size: 0.75rem; flex-shrink: 0;
}
.inf-chip-name { font-size: 0.85rem; font-weight: 600; color: var(--text-primary); flex: 1; }
.inf-chip-alias { font-size: 0.72rem; color: var(--text-secondary); }
.inf-chip-remove {
  background: none; border: none; cursor: pointer; color: var(--text-secondary);
  width: 22px; height: 22px; border-radius: 5px;
  display: flex; align-items: center; justify-content: center;
  transition: background 0.12s, color 0.12s; padding: 0;
}
.inf-chip-remove:hover { background: rgba(239,68,68,0.1); color: #EF4444; }

/* Ad sets */
.ads-list { display: flex; flex-direction: column; gap: 0.5rem; }
.ad-set-row {
  display: grid; grid-template-columns: 1fr auto;
  gap: 0.5rem; align-items: center;
}
.ad-set-remove {
  width: 32px; height: 32px; background: none;
  border: 1px solid var(--border-color); border-radius: 7px;
  cursor: pointer; color: var(--text-secondary);
  display: flex; align-items: center; justify-content: center;
  transition: all 0.12s; padding: 0; flex-shrink: 0;
}
.ad-set-remove:hover { border-color: #EF4444; color: #EF4444; background: rgba(239,68,68,0.06); }
.add-adset-btn {
  display: inline-flex; align-items: center; gap: 0.4rem;
  padding: 0.5rem 0.875rem; border: 1px dashed var(--border-color);
  border-radius: 8px; background: transparent; color: var(--primary-color);
  font-size: 0.82rem; font-weight: 600; cursor: pointer; font-family: inherit;
  transition: all 0.15s; align-self: flex-start; margin-top: 0.25rem;
}
.add-adset-btn:hover { border-color: var(--primary-color); background: rgba(102,126,234,0.05); }

/* search shared */
.search-input-wrap { position: relative; }
.search-icon { position: absolute; left: 0.625rem; top: 50%; transform: translateY(-50%); color: var(--text-secondary); pointer-events: none; }
.search-input { padding-left: 2rem; }

/* ════════════════════════════════════════════════════
   PRODUCT PICKER
   ════════════════════════════════════════════════════ */

/* Campaign-level products block */
.camp-prods-block {
  padding: 1rem 1.5rem 1.125rem;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
  background: linear-gradient(135deg, rgba(102,126,234,0.03), rgba(118,75,162,0.02));
}
.cpb-header {
  display: flex;
  align-items: center;
  gap: 0.45rem;
}
.cpb-icon { color: var(--primary-color); opacity: 0.85; flex-shrink: 0; }
.cpb-title {
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
.cpb-opt { font-size: 0.68rem; color: var(--text-secondary); font-weight: 400; }
.cpb-hint {
  font-size: 0.78rem;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.45;
}

/* Shared picker-wrap (anchor for dropdown) */
.prod-picker-wrap { position: relative; }

/* Close button inside search */
.picker-close-btn {
  position: absolute;
  right: 0.5rem; top: 50%; transform: translateY(-50%);
  background: none; border: none; cursor: pointer;
  color: var(--text-secondary); display: flex; align-items: center;
  padding: 4px;
  transition: color 0.12s;
}
.picker-close-btn:hover { color: var(--text-primary); }

/* Large dropdown (campaign-level) */
.prod-dropdown {
  position: absolute; top: calc(100% + 4px); left: 0; right: 0; z-index: 60;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(15,23,42,0.14);
  overflow: hidden;
  max-height: 280px;
  overflow-y: auto;
}
.prod-option {
  display: flex; align-items: center; gap: 0.625rem;
  padding: 0.55rem 0.875rem; width: 100%; text-align: left;
  border: none; background: transparent; cursor: pointer; font-family: inherit;
  transition: background 0.1s;
}
.prod-option:hover:not(.prod-option-added) { background: var(--bg-secondary); }
.prod-option-added { opacity: 0.55; cursor: default; }
.prod-opt-icon {
  width: 26px; height: 26px; border-radius: 7px;
  background: rgba(102,126,234,0.1); color: var(--primary-color);
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.prod-opt-info { display: flex; flex-direction: column; gap: 1px; flex: 1; min-width: 0; }
.prod-opt-name {
  font-size: 0.85rem; font-weight: 600; color: var(--text-primary);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.prod-opt-meta { font-size: 0.7rem; color: var(--text-secondary); }
.prod-opt-price { font-size: 0.78rem; font-weight: 700; color: var(--text-primary); font-feature-settings: "tnum"; white-space: nowrap; }
.prod-opt-check { color: #10B981; flex-shrink: 0; }
.prod-dropdown-empty { padding: 0.875rem 1rem; font-size: 0.82rem; color: var(--text-secondary); text-align: center; }

/* Product chips (campaign-level) */
.prod-chips-list {
  display: flex; flex-wrap: wrap; gap: 0.375rem;
}
.prod-chip {
  display: inline-flex; align-items: center; gap: 0.35rem;
  padding: 0.3rem 0.5rem 0.3rem 0.625rem;
  background: rgba(102,126,234,0.08);
  border: 1px solid rgba(102,126,234,0.2);
  border-radius: 999px;
  font-size: 0.78rem;
}
.pchip-icon { color: var(--primary-color); flex-shrink: 0; }
.pchip-name { font-weight: 600; color: var(--text-primary); }
.pchip-sku {
  font-size: 0.68rem; color: var(--text-secondary);
  background: var(--bg-secondary); padding: 0px 5px; border-radius: 4px;
}
.pchip-price { font-size: 0.72rem; font-weight: 700; color: var(--primary-color); font-feature-settings: "tnum"; }
.pchip-remove {
  background: none; border: none; cursor: pointer; color: var(--text-secondary);
  width: 18px; height: 18px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center; padding: 0;
  transition: background 0.12s, color 0.12s; margin-left: 1px;
}
.pchip-remove:hover { background: rgba(239,68,68,0.12); color: #EF4444; }

/* ── Per-item products section (posts) ─────── */
.per-item-prods {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  /* No `overflow: hidden` here: it would clip the absolutely-positioned
     `.prod-dd-small` "Afegir" dropdown. Inner corners are rounded on the
     children instead (see .pip-section-title). */
}
.pip-section-title {
  display: flex; align-items: center; gap: 0.4rem;
  padding: 0.5rem 0.75rem;
  font-size: 0.7rem; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.06em;
  color: var(--text-secondary);
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
  border-radius: 9px 9px 0 0;
}
.pip-row {
  padding: 0.5rem 0.75rem;
  border-bottom: 1px solid var(--border-color);
  display: flex; flex-direction: column; gap: 0.4rem;
}
.pip-row:last-child { border-bottom: none; }
.pip-row-header {
  display: flex; align-items: center; gap: 0.5rem;
  min-width: 0;
}
.pip-thumb {
  width: 22px; height: 22px; border-radius: 5px;
  display: flex; align-items: center; justify-content: center;
  color: white; flex-shrink: 0; font-size: 0;
}
.pip-post-title {
  font-size: 0.78rem; font-weight: 600; color: var(--text-primary);
  flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}

/* Products row (chips + add button) */
.pip-products-row {
  display: flex; flex-wrap: wrap; gap: 0.3rem; align-items: center;
}
.pip-products-inf {
  padding: 0.3rem 0.75rem 0.5rem;
  border-top: 1px dashed var(--border-color);
  margin: 0 -0.75rem -0.25rem;
}
.pip-products-ad {
  padding: 0.375rem 0;
}

/* Small product chip */
.prod-chip-sm {
  display: inline-flex; align-items: center; gap: 0.25rem;
  padding: 0.2rem 0.4rem 0.2rem 0.5rem;
  background: rgba(102,126,234,0.07);
  border: 1px solid rgba(102,126,234,0.18);
  border-radius: 999px;
  font-size: 0.72rem;
}
.pcsm-name { font-weight: 600; color: var(--text-primary); }
.pcsm-sku {
  font-size: 0.64rem; color: var(--text-secondary);
  background: var(--bg-primary); padding: 0 4px; border-radius: 3px;
}
.pcsm-rm {
  background: none; border: none; cursor: pointer; color: var(--text-secondary);
  width: 14px; height: 14px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center; padding: 0;
  transition: background 0.12s, color 0.12s;
}
.pcsm-rm:hover { background: rgba(239,68,68,0.12); color: #EF4444; }

/* "Afegir" trigger button */
.pip-add-btn {
  display: inline-flex; align-items: center; gap: 0.25rem;
  padding: 0.2rem 0.55rem;
  border: 1px dashed var(--border-color);
  border-radius: 999px;
  background: transparent; color: var(--primary-color);
  font-size: 0.72rem; font-weight: 600; cursor: pointer; font-family: inherit;
  transition: all 0.12s;
}
.pip-add-btn:hover { border-color: var(--primary-color); background: rgba(102,126,234,0.06); }

/* Small dropdown */
.pip-picker { position: relative; }
.prod-dd-small {
  position: absolute; top: calc(100% + 4px); left: 0; z-index: 70;
  width: 280px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(15,23,42,0.16);
  overflow: hidden;
}
.pdd-search-row {
  display: flex; align-items: center; gap: 0.375rem;
  padding: 0.5rem 0.625rem;
  border-bottom: 1px solid var(--border-color);
}
.pdd-search-icon { color: var(--text-secondary); flex-shrink: 0; }
.pdd-input {
  flex: 1; border: none; background: transparent;
  font-size: 0.82rem; color: var(--text-primary); outline: none; font-family: inherit;
}
.pdd-close {
  background: none; border: none; cursor: pointer; color: var(--text-secondary);
  display: flex; align-items: center; padding: 2px;
  transition: color 0.12s;
}
.pdd-close:hover { color: var(--text-primary); }
.pdd-list { max-height: 200px; overflow-y: auto; }
.pdd-item {
  display: flex; align-items: center; gap: 0.4rem;
  padding: 0.45rem 0.75rem; width: 100%; text-align: left;
  border: none; background: transparent; cursor: pointer; font-family: inherit;
  font-size: 0.8rem; transition: background 0.1s;
}
.pdd-item:hover:not(.pdd-added) { background: var(--bg-secondary); }
.pdd-added { opacity: 0.5; cursor: default; }
.pdd-name { flex: 1; font-weight: 600; color: var(--text-primary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.pdd-sku { font-size: 0.68rem; color: var(--text-secondary); white-space: nowrap; }
.pdd-check { color: #10B981; flex-shrink: 0; }

/* Influencer chip expansion */
.inf-chip-expanded {
  flex-direction: column !important;
  align-items: stretch !important;
  padding: 0.5rem 0.75rem 0.5rem !important;
  gap: 0 !important;
}
.inf-chip-top {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding-bottom: 0.4rem;
}

/* Ad set group */
.ad-set-group {
  display: flex; flex-direction: column; gap: 0;
  border: 1px solid var(--border-color); border-radius: 8px;
  /* No `overflow: hidden`: it would clip the product picker dropdown.
     Inner corners are rounded on the first/last children instead. */
}
.ad-set-group + .ad-set-group { margin-top: 0.5rem; }
.ad-set-group .ad-set-row {
  border-bottom: 1px solid var(--border-color);
  padding: 0.5rem;
  background: var(--bg-secondary);
  border-radius: 7px 7px 0 0;
}
.pip-products-ad {
  padding: 0.4rem 0.5rem;
  background: var(--bg-primary);
  border-radius: 0 0 7px 7px;
}

/* ── Responsive ────────────────────────────────────── */
@media (max-width: 1100px) {
  .kpi-strip { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 900px) {
  .gantt { grid-template-columns: 160px 1fr; }
  .gantt-row { grid-template-columns: 160px 1fr; }
  .gr-name-col { padding: 0.625rem 0.75rem; }
}

@media (max-width: 600px) {
  .kpi-strip { grid-template-columns: 1fr 1fr; gap: 0.5rem; }
  .campaigns-grid { grid-template-columns: 1fr; }
  .form-grid { grid-template-columns: 1fr; }
  .wf-row, .wf-row-3 { grid-template-columns: 1fr; }
  .targets-grid { grid-template-columns: repeat(2, 1fr); }
  .cc-stats { grid-template-columns: repeat(2, 1fr); gap: 0.625rem; }
}
</style>
