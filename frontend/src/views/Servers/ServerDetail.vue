<template>
  <div class="page-container">
    <div class="page-header">
      <h2>服务器详情 #{{ route.params.id }}</h2>
      <el-button @click="$router.push('/servers')">返回列表</el-button>
    </div>

    <el-card v-loading="loading" class="mb-16">
      <el-descriptions title="基本信息" :column="2" border>
        <el-descriptions-item label="名称">{{ server?.name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <JobStatusTag v-if="server" :status="server.status" />
        </el-descriptions-item>
        <el-descriptions-item label="主机">{{ server?.host || '-' }}</el-descriptions-item>
        <el-descriptions-item label="端口">{{ server?.port || '-' }}</el-descriptions-item>
        <el-descriptions-item label="用户名">{{ server?.username || '-' }}</el-descriptions-item>
        <el-descriptions-item label="认证方式">
          <el-tag :type="server?.auth_type === 'ssh_key' ? 'warning' : 'primary'" size="small">
            {{ server?.auth_type === 'ssh_key' ? 'SSH Key' : '密码' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ server?.created_at || '-' }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ server?.updated_at || '-' }}</el-descriptions-item>
      </el-descriptions>

      <div class="mt-16 flex-center" style="gap: 12px">
        <el-button type="primary" :loading="testing" @click="handleTest">
          测试连接
        </el-button>
        <el-button :loading="detecting" @click="handleDetect">
          检测环境
        </el-button>
      </div>
    </el-card>

    <el-card v-if="detectResult" class="mb-16">
      <template #header><span>环境检测结果</span></template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="主机名">{{ detectResult.hostname || '-' }}</el-descriptions-item>
        <el-descriptions-item label="操作系统">{{ detectResult.os || '-' }}</el-descriptions-item>
        <el-descriptions-item label="Apptainer">{{ detectResult.apptainer_version || '-' }}</el-descriptions-item>
        <el-descriptions-item label="Python">{{ detectResult.python_version || '-' }}</el-descriptions-item>
        <el-descriptions-item label="CUDA">{{ detectResult.cuda_version || '-' }}</el-descriptions-item>
        <el-descriptions-item label="磁盘">{{ detectResult.disk_info || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- Allowed Dirs -->
    <el-card class="mb-16">
      <template #header>
        <div class="flex-between">
          <span>允许的工作目录</span>
          <el-button size="small" type="primary" @click="showAddDirDialog">
            <el-icon><Plus /></el-icon> 添加
          </el-button>
        </div>
      </template>
      <el-table :data="allowedDirs" stripe empty-text="暂无配置">
        <el-table-column prop="path" label="路径" min-width="250" />
        <el-table-column prop="purpose" label="用途" width="150" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button size="small" type="danger" @click="handleRemoveDir(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Add Dir Dialog -->
    <el-dialog v-model="addDirVisible" title="添加允许目录" width="450px">
      <el-form label-position="top">
        <el-form-item label="路径">
          <el-input v-model="newDir.path" placeholder="/data/builds" />
        </el-form-item>
        <el-form-item label="用途">
          <el-select v-model="newDir.purpose" style="width: 100%">
            <el-option label="构建" value="build" />
            <el-option label="压测" value="benchmark" />
            <el-option label="报告" value="report" />
            <el-option label="通用" value="general" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addDirVisible = false">取消</el-button>
        <el-button type="primary" :loading="addingDir" @click="handleAddDir">添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useRoute } from 'vue-router'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import JobStatusTag from '@/components/JobStatusTag/index.vue'
import { getServer, testServerConnection, detectServerEnvironment } from '@/api/servers'
import type { Server, ServerDetectResult, ServerAllowedDir } from '@/types/server'

const route = useRoute()
const server = ref<Server | null>(null)
const loading = ref(false)
const testing = ref(false)
const detecting = ref(false)
const detectResult = ref<ServerDetectResult | null>(null)
const allowedDirs = ref<ServerAllowedDir[]>([])

const addDirVisible = ref(false)
const addingDir = ref(false)
const newDir = reactive({ path: '', purpose: 'general' })

async function fetchServer() {
  loading.value = true
  try {
    server.value = await getServer(Number(route.params.id))
  } finally {
    loading.value = false
  }
}

async function handleTest() {
  testing.value = true
  try {
    const result = await testServerConnection(Number(route.params.id))
    if (result.success) {
      ElMessage.success('连接成功')
    } else {
      ElMessage.error(result.message || '连接失败')
    }
  } catch (e: any) {
    ElMessage.error(e.message || '测试失败')
  } finally {
    testing.value = false
  }
}

async function handleDetect() {
  detecting.value = true
  try {
    detectResult.value = await detectServerEnvironment(Number(route.params.id))
    ElMessage.success('环境检测完成')
  } catch (e: any) {
    ElMessage.error(e.message || '检测失败')
  } finally {
    detecting.value = false
  }
}

function showAddDirDialog() {
  newDir.path = ''
  newDir.purpose = 'general'
  addDirVisible.value = true
}

async function handleAddDir() {
  if (!newDir.path) {
    ElMessage.warning('请输入路径')
    return
  }
  addingDir.value = true
  try {
    // TODO: add allowed dir API
    ElMessage.success('添加成功')
    addDirVisible.value = false
  } finally {
    addingDir.value = false
  }
}

function handleRemoveDir(dir: ServerAllowedDir) {
  // TODO: remove allowed dir API
  ElMessage.success('已删除')
}

onMounted(fetchServer)
</script>
