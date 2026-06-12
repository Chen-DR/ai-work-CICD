import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useJobStore = defineStore('job', () => {
  const pollingJobs = ref<Set<number>>(new Set())

  function startPolling(jobId: number) {
    pollingJobs.value.add(jobId)
  }

  function stopPolling(jobId: number) {
    pollingJobs.value.delete(jobId)
  }

  function clearPolling() {
    pollingJobs.value.clear()
  }

  return {
    pollingJobs,
    startPolling,
    stopPolling,
    clearPolling,
  }
})
