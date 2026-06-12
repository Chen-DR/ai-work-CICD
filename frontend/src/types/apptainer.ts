export interface ApptainerDefinition {
  id: number
  project_id: number
  conversation_id: number
  name: string
  version: string
  content: string
  storage_path: string
  created_by_id: number
  created_at: string
  updated_at: string
}

export type BuildJobStatus =
  | 'PENDING'
  | 'VALIDATING'
  | 'UPLOADING'
  | 'RUNNING'
  | 'COLLECTING'
  | 'SUCCESS'
  | 'FAILED'
  | 'CANCELLED'
  | 'TIMEOUT'

export interface ApptainerBuildJob {
  id: number
  project_id: number
  definition_id: number
  server_id: number
  workdir: string
  output_name: string
  status: BuildJobStatus
  celery_task_id: string
  log_path: string
  remote_output_path: string
  started_at: string | null
  finished_at: string | null
  error_message: string
  created_by_id: number
  created_at: string
  updated_at: string
}

export interface CreateBuildJobRequest {
  project_id: number
  definition_id: number
  server_id: number
  workdir: string
  output_name: string
}

export interface GenerateDefinitionRequest {
  project_id: number
  conversation_id: number
  requirement: string
  use_knowledge: boolean
}
