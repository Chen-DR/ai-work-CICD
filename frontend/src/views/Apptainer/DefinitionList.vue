<template>
  <div class="page-container">
    <div class="page-header">
      <h2>Definition 管理</h2>
      <div class="flex-center">
        <el-button @click="showGenerateDialog">
          <el-icon><MagicStick /></el-icon> AI 生成
        </el-button>
        <el-button type="primary" :icon="Plus" @click="$router.push('/apptainer/definitions/new')">
          新建 Definition
        </el-button>
      </div>
    </div>

    <el-table :data="definitions" v-loading="loading" stripe empty-text="暂无 definition">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="名称" min-width="150" />
      <el-table-column prop="version" label="版本" width="80" />
      <el-table-column label="内容预览" min-width="300">
        <template #default="{ row }">
          <code class="preview-code">{{ row.content?.slice(0, 120) }}...</code>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="250" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="$router.push(`/apptainer/definitions/${row.id}`)">编辑</el-button>
          <el-button size="small" type="primary" @click="showBuildDialog(row)">构建</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- AI Generate Dialog -->
    <el-dialog v-model="generateVisible" title="AI 生成 Definition" width="600px">
      <el-form label-position="top">
        <el-form-item label="项目">
          <ProjectSelector v-model="generateForm.project_id" />
        </el-form-item>
        <el-form-item label="容器需求描述">
          <el-input
            v-model="generateForm.requirement"
            type="textarea"
            :rows="4"
            placeholder="例：Ubuntu 22.04 + Python 3.10 + CUDA 12.1 + PyTorch"
          />
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="generateForm.use_knowledge" label="使用知识库增强" border />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="generateVisible = false">取消</el-button>
        <el-button type="primary" :loading="generating" @click="handleGenerate">生成</el-button>
      </template>
    </el-dialog>

    <!-- Build Dialog -->
    <el-dialog v-model="buildVisible" title="创建构建任务" width="550px">
      <el-form label-position="top">
        <el-form-item label="目标服务器">
          <ServerSelector v-model="buildForm.server_id" :project-id="buildForm.project_id" />
        </el-form-item>
        <el-form-item label="工作目录">
          <el-input v-model="buildForm.workdir" placeholder="/data/builds/my_image" />
        </el-form-item>
        <el-form-item label="输出文件名">
          <el-input v-model="buildForm.output_name" placeholder="my_image.sif" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="buildVisible = false">取消</el-button>
        <el-button type="primary" :loading="creatingBuild" @click="handleCreateBuild">创建任务</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { MagicStick, Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import ProjectSelector from '@/components/ProjectSelector/index.vue'
import ServerSelector from '@/components/ServerSelector/index.vue'
import { getDefinitions, deleteDefinition, generateDefinition, createBuildJob } from '@/api/apptainer'
import { useProjectStore } from '@/stores/project'
import { useRouter } from 'vue-router'
import { sanitizeSifFileName } from '@/utils/file'
import type { ApptainerDefinition } from '@/types/apptainer'

const router = useRouter()
const projectStore = useProjectStore()

const definitions = ref<ApptainerDefinition[]>([])
const loading = ref(false)

// Generate dialog
const generateVisible = ref(false)
const generating = ref(false)
const generateForm = reactive({
  project_id: projectStore.getCurrentProjectId() as number | null,
  requirement: '',
  use_knowledge: true,
})

// Build dialog
const buildVisible = ref(false)
const creatingBuild = ref(false)
const buildTarget = ref<ApptainerDefinition | null>(null)
const buildForm = reactive({
  project_id: projectStore.getCurrentProjectId() as number | null,
  server_id: null as number | null,
  workdir: '',
  output_name: '',
})

async function fetchDefinitions() {
  loading.value = true
  try {
    definitions.value = await getDefinitions()
  } finally {
    loading.value = false
  }
}

function showGenerateDialog() {
  generateForm.project_id = projectStore.getCurrentProjectId()
  generateVisible.value = true
}

async function handleGenerate() {
  if (!generateForm.requirement.trim()) {
    ElMessage.warning('请输入容器需求')
    return
  }
  generating.value = true
  try {
    const def = await generateDefinition({
      project_id: generateForm.project_id!,
      conversation_id: 0,
      requirement: generateForm.requirement,
      use_knowledge: generateForm.use_knowledge,
    })
    ElMessage.success('生成成功')
    generateVisible.value = false
    await fetchDefinitions()
    router.push(`/apptainer/definitions/${def.id}`)
  } catch (e: any) {
    if (!e.handled) ElMessage.error(e.message || '生成失败')
  } finally {
    generating.value = false
  }
}

function showBuildDialog(def: ApptainerDefinition) {
  buildTarget.value = def
  buildForm.project_id = def.project_id ?? def.project ?? null
  buildForm.server_id = null
  buildForm.workdir = ''
  buildForm.output_name = sanitizeSifFileName(def.name)
  buildVisible.value = true
}

async function handleCreateBuild() {
  if (!buildTarget.value || !buildForm.project_id) {
    ElMessage.warning('Definition 缺少项目归属，无法创建构建任务')
    return
  }
  if (!buildForm.server_id) {
    ElMessage.warning('请选择目标服务器')
    return
  }
  creatingBuild.value = true
  try {
    const job = await createBuildJob({
      project_id: buildForm.project_id,
      definition_id: buildTarget.value.id,
      server_id: buildForm.server_id,
      workdir: buildForm.workdir,
      output_name: buildForm.output_name,
    })
    ElMessage.success('构建任务已创建')
    buildVisible.value = false
    router.push(`/apptainer/build-jobs/${job.id}`)
  } catch (e: any) {
    if (!e.handled) ElMessage.error(e.message || '创建失败')
  } finally {
    creatingBuild.value = false
  }
}

async function handleDelete(def: ApptainerDefinition) {
  try {
    await ElMessageBox.confirm(`确定删除「${def.name}」吗？`, '确认', { type: 'warning' })
    await deleteDefinition(def.id)
    ElMessage.success('删除成功')
    await fetchDefinitions()
  } catch {
    // cancelled
  }
}

onMounted(fetchDefinitions)
</script>

<style scoped>
.preview-code {
  font-size: 12px;
  color: #666;
  background: #f5f5f5;
  padding: 4px 8px;
  border-radius: 4px;
}
</style>
