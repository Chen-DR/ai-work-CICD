export interface Conversation {
  id: number
  project_id: number
  title: string
  model_name: string
  created_at: string
  updated_at: string
}

export interface Message {
  id: number
  conversation_id: number
  role: 'user' | 'assistant' | 'system' | 'tool'
  content: string
  created_at: string
}

export interface KnowledgeReference {
  document_id: number
  document_title: string
  chunk_id: number
  content: string
}

export interface CompleteResponse {
  answer: string
  references: KnowledgeReference[]
}

export interface CompleteRequest {
  project_id: number
  conversation_id: number
  message: string
  use_knowledge: boolean
}
