<template>
  <div class="cockpit">
    <!-- Subtle tech background -->
    <div class="cockpit-bg" />

    <!-- ======== TOP HEADER ======== -->
    <header class="cockpit-header">
      <div class="h-left">
        <div class="h-brand">
          <span class="h-badge">AI-Ops</span>
          <span class="h-title">智能运维大数据驾驶舱</span>
        </div>
        <div class="h-time">
          <el-icon :size="14"><Clock /></el-icon>
          <span>{{ currentTime }}</span>
        </div>
      </div>
      <div class="h-right">
        <span class="h-live" />
        <span class="h-live-text">系统运行中</span>
        <span class="h-divider" />
        <el-date-picker
          v-model="dateRange"
          type="datetimerange"
          size="small"
          range-separator="至"
          class="h-picker"
        />
      </div>
    </header>

    <!-- ======== KPI ROW ======== -->
    <section class="kpi-row">
      <div v-for="c in kpiCards" :key="c.label" class="kpi-card">
        <div class="kpi-icon-wrap" :style="{ background: c.iconBg, color: c.color }">
          <el-icon :size="22"><component :is="c.icon" /></el-icon>
        </div>
        <div class="kpi-body">
          <div class="kpi-top">
            <span class="kpi-val" :style="{ color: c.color }">{{ c.val }}</span>
            <span class="kpi-unit">{{ c.unit }}</span>
          </div>
          <div class="kpi-label">{{ c.label }}</div>
          <div class="kpi-trend" :class="c.trend > 0 ? 'up' : 'down'">
            <el-icon :size="11"><ArrowUp v-if="c.trend > 0" /><ArrowDown v-else /></el-icon>
            <span>{{ Math.abs(c.trend) }}% 较昨日</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ======== BODY ======== -->
    <div class="cockpit-body">
      <!-- Charts -->
      <div class="charts-area">
        <div class="chart-card chart-main">
          <div class="chart-hd">
            <span class="chart-tt">资源使用趋势</span>
            <el-radio-group v-model="resourceRange" size="small">
              <el-radio-button value="1h">1h</el-radio-button>
              <el-radio-button value="6h">6h</el-radio-button>
              <el-radio-button value="24h">24h</el-radio-button>
            </el-radio-group>
          </div>
          <v-chart class="chart-body" :option="resourceOpt" autoresize />
        </div>
        <div class="chart-card">
          <div class="chart-hd"><span class="chart-tt">任务状态分布</span></div>
          <v-chart class="chart-body" :option="pieOpt" autoresize />
        </div>
        <div class="chart-card">
          <div class="chart-hd"><span class="chart-tt">任务执行趋势</span></div>
          <v-chart class="chart-body" :option="barOpt" autoresize />
        </div>
      </div>

      <!-- Lists -->
      <div class="lists-row">
        <div class="l-card">
          <div class="l-hd">
            <span class="l-tt">服务器健康状态</span>
            <el-tag size="small" class="l-tag">
              {{ servers.filter(s => s.status === 'online').length }}/{{ servers.length }} 在线
            </el-tag>
          </div>
          <div class="l-bd">
            <div v-for="s in servers" :key="s.name" class="l-row">
              <div class="l-left">
                <span class="dot" :class="`dot--${s.status}`" />
                <div>
                  <div class="l-name">{{ s.name }}</div>
                  <div class="l-meta">{{ s.host }}</div>
                </div>
              </div>
              <div class="l-metrics">
                <span class="l-metric"><em>CPU</em>{{ s.cpu }}</span>
                <span class="l-metric"><em>MEM</em>{{ s.mem }}</span>
                <span class="l-metric"><em>GPU</em>{{ s.gpu }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="l-card">
          <div class="l-hd">
            <span class="l-tt">实时告警</span>
            <el-tag v-if="alerts.length" size="small" type="danger" class="l-tag l-tag--dng">
              {{ alerts.length }} 条未处理
            </el-tag>
          </div>
          <div class="l-bd">
            <div v-for="a in alerts" :key="a.id" class="l-row">
              <div class="l-left">
                <span class="a-icon" :class="`a--${a.severity}`">
                  <el-icon :size="13"><WarningFilled /></el-icon>
                </span>
                <div>
                  <div class="l-name">{{ a.message }}</div>
                  <div class="l-meta">{{ a.source }} · {{ a.time }}</div>
                </div>
              </div>
              <el-tag
                :type="a.severity === 'critical' ? 'danger' : a.severity === 'warning' ? 'warning' : 'info'"
                size="small"
                effect="plain"
              >{{
                a.severity === 'critical' ? '严重' : a.severity === 'warning' ? '警告' : '提示'
              }}</el-tag>
            </div>
            <div v-if="!alerts.length" class="l-empty">系统运行正常</div>
          </div>
        </div>

        <div class="l-card">
          <div class="l-hd">
            <span class="l-tt">最近失败任务</span>
          </div>
          <div class="l-bd">
            <div v-for="t in failedTasks" :key="t.id" class="l-row">
              <div class="l-left">
                <span class="tt" :class="`tt--${t.type}`">{{ t.type === 'build' ? 'B' : 'P' }}</span>
                <div>
                  <div class="l-name">{{ t.name }}</div>
                  <div class="l-meta l-meta--err">{{ t.error }}</div>
                </div>
              </div>
              <span class="l-time">{{ t.time }}</span>
            </div>
            <div v-if="!failedTasks.length" class="l-empty">暂无失败任务</div>
          </div>
        </div>

        <div class="l-card">
          <div class="l-hd">
            <span class="l-tt">最近报告</span>
          </div>
          <div class="l-bd">
            <div v-for="r in recentReports" :key="r.id" class="l-row">
              <div class="l-left">
                <span class="r-icon"><el-icon :size="15"><Document /></el-icon></span>
                <div>
                  <div class="l-name">{{ r.name }}</div>
                  <div class="l-meta">{{ r.size }} · {{ r.time }}</div>
                </div>
              </div>
            </div>
            <div v-if="!recentReports.length" class="l-empty">暂无报告</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, PieChart, BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import {
  Monitor, Cpu, DataBoard, WarningFilled, Clock,
  ArrowUp, ArrowDown, Document, Wallet, TrendCharts,
} from '@element-plus/icons-vue'
import { getDashboardData } from '@/api/dashboard'
import type { DashboardData } from '@/api/dashboard'

use([CanvasRenderer, LineChart, PieChart, BarChart, GridComponent, TooltipComponent, LegendComponent])

// ======== Clock ========
const currentTime = ref('')
function tick() {
  const n = new Date()
  currentTime.value = n.toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false,
  })
}
tick()
const timer = setInterval(tick, 1000)
onUnmounted(() => clearInterval(timer))

