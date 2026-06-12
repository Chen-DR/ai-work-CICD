<template>
  <div class="page-container">
    <div class="page-header">
      <h2>压测脚本管理</h2>
      <el-button type="primary" :icon="Upload" @click="$router.push('/benchmark/scripts/upload')">
        上传脚本
      </el-button>
    </div>

    <el-table :data="scripts" v-loading="loading" stripe empty-text="暂无压测脚本">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="名称" min-width="150" />
      <el-table-column label="类型" width="100">
        <template #default="{ row }">
          <el-tag :type="scriptTypeTag(row.script_type)" size="small">{{ row.script_type }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="version" label="版本" width="80" />
      <el-table-column prop="file_name" label="文件名" min-width="180" />
      <el-table-column prop="description" label="描述" show-overflow-tooltip />
      <el-table-column prop="created_at" label="上传时间" width="180" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" @click="showRunDialog(row)">运行</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Run Dialog -->
    <el-dialog v-model="runVisible" title="创建压测任务" width="550px">
      <el-form label-position="top">
        <el-form-item label="脚本">{{ runTarget?.name }}</el-form-item>
        <el-form-item label="目标服务器">
          <ServerSelector v-model="runForm.server_id" :project-id="runTarget?.project_id" />
        </el-form-item>
        <el-form-item label="工作目录">
          <el-input v-model="runForm.workdir" placeholder="/data/benchmark" />
        </el-form-item>
        <el-form-item label="压测参数（JSON）">
          <el-input
            v-model="runForm.paramsStr"
            type="textarea"
            :rows="4"
            placeholder='{"duration": 300, "threads": 16}'
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="runVisible = false">取消</el-button>
        <el-button type="primary" :loading="running" @click="handleRun">开始压测</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { Upload } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import ServerSelector from '@/components/ServerSelector/index.vue'
import { getScripts, deleteScript, createBenchmarkJob } from '@/api/benchmark'
import { useRouter } from 'vue-router'
import type { BenchmarkScript } from '@/types/benchmark'

const router = useRouter()

const scripts = ref<BenchmarkScript[]>([])
const loading = ref(false)

const runVisible = ref(false)
const running = ref(false)
const runTarget = ref<BenchmarkScript | null>(null)
const runForm = reactive({
  server_id: null as number | null,
  workdir: '',
  paramsStr: '',
})

function scriptTypeTag(type: string) {
  const map: Record<string, string> = { cpu: 'primary', disk: 'success', gpu: 'danger', mixed: 'warning', custom: 'info' }
  return map[type] || 'info'
}

async function fetchScripts() {
  loading.value = true
  try {
    scripts.value = await getScripts()
  } finally {
    loading.value = false
  }
}

function showRunDialog(script: BenchmarkScript) {
  runTarget.value = script
  runForm.server_id = null
  runForm.workdir = ''
  runForm.paramsStr = JSON.stringify({ duration: 300, threads: 16 }, null, 2)
  runVisible.value = true
}

async function handleRun() {
  if (!runTarget.value) return
  let params: Record<string, unknown>
  try {
    params = JSON.parse(runForm.paramsStr)
  } catch {
    ElMessage.error('参数格式错误，请输入合法 JSON')
    return
  }

  running.value = true
  try {
    const job = await createBenchmarkJob({
      project_id: runTarget.value.project_id,
      script_id: runTarget.value.id,
      server_id: runForm.server_id!,
      workdir: runForm.workdir,
      params,
    })
    ElMessage.success('压测任务已创建')
    runVisible.value = false
    router.push(`/benchmark/jobs/${job.id}`)
  } catch (e: any) {
    ElMessage.error(e.message || '创建失败')
  } finally {
    running.value = false
  }
}

async function handleDelete(script: BenchmarkScript) {
  try {
    await ElMessageBox.confirm(`确定删除脚本「${script.name}」吗？`, '确认', { type: 'warning' })
    await deleteScript(script.id)
    ElMessage.success('删除成功')
    await fetchScripts()
  } catch {
    // cancelled
  }
}

onMounted(fetchScripts)
</script>
