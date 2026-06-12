import request from './request'
import type {
  BenchmarkScript,
  BenchmarkJob,
  CreateBenchmarkJobRequest,
} from '@/types/benchmark'

// Scripts
export function getScripts(projectId?: number) {
  const params = projectId ? { project_id: projectId } : {}
  return request.get<BenchmarkScript[]>('/benchmark/scripts/', { params })
}

export function getScript(id: number) {
  return request.get<BenchmarkScript>(`/benchmark/scripts/${id}/`)
}

export function uploadScript(projectId: number, name: string, scriptType: string, file: File, description?: string) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('project_id', String(projectId))
  formData.append('name', name)
  formData.append('script_type', scriptType)
  if (description) formData.append('description', description)
  return request.post<BenchmarkScript>('/benchmark/scripts/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function deleteScript(id: number) {
  return request.delete(`/benchmark/scripts/${id}/`)
}

// Jobs
export function getBenchmarkJobs(projectId?: number) {
  const params = projectId ? { project_id: projectId } : {}
  return request.get<BenchmarkJob[]>('/benchmark/jobs/', { params })
}

export function getBenchmarkJob(id: number) {
  return request.get<BenchmarkJob>(`/benchmark/jobs/${id}/`)
}

export function createBenchmarkJob(data: CreateBenchmarkJobRequest) {
  return request.post<BenchmarkJob>('/benchmark/jobs/', data)
}

export function cancelBenchmarkJob(id: number) {
  return request.post(`/benchmark/jobs/${id}/cancel/`)
}

export function getBenchmarkJobLogs(id: number, tail = 200) {
  return request.get<string>(`/benchmark/jobs/${id}/logs/`, {
    params: { tail },
  })
}
