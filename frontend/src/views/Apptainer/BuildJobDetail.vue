<template>
  <div class="page-container">
    <div class="page-header">
      <h2>构建任务 #{{ route.params.id }}</h2>
      <el-button @click="$router.push('/apptainer/build-jobs')">返回列表</el-button>
    </div>

    <el-card v-loading="loading" class="mb-16">
      <el-descriptions title="任务信息" :column="2" border>
        <el-descriptions-item label="状态">
          <JobStatusTag v-if="job" :status="job.status" />
        </el-descriptions-item>
        <el-descriptions-item label="输出文件">{{ job?.output_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="工作目录">{{ job?.workdir || '-' }}</el-descriptions-item>
        <el-descriptions-item label="服务器 ID">{{ job?.server_id || '-' }}</el-descriptions-item>
        <el-descriptions-item label="开始时间">{{ job?.started_at || '-' }}</el-descriptions-item>
        <el-descriptions-item label="完成时间">{{ job?.finished_at || '-' }}</el-descriptions-item>
        <el-descriptions-item v-if="job?.error_message" label="错误信息" :span="2">
          <span class="text-danger">{{ job.error_message }}</span>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card class="mb-16">
      <template #header>
        <div class="flex-between">
          <span>构建日志</span>
          <el-button size="small" @click="fetchLogs" :loading="logLoading">
            <el-icon><Refresh /></el-icon> 刷新
          </el-button>
        </div>
      </template>
      <LogViewer :logs="logs" @refresh="fetchLogs" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Refresh } from '@element-plus/icons-vue'
import JobStatusTag from '@/components/JobStatusTag/index.vue'
import LogViewer from '@/components/LogViewer/index.vue'
import { getBuildJob, getBuildJobLogs } from '@/api/apptainer'
import { usePolling } from '@/utils/usePolling'
import type { ApptainerBuildJob } from '@/types/apptainer'

const route = useRoute()
const job = ref<ApptainerBuildJob | null>(null)
const loading = ref(false)
const logs = ref<string | null>(null)
const logLoading = ref(false)
const jobId = Number(route.params.id)

function isTerminal() {
  return job.value ? ['SUCCESS', 'FAILED', 'CANCELLED', 'TIMEOUT'].includes(job.value.status) : false
}

const { start: startPolling } = usePolling(async () => {
  await fetchJob()
  await fetchLogs()
}, 3000, isTerminal)

async function fetchJob() {
  loading.value = true
  try {
    job.value = await getBuildJob(jobId)
  } finally {
    loading.value = false
  }
}

async function fetchLogs() {
  logLoading.value = true
  try {
    logs.value = await getBuildJobLogs(jobId)
  } finally {
    logLoading.value = false
  }
}

onMounted(() => {
  fetchJob()
  fetchLogs()
  startPolling()
})
</script>
