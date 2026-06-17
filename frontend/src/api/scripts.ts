import request from './request'
import type { ExecuteScriptRequest, ManagedScript, ScriptExecutionTask, ScriptParamPreset } from '@/types/scripts'

export function getManagedScripts(projectId?: number) {
  const params = projectId ? { project_id: projectId } : {}
  return request.get<ManagedScript[]>('/scripts/', { params })
}

export function getManagedScript(id: number) {
  return request.get<ManagedScript>(`/scripts/${id}/`)
}

export function uploadManagedScript(projectId: number, name: string, file: File, description?: string) {
  const formData = new FormData()
  formData.append('project_id', String(projectId))
  formData.append('name', name)
  formData.append('file', file)
  if (description) formData.append('description', description)
  return request.post<ManagedScript>('/scripts/upload/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function updateManagedScript(id: number, data: Partial<Pick<ManagedScript, 'name' | 'description' | 'content'>>) {
  return request.put<ManagedScript>(`/scripts/${id}/`, data)
}

export function deleteManagedScript(id: number) {
  return request.delete(`/scripts/${id}/`)
}

export function executeManagedScript(id: number, data: ExecuteScriptRequest) {
  return request.post<ScriptExecutionTask>(`/scripts/${id}/execute/`, data)
}

export function getScriptPresets(scriptId: number) {
  return request.get<ScriptParamPreset[]>(`/scripts/${scriptId}/presets/`)
}

export function createScriptPreset(scriptId: number, data: { name: string; args: string }) {
  return request.post<ScriptParamPreset>(`/scripts/${scriptId}/presets/`, data)
}

export function updateScriptPreset(scriptId: number, presetId: number, data: Partial<Pick<ScriptParamPreset, 'name' | 'args'>>) {
  return request.put<ScriptParamPreset>(`/scripts/${scriptId}/presets/${presetId}/`, data)
}

export function deleteScriptPreset(scriptId: number, presetId: number) {
  return request.delete(`/scripts/${scriptId}/presets/${presetId}/`)
}

export function useScriptPreset(scriptId: number, presetId: number) {
  return request.post<ScriptParamPreset>(`/scripts/${scriptId}/presets/${presetId}/use/`)
}

export function getScriptRecentCwds(scriptId: number) {
  return request.get<string[]>(`/scripts/${scriptId}/recent_cwds/`)
}

export function terminateScriptTask(taskId: string) {
  return request.delete(`/scripts/tasks/${taskId}/`)
}

export function scriptTaskLogStreamUrl(taskId: string) {
  const base = import.meta.env.VITE_API_BASE_URL || '/api/v1'
  return `${base}/scripts/tasks/${taskId}/log/stream/`
}
