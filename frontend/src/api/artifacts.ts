import request from './request'
import type { Artifact } from '@/types/artifact'

export function getArtifacts(params?: {
  project_id?: number
  job_type?: string
  artifact_type?: string
}) {
  return request.get<Artifact[]>('/artifacts/', { params })
}

export function getArtifact(id: number) {
  return request.get<Artifact>(`/artifacts/${id}/`)
}

export function downloadArtifact(id: number) {
  return request.get<string>(`/artifacts/${id}/download/`, {
    responseType: 'blob',
  })
}

export function deleteArtifact(id: number) {
  return request.delete(`/artifacts/${id}/`)
}
