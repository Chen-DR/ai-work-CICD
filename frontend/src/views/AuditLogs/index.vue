<template>
  <div class="page-container">
    <div class="page-header">
      <h2>审计日志</h2>
    </div>

    <div class="search-bar">
      <el-input v-model="filterAction" placeholder="筛选操作类型" clearable style="width: 200px" />
      <el-button type="primary" @click="fetchLogs">
        <el-icon><Search /></el-icon> 查询
      </el-button>
    </div>

    <el-table :data="logs" v-loading="loading" stripe empty-text="暂无审计日志">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column label="用户" width="100">
        <template #default="{ row }">#{{ row.user_id }}</template>
      </el-table-column>
      <el-table-column prop="action" label="操作" width="200">
        <template #default="{ row }">
          <el-tag size="small">{{ row.action }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="resource_type" label="资源类型" width="120" />
      <el-table-column prop="resource_id" label="资源 ID" width="80" />
      <el-table-column prop="detail" label="详情" show-overflow-tooltip />
      <el-table-column prop="ip_address" label="IP" width="130" />
      <el-table-column prop="created_at" label="时间" width="180" />
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { getAuditLogs } from '@/api/audit'
import type { AuditLogEntry } from '@/api/audit'

const logs = ref<AuditLogEntry[]>([])
const loading = ref(false)
const filterAction = ref('')

async function fetchLogs() {
  loading.value = true
  try {
    logs.value = await getAuditLogs({
      action: filterAction.value || undefined,
    })
  } finally {
    loading.value = false
  }
}

onMounted(fetchLogs)
</script>
