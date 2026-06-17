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

function handledError(message: string) {
  const err = new Error(message)
  ;(err as any).handled = true
  return err
}

const fieldLabels: Record<string, string> = {
  project_id: '所属项目',
  name: '名称',
  version: '版本',
  content: 'Definition 内容',
  non_field_errors: '参数',
}

function flattenErrorDetails(details: unknown, prefix = ''): string[] {
  if (!details) return []
  if (typeof details === 'string') return [`${prefix}${details}`]
  if (Array.isArray(details)) {
    return details.flatMap(item => flattenErrorDetails(item, prefix))
  }
  if (typeof details === 'object') {
    return Object.entries(details as Record<string, unknown>).flatMap(([key, value]) => {
      const label = fieldLabels[key] || key
      return flattenErrorDetails(value, `${label}：`)
    })
  }
  return [`${prefix}${String(details)}`]
}

function formatApiError(message: string, details?: unknown) {
  const detailText = flattenErrorDetails(details).join('；')
  return detailText ? `${message}：${detailText}` : message
}

// Response interceptor
instance.interceptors.response.use(
  (response) => {
    const res = response.data
    if (res && typeof res === 'object' && 'code' in res && res.code !== 0) {
      const message = formatApiError(res.message || '请求失败', res.data)
      ElMessage.error(message)
      return Promise.reject(handledError(message))
    }
    return response
  },
  (error) => {
    let message = '无法连接到后端服务，请确认后端已启动'
    if (error.response) {
      const { status, data } = error.response
      switch (status) {
        case 401:
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          router.push('/login')
          message = data?.message || '登录已过期，请重新登录'
          break
        case 403:
          message = data?.message || '无权限访问'
          break
        case 404:
          message = data?.message || '资源不存在'
          break
        case 500:
          message = data?.message || '服务器处理失败'
          break
        default:
          message = data?.message || `请求失败（${status}）`
      }
      if (data && typeof data === 'object' && 'data' in data) {
        message = formatApiError(message, data.data)
      }
    } else if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      message = '请求处理超时，请稍后查看结果或重试'
    }
    ElMessage.error(message)
    return Promise.reject(handledError(message))
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
  patch<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return instance.patch<T>(url, data, config).then(res => unwrap<T>(res))
  },
  delete<T = void>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return instance.delete<T>(url, config).then(res => unwrap<T>(res))
  },
}

export default request
