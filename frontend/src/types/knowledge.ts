export type KnowledgeDocumentStatus = 'UPLOADED' | 'PARSING' | 'READY' | 'FAILED'

export interface KnowledgeDocument {
  id: number
  project_id: number
  title: string
  file_name: string
  file_type: string
  storage_path: string
  status: KnowledgeDocumentStatus
  error_message: string
  created_by_id: number
  created_at: string
  updated_at: string
}

export interface KnowledgeChunk {
  id: number
  document_id: number
  project_id: number
  chunk_index: number
  content: string
  metadata: Record<string, unknown>
  created_at: string
}

export interface KnowledgeSearchRequest {
  project_id: number
  query: string
  top_k: number
}

export interface KnowledgeSearchResult {
  chunks: KnowledgeChunk[]
}
