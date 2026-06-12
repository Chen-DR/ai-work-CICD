import request from './request'
import type { Project, ProjectCreateRequest } from '@/types/project'

export function getProjects() {
  return request.get<Project[]>('/projects/')
}

export function getProject(id: number) {
  return request.get<Project>(`/projects/${id}/`)
}

export function createProject(data: ProjectCreateRequest) {
  return request.post<Project>('/projects/', data)
}

export function updateProject(id: number, data: Partial<Project>) {
  return request.put<Project>(`/projects/${id}/`, data)
}

export function deleteProject(id: number) {
  return request.delete(`/projects/${id}/`)
}
