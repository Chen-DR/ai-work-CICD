import request from './request'

export interface AuditLogEntry {
  id: number
  project_id: number | null
  user_id: number
  action: string
  resource_type: string
  resource_id: string
  ip_address: string
  detail: string
  created_at: string
}

export interface AuditLogQuery {
  project_id?: number
  user_id?: number
  action?: string
  page?: number
  page_size?: number
}

export function getAuditLogs(params: AuditLogQuery = {}) {
  return request.get<AuditLogEntry[]>('/audit/logs/', { params })
}
