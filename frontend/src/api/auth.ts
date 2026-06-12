import request from './request'
import type { LoginRequest, User } from '@/types/user'

export function login(data: LoginRequest) {
  return request.post<{ token: string; user: User }>('/auth/login/', data)
}

export function logout() {
  return request.post('/auth/logout/')
}

export function getCurrentUser() {
  return request.get<User>('/auth/me/')
}
