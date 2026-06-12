import axios from 'axios'
import type { AxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'

const instance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Response interceptor
instance.interceptors.response.use(
  (response) => {
    const res = response.data
    if (res && typeof res === 'object' && 'code' in res && res.code !== 0) {
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message))
    }
    return response
  },
  (error) => {
    if (error.response) {
      const { status, data } = error.response
      switch (status) {
        case 401:
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          router.push('/login')
          ElMessage.error('登录已过期，请重新登录')
          break
        case 403:
          ElMessage.error(data?.message || '无权限访问')
          break
        case 404:
          ElMessage.error(data?.message || '资源不存在')
          break
        case 500:
          ElMessage.error(data?.message || '服务器错误')
          break
        default:
          ElMessage.error(data?.message || `请求失败 (${status})`)
      }
    } else {
      ElMessage.error('无法连接到后端服务，请确认后端已启动')
    }
    return Promise.reject(error)
  }
)

// Request interceptor - attach token
instance.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

/** Unwrap API response to handle both custom and DRF formats. */
function unwrap<T>(res: any): T {
  const body = res.data as any
  if (!body || typeof body !== 'object') return body

  // Custom format: {code: 0, message, data}
  if ('code' in body) return body.data

  // DRF paginated format: {count, results}
  if ('count' in body && 'results' in body) return body.results

  // DRF detail or list: plain object or array
  return body
}

// Typed wrapper that properly unwraps AxiosResponse
const request = {
  get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return instance.get<T>(url, config).then(res => unwrap<T>(res))
  },
  post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return instance.post<T>(url, data, config).then(res => unwrap<T>(res))
  },
  put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return instance.put<T>(url, data, config).then(res => unwrap<T>(res))
  },
  delete<T = void>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return instance.delete<T>(url, config).then(res => unwrap<T>(res))
  },
}

export default request
