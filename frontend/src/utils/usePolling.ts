import { ref, onUnmounted, type Ref } from 'vue'

/**
 * 通用轮询 composable
 * @param fetcher  轮询执行的异步函数
 * @param intervalMs 轮询间隔（毫秒）
 * @param stopWhen  可选：当返回 true 时停止轮询
 */
export function usePolling(
  fetcher: () => Promise<void>,
  intervalMs = 3000,
  stopWhen?: () => boolean
) {
  const isPolling = ref(false)
  let timer: ReturnType<typeof setInterval> | null = null

  function start() {
    if (timer) return
    isPolling.value = true
    timer = setInterval(async () => {
      try {
        await fetcher()
        if (stopWhen?.()) {
          stop()
        }
      } catch {
        // 轮询失败不中断，下次继续
      }
    }, intervalMs)
  }

  function stop() {
    if (timer) {
      clearInterval(timer)
      timer = null
    }
    isPolling.value = false
  }

  onUnmounted(() => stop())

  return { start, stop, isPolling }
}
