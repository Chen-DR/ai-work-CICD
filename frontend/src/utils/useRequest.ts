import { ref, type Ref } from 'vue'

/**
 * 通用请求 composable — 管理 loading / error / data 三态
 */
export function useRequest<T>() {
  const data = ref<T | null>(null) as Ref<T | null>
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function run(fn: () => Promise<T>): Promise<T | null> {
    loading.value = true
    error.value = null
    try {
      const result = await fn()
      data.value = result
      return result
    } catch (e: any) {
      error.value = e.message || '请求失败'
      return null
    } finally {
      loading.value = false
    }
  }

  return { data, loading, error, run }
}
