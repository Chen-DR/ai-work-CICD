<template>
  <div class="page-container">
    <div class="page-header">
      <h2>压测任务</h2>
    </div>

    <el-table :data="jobs" v-loading="loading" stripe empty-text="暂无压测任务">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column label="状态" width="120">
        <template #default="{ row }">
          <JobStatusTag :status="row.status" />
        </template>
      </el-table-column>
      <el-table-column prop="workdir" label="工作目录" min-width="200" show-overflow-tooltip />
      <el-table-column label="参数" min-width="200" show-overflow-tooltip>
        <template #default="{ row }">
          <code>{{ JSON.stringify(row.params) }}</code>
        </template>
      </el-table-column>
      <el-table-column prop="error_message" label="错误" min-width="200" show-overflow-tooltip>
        <template #default="{ row }">
          <span v-if="row.error_message" class="text-danger">{{ row.error_message }}</span>
          <span v-else class="text-secondary">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="started_at" label="开始时间" width="170" />
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="$router.push(`/benchmark/jobs/${row.id}`)">
            详情
          </el-button>
          <el-button
            v-if="row.status === 'PENDING' || row.status === 'RUNNING'"
            size="small"
            type="danger"
            @click="handleCancel(row)"
          >
            取消
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import JobStatusTag from '@/components/JobStatusTag/index.vue'
import { getBenchmarkJobs, cancelBenchmarkJob } from '@/api/benchmark'
import { usePolling } from '@/utils/usePolling'
import type { BenchmarkJob } from '@/types/benchmark'

const jobs = ref<BenchmarkJob[]>([])
const loading = ref(false)

const { start: startPolling } = usePolling(fetchJobs, 5000)

async function fetchJobs() {
  loading.value = true
  try {
    jobs.value = await getBenchmarkJobs()
  } finally {
    loading.value = false
  }
}

async function handleCancel(job: BenchmarkJob) {
  try {
    await cancelBenchmarkJob(job.id)
    ElMessage.success('已取消')
    await fetchJobs()
  } catch {
    ElMessage.error('取消失败')
  }
}

onMounted(() => {
  fetchJobs()
  startPolling()
})
</script>