const dateRange = ref<[Date, Date]>([new Date(Date.now() - 3600000), new Date()])
const resourceRange = ref('1h')

// ======== Dashboard data (from API) ========
const loading = ref(false)
const dashboardData = ref<DashboardData | null>(null)

async function fetchDashboard() {
  loading.value = true
  try {
    const res = await getDashboardData()
    dashboardData.value = res
  } finally {
    loading.value = false
  }
}
onMounted(fetchDashboard)

// Refresh every 30s
const refreshTimer = setInterval(fetchDashboard, 30000)
onUnmounted(() => clearInterval(refreshTimer))

// ======== Computed: KPI cards ========
const kpiCards = computed(() => {
  const d = dashboardData.value?.kpi
  if (!d) {
    return [
      { icon: Monitor,  label: '在线服务器', val: '0', unit: '台',  color: '#6366f1', iconBg: 'rgba(99,102,241,0.08)', trend: 0 },
      { icon: Cpu,      label: '运行中任务', val: '0', unit: '个',  color: '#6366f1', iconBg: 'rgba(99,102,241,0.08)', trend: 0 },
      { icon: Wallet,   label: 'GPU 使用率', val: '0', unit: '%',  color: '#f59e0b', iconBg: 'rgba(245,158,11,0.08)', trend: 0 },
      { icon: TrendCharts, label: 'CPU 负载', val: '0', unit: '%', color: '#10b981', iconBg: 'rgba(16,185,129,0.08)', trend: 0 },
      { icon: DataBoard, label: '存储占用', val: '0', unit: 'GB', color: '#8b5cf6', iconBg: 'rgba(139,92,246,0.08)', trend: 0 },
      { icon: WarningFilled, label: '失败任务', val: '0', unit: '个', color: '#ef4444', iconBg: 'rgba(239,68,68,0.08)', trend: 0 },
    ]
  }
  return [
    { icon: Monitor,  label: '在线服务器', val: String(d.online_servers), unit: '台',  color: '#6366f1', iconBg: 'rgba(99,102,241,0.08)', trend: 0 },
    { icon: Cpu,      label: '运行中任务', val: String(d.total_running), unit: '个',  color: '#6366f1', iconBg: 'rgba(99,102,241,0.08)', trend: 0 },
    { icon: Wallet,   label: 'GPU 使用率', val: String(d.gpu_usage), unit: '%',  color: '#f59e0b', iconBg: 'rgba(245,158,11,0.08)', trend: 0 },
    { icon: TrendCharts, label: 'CPU 负载', val: String(d.cpu_load), unit: '%', color: '#10b981', iconBg: 'rgba(16,185,129,0.08)', trend: 0 },
    { icon: DataBoard, label: '存储占用', val: d.storage_used_gb.toString(), unit: 'GB', color: '#8b5cf6', iconBg: 'rgba(139,92,246,0.08)', trend: 0 },
    { icon: WarningFilled, label: '失败任务', val: String(d.total_failed), unit: '个', color: '#ef4444', iconBg: 'rgba(239,68,68,0.08)', trend: 0 },
  ]
})

