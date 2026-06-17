export type ScriptLanguage = 'shell' | 'python'

export interface ManagedScript {
  id: number
  project: number
  name: string
  file_name: string
  storage_path: string
  description: string
  language: ScriptLanguage
  content?: string | null
  created_by: number | null
  created_at: string
  updated_at: string
}

export type ScriptTaskStatus = 'PENDING' | 'RUNNING' | 'SUCCESS' | 'FAILED' | 'CANCELLED' | 'TIMEOUT'

export interface ScriptExecutionTask {
  task_id: string
  project: number
  script: number
  server: number | null
  cwd: string
  args: string
  run_as: string
  timeout: number
  status: ScriptTaskStatus
  celery_task_id: string
  log_path: string
  exit_code: number | null
  process_id: number | null
  error_message: string
  created_by: number | null
  started_at: string | null
  finished_at: string | null
  created_at: string
  updated_at: string
}

export interface ExecuteScriptRequest {
  server_id: number
  cwd: string
  args?: string
  timeout?: number
  run_as?: string
}

export interface ScriptParamPreset {
  id: number
  script_id: number
  name: string
  args: string
  last_used_at: string | null
  created_by: number | null
  created_at: string
  updated_at: string
}

export interface ScriptLogEvent {
  type: 'stdout' | 'stderr' | 'exit' | 'meta'
  line?: string
  command?: string[]
  cwd?: string
  run_as?: string
  code?: number
  ts: string
}
