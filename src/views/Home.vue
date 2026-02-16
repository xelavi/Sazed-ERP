<template>
  <div class="home-view">
    <!-- Page Header -->
    <header class="page-header">
      <div class="header-greeting">
        <p class="header-date">{{ currentDate }}</p>
        <h1 class="greeting-text">Good afternoon, Alex</h1>
      </div>
      <div class="header-stats">
        <button class="stat-btn">My week</button>
        <button class="stat-btn">
          <span class="stat-dot"></span>
          0 tasks completed
        </button>
        <button class="stat-btn">1 collaborator</button>
        <button class="stat-btn">Customize</button>
      </div>
    </header>

    <!-- Main Content -->
    <div class="content-area">
      <!-- My Tasks Section -->
      <section class="tasks-section">
        <div class="tasks-header">
          <div class="tasks-title-row">
            <div class="avatar-circle">A</div>
            <h2 class="tasks-title">My tasks</h2>
          </div>
          <button class="more-btn">
            <MoreHorizontal :size="20" />
          </button>
        </div>

        <!-- Tabs -->
        <div class="tabs">
          <button 
            v-for="tab in tabs" 
            :key="tab.id" 
            class="tab-btn"
            :class="{ active: activeTab === tab.id }"
            @click="activeTab = tab.id"
          >
            {{ tab.label }}
          </button>
        </div>

        <!-- Create Task -->
        <button class="create-task-btn">
          <Plus :size="16" />
          <span>Create task</span>
        </button>

        <!-- Task List -->
        <div class="task-list">
          <div 
            v-for="task in filteredTasks" 
            :key="task.id" 
            class="task-row"
            :class="{ completed: task.completed }"
          >
            <label class="task-checkbox">
              <input type="checkbox" v-model="task.completed" />
              <span class="checkbox-visual">
                <Check v-if="task.completed" :size="12" />
              </span>
            </label>
            <span class="task-title" :class="{ done: task.completed }">{{ task.title }}</span>
            <div class="task-meta">
              <span 
                v-for="(tag, i) in task.tags" 
                :key="i" 
                class="task-tag"
                :class="tag.colorClass"
              >
                {{ tag.label }}
              </span>
              <span class="task-date">{{ task.dueDate }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Learn Section -->
      <section class="learn-section">
        <h2 class="learn-title">Learn ProjectHub</h2>
        <div class="learn-grid">
          <div 
            v-for="card in learningCards" 
            :key="card.id" 
            class="learn-card"
          >
            <div class="learn-illustration" :class="card.bgClass">
              <component :is="card.icon" :size="48" class="learn-icon" />
              <div class="learn-duration">
                <Clock :size="12" />
                <span>{{ card.duration }}</span>
              </div>
            </div>
            <div class="learn-body">
              <h3 class="learn-card-title">{{ card.title }}</h3>
              <p class="learn-card-desc">{{ card.description }}</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { MoreHorizontal, Plus, Check, Clock, Rocket, ListChecks } from 'lucide-vue-next'

const currentDate = computed(() => {
  const now = new Date()
  return now.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })
})

const activeTab = ref('upcoming')

const tabs = [
  { id: 'upcoming', label: 'Upcoming' },
  { id: 'overdue', label: 'Overdue' },
  { id: 'completed', label: 'Completed' },
]

const tasks = ref([
  {
    id: '1',
    title: 'Review design mockups for landing page',
    completed: false,
    tags: [
      { label: 'Design', colorClass: 'tag-purple' },
      { label: 'High Priority', colorClass: 'tag-red' },
    ],
    dueDate: 'Today',
    status: 'upcoming',
  },
  {
    id: '2',
    title: 'Update user documentation',
    completed: true,
    tags: [{ label: 'Documentation', colorClass: 'tag-blue' }],
    dueDate: 'Yesterday',
    status: 'completed',
  },
  {
    id: '3',
    title: 'Prepare Q1 presentation slides',
    completed: false,
    tags: [{ label: 'Marketing', colorClass: 'tag-green' }],
    dueDate: 'Feb 18',
    status: 'upcoming',
  },
  {
    id: '4',
    title: 'Code review for mobile app PR #234',
    completed: false,
    tags: [
      { label: 'Development', colorClass: 'tag-orange' },
      { label: 'Mobile', colorClass: 'tag-pink' },
    ],
    dueDate: 'Feb 17',
    status: 'upcoming',
  },
])

const filteredTasks = computed(() => {
  if (activeTab.value === 'completed') return tasks.value.filter(t => t.completed)
  if (activeTab.value === 'overdue') return tasks.value.filter(t => !t.completed && t.dueDate === 'Yesterday')
  return tasks.value
})

const learningCards = [
  {
    id: '1',
    title: 'Master Project Management',
    description: 'Learn the fundamentals of agile project management in 30 minutes',
    duration: '30 min',
    bgClass: 'bg-pink',
    icon: Rocket,
  },
  {
    id: '2',
    title: 'Team Collaboration Best Practices',
    description: 'Discover tips to improve team communication and productivity',
    duration: '20 min',
    bgClass: 'bg-red',
    icon: ListChecks,
  },
]
</script>

<style scoped>
.home-view {
  min-height: 100%;
}

/* ============================
   PAGE HEADER
   ============================ */
.page-header {
  padding: 0 0 1.75rem;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 2rem;
}

.header-date {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  margin: 0 0 0.375rem;
}

.greeting-text {
  font-size: var(--font-size-3xl);
  font-weight: 300;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.2;
}

