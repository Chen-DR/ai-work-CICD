<template>
  <div class="page-container">
    <div class="page-header">
      <h2>服务器管理</h2>
      <el-button type="primary" :icon="Plus" @click="$router.push('/servers/new')">
        新增服务器
      </el-button>
    </div>

    <el-table :data="servers" v-loading="loading" stripe empty-text="暂无服务器">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="名称" min-width="120" />
      <el-table-column prop="host" label="主机" min-width="140" />
      <el-table-column prop="port" label="端口" width="80" />
      <el-table-column prop="username" label="用户名" width="100" />
      <el-table-column label="认证方式" width="100">
        <template #default="{ row }">
          <el-tag :type="row.auth_type === 'ssh_key' ? 'warning' : 'primary'" size="small">
            {{ row.auth_type === 'ssh_key' ? 'SSH Key' : '密码' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <JobStatusTag :status="row.status" />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="280" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="handleTestConnection(row)">测试</el-button>
          <el-button size="small" @click="$router.push(`/servers/${row.id}`)">详情</el-button>
          <el-button size="small" @click="handleEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Edit Dialog -->
    <el-dialog v-model="editVisible" title="编辑服务器" width="550px">
      <el-form label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="名称">
              <el-input v-model="editForm.name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-select v-model="editForm.status" style="width: 100%">
                <el-option label="可用" value="ACTIVE" />
                <el-option label="禁用" value="DISABLED" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSaveEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import JobStatusTag from '@/components/JobStatusTag/index.vue'
import { getServers, testServerConnection, updateServer, deleteServer } from '@/api/servers'
import type { Server, ServerStatus } from '@/types/server'

const servers = ref<Server[]>([])
const loading = ref(false)
const editVisible = ref(false)
const editingServer = ref<Server | null>(null)
const editForm = reactive({ name: '', status: 'ACTIVE' as ServerStatus })
const saving = ref(false)

async function fetchServers() {
  loading.value = true
  try {
    servers.value = await getServers()
  } finally {
    loading.value = false
  }
}

async function handleTestConnection(server: Server) {
  ElMessage.info('正在测试连接...')
  try {
    const result = await testServerConnection(server.id)
    if (result.success) {
      ElMessage.success('连接成功')
    } else {
      ElMessage.error(result.message || '连接失败')
    }
  } catch (e: any) {
    ElMessage.error(e.message || '连接测试失败')
  }
}

function handleEdit(server: Server) {
  editingServer.value = server
  editForm.name = server.name
  editForm.status = server.status
  editVisible.value = true
}

async function handleSaveEdit() {
  if (!editingServer.value) return
  saving.value = true
  try {
    await updateServer(editingServer.value.id, editForm)
    ElMessage.success('保存成功')
    editVisible.value = false
    await fetchServers()
  } finally {
    saving.value = false
  }
}

async function handleDelete(server: Server) {
  try {
    await ElMessageBox.confirm(`确定删除服务器「${server.name}」吗？`, '确认', { type: 'warning' })
    await deleteServer(server.id)
    ElMessage.success('删除成功')
    await fetchServers()
  } catch {
    // cancelled
  }
}

onMounted(fetchServers)
</script>
