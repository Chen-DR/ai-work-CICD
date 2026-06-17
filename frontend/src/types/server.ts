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
  allow_script_root: boolean
  metrics?: {
    cpu_percent: number
    mem_percent: number
    mem_used_gb: number
    gpu_percent: number
    gpu_mem_percent: number
    disk_percent: number
    disk_used_gb: number
    collected_at: string
  } | null
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