.header-stats {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  flex-wrap: wrap;
}

.stat-btn {
  padding: 0.5rem 0.875rem;
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  background: none;
  border: none;
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
  font-family: var(--font-family);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  white-space: nowrap;
}

.stat-btn:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.stat-dot {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent-purple), var(--accent-pink));
  flex-shrink: 0;
}

/* ============================
   CONTENT
   ============================ */
.content-area {
  padding: 2rem 0 0;
}

/* ============================
   TASKS SECTION
   ============================ */
.tasks-section {
  margin-bottom: 3rem;
}

.tasks-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.25rem;
}

.tasks-title-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.avatar-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent-purple), var(--accent-pink));
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: var(--font-size-base);
  flex-shrink: 0;
}

.tasks-title {
  font-size: var(--font-size-xl);
  font-weight: 500;
  color: var(--text-primary);
  margin: 0;
}

.more-btn {
  background: none;
  border: none;
  color: var(--text-tertiary);
  padding: 0.375rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all var(--transition-fast);
  display: flex;
}

.more-btn:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

/* Tabs */
.tabs {
  display: flex;
  gap: 1.5rem;
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 0.75rem;
}

.tab-btn {
  position: relative;
  padding: 0.75rem 0.125rem;
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--text-tertiary);
  background: none;
  border: none;
  cursor: pointer;
  font-family: var(--font-family);
  transition: color var(--transition-fast);
}

.tab-btn:hover {
  color: var(--text-secondary);
}

.tab-btn.active {
  color: var(--text-primary);
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--text-primary);
  border-radius: 1px 1px 0 0;
}

/* Create Task */
.create-task-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.25rem;
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  background: none;
  border: none;
  cursor: pointer;
  font-family: var(--font-family);
  transition: color var(--transition-fast);
  margin-bottom: 0.25rem;
}

.create-task-btn:hover {
  color: var(--text-primary);
}

/* Task List */
.task-list {
  display: flex;
  flex-direction: column;
}

.task-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 0.5rem;
  border-radius: var(--border-radius-sm);
  transition: background var(--transition-fast);
}

.task-row:hover {
  background: var(--bg-secondary);
}

.task-checkbox {
  display: flex;
  align-items: center;
  cursor: pointer;
  flex-shrink: 0;
}

.task-checkbox input {
  display: none;
}

.checkbox-visual {
  width: 20px;
  height: 20px;
  border: 2px solid var(--border-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
  background: #fff;
}

.task-checkbox input:checked + .checkbox-visual {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: #fff;
}

.task-title {
  flex: 1;
  font-size: var(--font-size-sm);
  color: var(--text-primary);
  min-width: 0;
}

.task-title.done {
  text-decoration: line-through;
  color: var(--text-tertiary);
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.task-tag {
  padding: 0.125rem 0.5rem;
  font-size: var(--font-size-xs);
  font-weight: 400;
  border-radius: 4px;
  white-space: nowrap;
}

.tag-purple { background: #f3f0ff; color: #6d28d9; }
.tag-red { background: #fef2f2; color: #dc2626; }
.tag-blue { background: #eff6ff; color: #2563eb; }
.tag-green { background: #ecfdf5; color: #059669; }
.tag-orange { background: #fff7ed; color: #ea580c; }
.tag-pink { background: #fdf2f8; color: #db2777; }

.task-date {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  min-width: 70px;
  text-align: right;
}

/* ============================
   LEARN SECTION
   ============================ */
.learn-section {
  margin-top: 1rem;
}

.learn-title {
  font-size: var(--font-size-xl);
  font-weight: 500;
  color: var(--text-primary);
  margin: 0 0 1rem;
}

.learn-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.learn-card {
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  overflow: hidden;
  cursor: pointer;
  transition: box-shadow var(--transition-base);
}

.learn-card:hover {
  box-shadow: var(--shadow-md);
}

.learn-illustration {
  height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.learn-illustration.bg-pink {
  background: linear-gradient(135deg, #fce7f3, #fdf2f8);
}

.learn-illustration.bg-red {
  background: linear-gradient(135deg, #fee2e2, #fef2f2);
}

.learn-icon {
  opacity: 0.6;
}

.bg-pink .learn-icon { color: #ec4899; }
.bg-red .learn-icon { color: #ef4444; }

.learn-duration {
  position: absolute;
  bottom: 0.5rem;
  left: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 4px;
  font-size: var(--font-size-xs);
  font-weight: 500;
}

.bg-pink .learn-duration { color: #9d174d; }
.bg-red .learn-duration { color: #991b1b; }

.learn-body {
  padding: 1rem 1.25rem 1.25rem;
}

.learn-card-title {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--text-primary);
  margin: 0 0 0.375rem;
}

.learn-card-desc {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.5;
}

/* ============================
   RESPONSIVE
   ============================ */
@media (max-width: 1024px) {
  .task-meta {
    flex-wrap: wrap;
  }
}

@media (max-width: 900px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .learn-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .greeting-text {
    font-size: var(--font-size-2xl);
  }
  .header-stats {
    gap: 0.25rem;
  }
  .stat-btn {
    padding: 0.375rem 0.625rem;
    font-size: var(--font-size-xs);
  }
}

@media (max-width: 480px) {
  .task-row {
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  .task-meta {
    width: 100%;
    padding-left: 2.25rem;
  }
  .greeting-text {
    font-size: var(--font-size-xl);
  }
}
</style>

