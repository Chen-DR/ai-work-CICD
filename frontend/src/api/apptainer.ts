import request from './request'
import type {
  ApptainerDefinition,
  ApptainerBuildJob,
  CreateBuildJobRequest,
  GenerateDefinitionRequest,
} from '@/types/apptainer'

// Definitions
export function getDefinitions(projectId?: number) {
  const params = projectId ? { project_id: projectId } : {}
  return request.get<ApptainerDefinition[]>('/apptainer/definitions/', { params })
}

export function getDefinition(id: number) {
  return request.get<ApptainerDefinition>(`/apptainer/definitions/${id}/`)
}

export function createDefinition(data: Partial<ApptainerDefinition>) {
  return request.post<ApptainerDefinition>('/apptainer/definitions/', data)
}

export function updateDefinition(id: number, data: Partial<ApptainerDefinition>) {
  return request.put<ApptainerDefinition>(`/apptainer/definitions/${id}/`, data)
}

export function deleteDefinition(id: number) {
  return request.delete(`/apptainer/definitions/${id}/`)
}

export function generateDefinition(data: GenerateDefinitionRequest) {
  return request.post<ApptainerDefinition>('/apptainer/generate/', data)
}

// Build Jobs
export function getBuildJobs(projectId?: number) {
  const params = projectId ? { project_id: projectId } : {}
  return request.get<ApptainerBuildJob[]>('/apptainer/build-jobs/', { params })
}

export function getBuildJob(id: number) {
  return request.get<ApptainerBuildJob>(`/apptainer/build-jobs/${id}/`)
}

export function createBuildJob(data: CreateBuildJobRequest) {
  return request.post<ApptainerBuildJob>('/apptainer/build-jobs/', data)
}

export function cancelBuildJob(id: number) {
  return request.post(`/apptainer/build-jobs/${id}/cancel/`)
}

export function getBuildJobLogs(id: number, tail = 200) {
  return request.get<string>(`/apptainer/build-jobs/${id}/logs/`, {
    params: { tail },
  })
}
