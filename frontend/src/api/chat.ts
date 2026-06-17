import request from './request'
import type { Conversation, Message, CompleteRequest, CompleteResponse } from '@/types/chat'

export function getConversations(projectId?: number) {
  const params = projectId ? { project_id: projectId } : {}
  return request.get<Conversation[]>('/chat/conversations/', { params })
}

export function createConversation(data: { project_id: number; title?: string }) {
  return request.post<Conversation>('/chat/conversations/', data)
}

export function getConversation(id: number) {
  return request.get<Conversation>(`/chat/conversations/${id}/`)
}

export function deleteConversation(id: number) {
  return request.delete(`/chat/conversations/${id}/`)
}

export function getMessages(conversationId: number) {
  return request.get<Message[]>(`/chat/conversations/${conversationId}/messages/`)
}

export function sendMessage(conversationId: number, content: string) {
  return request.post<Message>(`/chat/conversations/${conversationId}/messages/`, { content })
}

export function complete(data: CompleteRequest) {
  return request.post<CompleteResponse>('/chat/complete/', data, { timeout: 180000 })
}
