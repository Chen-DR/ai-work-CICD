export type ArtifactType =
  | 'knowledge_file'
  | 'apptainer_def'
  | 'build_log'
  | 'sif_path_record'
  | 'benchmark_script'
  | 'benchmark_log'
  | 'benchmark_report'

export interface Artifact {
  id: number
  project_id: number
  job_type: string
  job_id: number
  artifact_type: ArtifactType
  file_name: string
  storage_path: string
  file_size: number
  checksum: string
  created_at: string
}
