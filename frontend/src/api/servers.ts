import request from './request'
import type { Server, ServerCreateRequest, ServerTestResult, ServerDetectResult, ServerAllowedDir } from '@/types/server'

export function getServers(projectId?: number) {
  const params = projectId ? { project_id: projectId } : {}
  return request.get<Server[]>('/servers/', { params })
}

export function getServer(id: number) {
  return request.get<Server>(`/servers/${id}/`)
}

export function createServer(data: ServerCreateRequest) {
  return request.post<Server>('/servers/', data)
}

export function updateServer(id: number, data: Partial<Server>) {
  return request.patch<Server>(`/servers/${id}/`, data)
}

export function deleteServer(id: number) {
  return request.delete(`/servers/${id}/`)
}

export function testServerConnection(id: number) {
  return request.post<ServerTestResult>(`/servers/${id}/test/`)
}

export function detectServerEnvironment(id: number) {
  return request.post<ServerDetectResult>(`/servers/${id}/detect/`)
}

export function getServerAllowedDirs(id: number) {
  return request.get<ServerAllowedDir[]>(`/servers/${id}/allowed_dirs/`)
}

export function createServerAllowedDir(id: number, data: { path: string; purpose: string }) {
  return request.post<ServerAllowedDir>(`/servers/${id}/allowed_dirs/`, data)
}

export function deleteServerAllowedDir(serverId: number, dirId: number) {
  return request.delete(`/servers/${serverId}/allowed_dirs/${dirId}/`)
}
