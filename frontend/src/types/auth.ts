export interface User {
  id: string
  email: string
  first_name: string
  last_name: string
  company_name?: string
  phone?: string
  is_active: boolean
  is_verified: boolean
  roles: string[]
  bio?: string
  avatar_url?: string
  created_at: string
  updated_at?: string
  last_login?: string
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  email: string
  password: string
  first_name: string
  last_name: string
  company_name?: string
  phone?: string
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface TokenData {
  email: string
  type: string
  exp: number
}
