export interface Project {
  id: number
  name: string
  description: string
  owner_id: number
  created_at: string
  updated_at: string
}

export interface ProjectMember {
  id: number
  project_id: number
  user_id: number
  role: string
  created_at: string
}

export interface ProjectCreateRequest {
  name: string
  description?: string
}