// ======== Chart theme colors ========
const lightAxis = '#e2e8f0'
const lightText = '#94a3b8'

// ======== Chart: Resource trend ========
const resourceOpt = computed(() => {
  const d = dashboardData.value?.resource_trend
  return {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255,255,255,0.95)',
      borderColor: '#e2e8f0',
      textStyle: { color: '#1e293b', fontSize: 11 },
    },
    legend: {
      data: ['CPU', '内存', 'GPU'],
      textStyle: { color: lightText, fontSize: 10 },
      bottom: 0, icon: 'roundRect',
    },
    grid: { left: 36, right: 10, top: 6, bottom: 30 },
    xAxis: {
      type: 'category',
      data: d?.labels ?? ['00', '02', '04', '06', '08', '10', '12', '14', '16', '18', '20', '22'],
      axisLine: { lineStyle: { color: lightAxis } },
      axisLabel: { color: lightText, fontSize: 9 },
    },
    yAxis: {
      type: 'value', max: 100,
      axisLabel: { color: lightText, fontSize: 9, formatter: '{value}%' },
      splitLine: { lineStyle: { color: '#f1f5f9' } },
    },
    series: [
      { name: 'CPU', type: 'line', smooth: true, symbol: 'none', lineStyle: { width: 2.5, color: '#6366f1' }, areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(99,102,241,0.12)' }, { offset: 1, color: 'rgba(99,102,241,0)' }] } }, data: d?.cpu ?? [] },
      { name: '内存', type: 'line', smooth: true, symbol: 'none', lineStyle: { width: 2.5, color: '#22d3ee' }, areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(34,211,238,0.1)' }, { offset: 1, color: 'rgba(34,211,238,0)' }] } }, data: d?.mem ?? [] },
      { name: 'GPU', type: 'line', smooth: true, symbol: 'none', lineStyle: { width: 2.5, color: '#f59e0b' }, areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(245,158,11,0.1)' }, { offset: 1, color: 'rgba(245,158,11,0)' }] } }, data: d?.gpu ?? [] },
    ],
  }
})

// ======== Chart: Task status pie ========
const pieOpt = computed(() => ({
  tooltip: {
    trigger: 'item',
    backgroundColor: 'rgba(255,255,255,0.95)',
    borderColor: '#e2e8f0',
    textStyle: { color: '#1e293b', fontSize: 11 },
    formatter: '{b}: {c}',
  },
  series: [{
    type: 'pie', radius: ['42%', '68%'], center: ['50%', '48%'],
    itemStyle: { borderRadius: 3, borderColor: '#fff', borderWidth: 2.5 },
    label: { color: '#64748b', fontSize: 10, formatter: '{b}\n{d}%' },
    labelLine: { lineStyle: { color: '#e2e8f0' } },
    data: dashboardData.value?.pie_data ?? [],
  }],
}))

// ======== Chart: Task execution trend ========
const barOpt = computed(() => ({
  tooltip: {
    trigger: 'axis',
    backgroundColor: 'rgba(255,255,255,0.95)',
    borderColor: '#e2e8f0',
    textStyle: { color: '#1e293b', fontSize: 11 },
  },
  grid: { left: 34, right: 10, top: 6, bottom: 22 },
  xAxis: {
    type: 'category',
    data: dashboardData.value?.bar_trend.labels ?? ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
    axisLine: { lineStyle: { color: lightAxis } },
    axisLabel: { color: lightText, fontSize: 9 },
  },
  yAxis: {
    type: 'value',
    axisLabel: { color: lightText, fontSize: 9 },
    splitLine: { lineStyle: { color: '#f1f5f9' } },
  },
  series: [{
    type: 'bar', barWidth: '36%',
    itemStyle: {
      borderRadius: [4, 4, 0, 0],
      color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#6366f1' }, { offset: 1, color: 'rgba(99,102,241,0.15)' }] },
    },
    data: dashboardData.value?.bar_trend.data ?? [],
  }],
}))

// ======== Server health list (from API) ========
const servers = computed(() => {
  const items = dashboardData.value?.servers ?? []
  return items.map(s => {
    const statusMap: Record<string, string> = { ACTIVE: 'online', DISABLED: 'offline', FAILED: 'warning', UNKNOWN: 'warning' }
    const m = s.metrics
    return {
      name: s.name,
      host: s.host,
      status: statusMap[s.status] ?? 'offline',
      cpu: m.cpu_percent > 0 ? `${Math.round(m.cpu_percent)}%` : '-',
      mem: m.mem_percent > 0 ? `${Math.round(m.mem_percent)}%` : '-',
      gpu: m.gpu_mem_percent > 0 ? `${Math.round(m.gpu_mem_percent)}%` : '-',
    }
  })
})

// ======== Alerts (no source yet; will come from audit/monitoring) ========
const alerts = ref([])

// ======== Failed tasks (from API) ========
const failedTasks = computed(() => {
  return (dashboardData.value?.failed_tasks ?? []).map(t => ({
    id: t.id,
    name: t.definition_name || t.script_name || `任务 #${t.id}`,
    type: t.type as 'build' | 'benchmark',
    error: t.error_message || '未知错误',
    time: t.created_at ? new Date(t.created_at).toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', hour12: false }) : '',
  }))
})

// ======== Recent reports (from API) ========
const recentReports = computed(() => {
  return (dashboardData.value?.recent_reports ?? []).map(r => ({
    id: r.id,
    name: r.name,
    size: r.size,
    time: r.created_at ? new Date(r.created_at).toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', hour12: false }) : '',
  }))
})
</script>

<style scoped>
/* =====================================================
   COCKPIT — Light Tech Big-Data Cockpit
   Enterprise SaaS console style, fits 1920×1080
   ===================================================== */
.cockpit {
  position: relative;
  height: 100%;
  overflow: hidden;
  background: #f0f4f8;
  color: #1e293b;
  display: flex;
  flex-direction: column;
}

/* Subtle tech pattern background */
.cockpit-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background-image:
    radial-gradient(circle at 20% 30%, rgba(99,102,241,0.02) 0%, transparent 60%),
    radial-gradient(circle at 80% 70%, rgba(34,211,238,0.02) 0%, transparent 60%);
}

