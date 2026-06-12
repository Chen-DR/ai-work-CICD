import request from './request'
import type { KnowledgeDocument, KnowledgeSearchRequest, KnowledgeSearchResult } from '@/types/knowledge'

export function getDocuments(projectId?: number) {
  const params = projectId ? { project_id: projectId } : {}
  return request.get<KnowledgeDocument[]>('/knowledge/documents/', { params })
}

export function getDocument(id: number) {
  return request.get<KnowledgeDocument>(`/knowledge/documents/${id}/`)
}

export function uploadDocument(projectId: number, file: File) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('project_id', String(projectId))
  return request.post<KnowledgeDocument>('/knowledge/documents/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function deleteDocument(id: number) {
  return request.delete(`/knowledge/documents/${id}/`)
}

export function parseDocument(id: number) {
  return request.post(`/knowledge/documents/${id}/parse/`)
}

export function searchKnowledge(data: KnowledgeSearchRequest) {
  return request.post<KnowledgeSearchResult>('/knowledge/search/', data)
}
