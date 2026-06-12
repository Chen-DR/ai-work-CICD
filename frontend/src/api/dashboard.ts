import request from './request'

export interface KpiData {
  total_servers: number
  online_servers: number
  total_running: number
  gpu_usage: number
  cpu_load: number
  storage_used_gb: number
  total_failed: number
}

export interface PieDataItem {
  name: string
  value: number
}

export interface ServerMetrics {
  cpu_percent: number
  mem_percent: number
  mem_used_gb: number
  gpu_percent: number
  gpu_mem_percent: number
  disk_percent: number
  disk_used_gb: number
  collected_at: string
}

export interface ServerHealthItem {
  id: number
  name: string
  host: string
  port: number
  username: string
  auth_type: string
  status: string
  status_display: string
  metrics: ServerMetrics
}

export interface FailedTaskItem {
  id: number
  definition_name?: string
  script_name?: string
  status: string
  status_display: string
  error_message: string
  created_at: string
  type: 'build' | 'benchmark'
}

export interface ReportItem {
  id: number
  file_name: string
  file_size: number
  created_at: string
  name: string
  size: string
}

export interface DashboardData {
  kpi: KpiData
  pie_data: PieDataItem[]
  servers: ServerHealthItem[]
  failed_tasks: FailedTaskItem[]
  recent_reports: ReportItem[]
  resource_trend: {
    labels: string[]
    cpu: number[]
    mem: number[]
    gpu: number[]
  }
  bar_trend: {
    labels: string[]
    data: number[]
  }
  last_updated: string
}

export function getDashboardData() {
  return request.get<DashboardData>('/dashboard/')
}
