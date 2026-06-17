<template>
  <div class="page-container">
    <div class="page-header">
      <h2>构建任务</h2>
    </div>

    <el-table :data="jobs" v-loading="loading" stripe empty-text="暂无构建任务">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column label="状态" width="120">
        <template #default="{ row }">
          <JobStatusTag :status="row.status" />
        </template>
      </el-table-column>
      <el-table-column prop="output_name" label="输出文件" min-width="150" />
      <el-table-column prop="workdir" label="工作目录" min-width="200" show-overflow-tooltip />
      <el-table-column prop="remote_output_path" label="远程路径" min-width="200" show-overflow-tooltip />
      <el-table-column prop="error_message" label="错误信息" min-width="200" show-overflow-tooltip>
        <template #default="{ row }">
          <span v-if="row.error_message" class="text-danger">{{ row.error_message }}</span>
          <span v-else class="text-secondary">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="started_at" label="开始时间" width="170" />
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="$router.push(`/apptainer/build-jobs/${row.id}`)">
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
          <el-button
            v-if="canDelete(row)"
            size="small"
            type="danger"
            @click="handleDelete(row)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import JobStatusTag from '@/components/JobStatusTag/index.vue'
import { getBuildJobs, cancelBuildJob, deleteBuildJob } from '@/api/apptainer'
import { usePolling } from '@/utils/usePolling'
import type { ApptainerBuildJob, BuildJobStatus } from '@/types/apptainer'

const jobs = ref<ApptainerBuildJob[]>([])
const loading = ref(false)
const deletableStatuses: BuildJobStatus[] = ['SUCCESS', 'FAILED', 'CANCELLED', 'TIMEOUT']

const { start: startPolling } = usePolling(fetchJobs, 5000)

async function fetchJobs() {
  loading.value = true
  try {
    jobs.value = await getBuildJobs()
  } finally {
    loading.value = false
  }
}

function canDelete(job: ApptainerBuildJob) {
  return deletableStatuses.includes(job.status)
}

async function handleCancel(job: ApptainerBuildJob) {
  try {
    await cancelBuildJob(job.id)
    ElMessage.success('已取消')
    await fetchJobs()
  } catch {
    ElMessage.error('取消失败')
  }
}

async function handleDelete(job: ApptainerBuildJob) {
  try {
    await ElMessageBox.confirm(`确定删除构建任务 #${job.id} 吗？`, '确认', { type: 'warning' })
    await deleteBuildJob(job.id)
    ElMessage.success('删除成功')
    await fetchJobs()
  } catch {
    // cancelled
  }
}

onMounted(() => {
  fetchJobs()
  startPolling()
})
</script>