/* ==================================================
   HEADER (48px)
   ================================================== */
.cockpit-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
  padding: 0 24px;
  height: 48px;
  background: rgba(255,255,255,0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid #e2e8f0;
  position: relative;
  z-index: 2;
}

.h-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.h-brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.h-badge {
  display: inline-flex;
  align-items: center;
  padding: 3px 12px;
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  border-radius: 5px;
  font-size: 14px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 0.03em;
}

.h-title {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
}

.h-time {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: #94a3b8;
  font-variant-numeric: tabular-nums;
}

.h-right {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-shrink: 0;
}

.h-live {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #10b981;
  box-shadow: 0 0 6px rgba(16,185,129,0.4);
  animation: pulse 2s infinite;
}

@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }

.h-live-text {
  font-size: 12px;
  color: #10b981;
  font-weight: 500;
}

.h-divider {
  width: 1px;
  height: 16px;
  background: #e2e8f0;
}

.h-picker :deep(.el-input__wrapper) {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  box-shadow: none;
  border-radius: 6px;
}

.h-picker :deep(.el-input__inner) {
  color: #475569;
  font-size: 12px;
}

/* ==================================================
   KPI ROW (76px)
   ================================================== */
.kpi-row {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 10px;
  padding: 10px 20px;
  flex-shrink: 0;
  position: relative;
  z-index: 1;
}

.kpi-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.02);
  border: 1px solid #e2e8f0;
  transition: all 0.25s;
}

