export type ServerStatus = 'ACTIVE' | 'DISABLED' | 'UNKNOWN' | 'FAILED'
export type AuthType = 'password' | 'ssh_key'

export interface Server {
  id: number
  project_id: number
  name: string
  host: string
  port: number
  username: string
  auth_type: AuthType
  status: ServerStatus
  created_at: string
  updated_at: string
}

export interface ServerCreateRequest {
  project_id: number
  name: string
  host: string
  port: number
  username: string
  auth_type: AuthType
  password?: string
  ssh_key?: string
}

export interface ServerAllowedDir {
  id: number
  server_id: number
  path: string
  purpose: string
  created_at: string
}

export interface ServerTestResult {
  success: boolean
  message: string
}

export interface ServerDetectResult {
  hostname: string
  os: string
  apptainer_version: string
  python_version: string
  cuda_version: string
  disk_info: string
}
