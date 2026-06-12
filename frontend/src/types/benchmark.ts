export type ScriptType = 'cpu' | 'disk' | 'gpu' | 'mixed' | 'custom'

export interface BenchmarkScript {
  id: number
  project_id: number
  name: string
  script_type: ScriptType
  version: string
  file_name: string
  storage_path: string
  description: string
  created_by_id: number
  created_at: string
  updated_at: string
}

export type BenchmarkJobStatus =
  | 'PENDING'
  | 'VALIDATING'
  | 'UPLOADING'
  | 'RUNNING'
  | 'COLLECTING'
  | 'SUCCESS'
  | 'FAILED'
  | 'CANCELLED'
  | 'TIMEOUT'

export interface BenchmarkJob {
  id: number
  project_id: number
  script_id: number
  server_id: number
  workdir: string
  params: Record<string, unknown>
  status: BenchmarkJobStatus
  celery_task_id: string
  log_path: string
  report_path: string
  remote_report_path: string
  started_at: string | null
  finished_at: string | null
  error_message: string
  created_by_id: number
  created_at: string
  updated_at: string
}

export interface CreateBenchmarkJobRequest {
  project_id: number
  script_id: number
  server_id: number
  workdir: string
  params: Record<string, unknown>
}
