export interface User {
  id: number
  username: string
  display_name: string
  role: 'admin' | 'developer' | 'operator' | 'viewer'
  created_at: string
  updated_at: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  token: string
  user: User
}
