import { apiClient } from './apiClient'
import { LoginCredentials, RegisterData, AuthResponse, User } from '../types/auth'

class AuthService {
  private baseUrl = '/api/v1/auth'

  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const formData = new FormData()
    formData.append('username', credentials.email)
    formData.append('password', credentials.password)

    const response = await apiClient.post(`${this.baseUrl}/login`, formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })

    return response.data
  }

  async register(data: RegisterData): Promise<User> {
    const response = await apiClient.post(`${this.baseUrl}/register`, data)
    return response.data
  }

  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get(`${this.baseUrl}/me`)
    return response.data
  }

  async refreshToken(refreshToken: string): Promise<AuthResponse> {
    const response = await apiClient.post(`${this.baseUrl}/refresh`, {
      refresh_token: refreshToken,
    })
    return response.data
  }

  async logout(): Promise<void> {
    await apiClient.post(`${this.baseUrl}/logout`)
  }

  getToken(): string | null {
    return localStorage.getItem('access_token')
  }

  getRefreshToken(): string | null {
    return localStorage.getItem('refresh_token')
  }

  setTokens(accessToken: string, refreshToken: string): void {
    localStorage.setItem('access_token', accessToken)
    localStorage.setItem('refresh_token', refreshToken)
  }

  clearTokens(): void {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  isTokenExpired(token: string): boolean {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      return payload.exp * 1000 < Date.now()
    } catch {
      return true
    }
  }
}

export const authService = new AuthService()
