<template>
  <div class="page-container">
    <div class="page-header">
      <h2>压测任务 #{{ route.params.id }}</h2>
      <el-button @click="$router.push('/benchmark/jobs')">返回列表</el-button>
    </div>

    <el-card v-loading="loading" class="mb-16">
      <el-descriptions title="任务信息" :column="2" border>
        <el-descriptions-item label="状态">
          <JobStatusTag v-if="job" :status="job.status" />
        </el-descriptions-item>
        <el-descriptions-item label="脚本 ID">{{ job?.script_id || '-' }}</el-descriptions-item>
        <el-descriptions-item label="服务器 ID">{{ job?.server_id || '-' }}</el-descriptions-item>
        <el-descriptions-item label="工作目录">{{ job?.workdir || '-' }}</el-descriptions-item>
        <el-descriptions-item label="参数">
          <code>{{ JSON.stringify(job?.params) }}</code>
        </el-descriptions-item>
        <el-descriptions-item label="报告路径">{{ job?.report_path || '-' }}</el-descriptions-item>
        <el-descriptions-item label="开始时间">{{ job?.started_at || '-' }}</el-descriptions-item>
        <el-descriptions-item label="完成时间">{{ job?.finished_at || '-' }}</el-descriptions-item>
        <el-descriptions-item v-if="job?.error_message" label="错误信息" :span="2">
          <span class="text-danger">{{ job.error_message }}</span>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-row :gutter="16">
      <el-col :span="job?.report_path ? 12 : 24">
        <el-card class="mb-16">
          <template #header>
            <div class="flex-between">
              <span>运行日志</span>
              <el-button size="small" @click="fetchLogs" :loading="logLoading">
                <el-icon><Refresh /></el-icon> 刷新
              </el-button>
            </div>
          </template>
          <LogViewer :logs="logs" @refresh="fetchLogs" />
        </el-card>
      </el-col>
      <el-col v-if="job?.report_path" :span="12">
        <el-card class="mb-16">
          <template #header>
            <div class="flex-between">
              <span>压测报告</span>
              <el-button size="small" type="primary" @click="downloadReport">
                下载报告
              </el-button>
            </div>
          </template>
          <ReportViewer :report-url="reportUrl" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import JobStatusTag from '@/components/JobStatusTag/index.vue'
import LogViewer from '@/components/LogViewer/index.vue'
import ReportViewer from '@/components/ReportViewer/index.vue'
import { getBenchmarkJob, getBenchmarkJobLogs } from '@/api/benchmark'
import { usePolling } from '@/utils/usePolling'
import type { BenchmarkJob } from '@/types/benchmark'

const route = useRoute()
const job = ref<BenchmarkJob | null>(null)
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

const reportUrl = computed(() => {
  if (!job.value?.report_path) return null
  return null // Needs artifact ID to construct URL
})

async function fetchJob() {
  loading.value = true
  try {
    job.value = await getBenchmarkJob(jobId)
  } finally {
    loading.value = false
  }
}

async function fetchLogs() {
  logLoading.value = true
  try {
    logs.value = await getBenchmarkJobLogs(jobId)
  } finally {
    logLoading.value = false
  }
}

function downloadReport() {
  ElMessage.info('报告下载需要关联 Artifact ID')
}

onMounted(() => {
  fetchJob()
  fetchLogs()
  startPolling()
})
</script>