.kpi-card:hover {
  box-shadow: 0 4px 12px rgba(99,102,241,0.08);
  border-color: rgba(99,102,241,0.15);
  transform: translateY(-1px);
}

.kpi-icon-wrap {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.kpi-body {
  min-width: 0;
  flex: 1;
}

.kpi-top {
  display: flex;
  align-items: baseline;
  gap: 3px;
}

.kpi-val {
  font-size: 24px;
  font-weight: 700;
  line-height: 1;
  font-variant-numeric: tabular-nums;
}

.kpi-unit {
  font-size: 12px;
  color: #94a3b8;
}

.kpi-label {
  font-size: 12px;
  color: #64748b;
  margin-top: 1px;
}

.kpi-trend {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 11px;
  margin-top: 2px;
}

.kpi-trend.up { color: #10b981; }
.kpi-trend.down { color: #ef4444; }

/* ==================================================
   BODY (flex: 1)
   ================================================== */
.cockpit-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0 20px 12px;
  gap: 10px;
  min-height: 0;
  position: relative;
  z-index: 1;
}

/* Charts */
.charts-area {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 10px;
  flex: 1;
  min-height: 0;
}

.chart-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.03);
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.chart-hd {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px 0;
  flex-shrink: 0;
}

.chart-tt {
  font-size: 13px;
  font-weight: 600;
  color: #1e293b;
}

.chart-hd :deep(.el-radio-button__inner) {
  background: #f8fafc;
  border-color: #e2e8f0;
  color: #64748b;
  font-size: 10px;
  padding: 2px 10px;
}

.chart-hd :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background: rgba(99,102,241,0.08);
  border-color: rgba(99,102,241,0.2);
  color: #6366f1;
  box-shadow: none;
}

.chart-body {
  flex: 1;
  min-height: 0;
}

/* Lists */
.lists-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  flex-shrink: 0;
  min-height: 0;
}

.l-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.03);
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.l-hd {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px 4px;
  flex-shrink: 0;
}

.l-tt {
  font-size: 12px;
  font-weight: 600;
  color: #1e293b;
}

.l-tag {
  font-size: 10px;
  height: 22px;
  padding: 0 8px;
  border: 1px solid rgba(99,102,241,0.15);
  background: rgba(99,102,241,0.05);
  color: #6366f1;
}

.l-tag--dng {
  border-color: rgba(239,68,68,0.15);
  background: rgba(239,68,68,0.05);
  color: #ef4444;
}

.l-bd {
  flex: 1;
  padding: 2px 4px;
  overflow-y: auto;
}

.l-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 5px 8px;
  border-radius: 6px;
  transition: background 0.15s;
}

.l-row:hover {
  background: #f8fafc;
}

.l-left {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
  flex: 1;
}

.l-name {
  font-size: 12px;
  font-weight: 500;
  color: #1e293b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 150px;
}

.l-meta {
  font-size: 10px;
  color: #94a3b8;
  margin-top: 1px;
}

.l-meta--err {
  color: #ef4444;
}

.l-time {
  font-size: 11px;
  color: #94a3b8;
  flex-shrink: 0;
}

.l-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 18px;
  color: #94a3b8;
  font-size: 12px;
}

/* Server indicators */
.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.dot--online { background: #10b981; }
.dot--warning { background: #f59e0b; }
.dot--offline { background: #ef4444; }

.l-metrics {
  display: flex;
  gap: 10px;
  flex-shrink: 0;
}

.l-metric {
  font-size: 11px;
  font-weight: 600;
  color: #475569;
  font-variant-numeric: tabular-nums;
}

.l-metric em {
  font-style: normal;
  font-weight: 400;
  color: #94a3b8;
  margin-right: 2px;
}

/* Alerts */
.a-icon {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.a--critical { background: rgba(239,68,68,0.08); color: #ef4444; }
.a--warning { background: rgba(245,158,11,0.08); color: #f59e0b; }
.a--info { background: rgba(99,102,241,0.08); color: #6366f1; }

/* Task type badge */
.tt {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 700;
  flex-shrink: 0;
}
.tt--build { background: rgba(245,158,11,0.1); color: #f59e0b; }
.tt--benchmark { background: rgba(239,68,68,0.1); color: #ef4444; }

/* Report icon */
.r-icon {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(99,102,241,0.06);
  color: #6366f1;
  flex-shrink: 0;
}
</style>
