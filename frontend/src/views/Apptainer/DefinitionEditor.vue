<template>
  <div class="page-container">
    <div class="page-header">
      <h2>{{ isNew ? '新建 Definition' : `编辑 Definition #${route.params.id}` }}</h2>
      <div class="flex-center">
        <el-button @click="$router.push('/apptainer/definitions')">返回列表</el-button>
      </div>
    </div>

    <el-form label-position="top" class="definition-form">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item v-if="isNew" label="所属项目" required>
            <ProjectSelector v-model="form.project_id" />
          </el-form-item>
          <el-form-item v-else label="所属项目">
            <el-input :model-value="definitionProjectName" disabled placeholder="-" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="名称">
            <el-input v-model="form.name" placeholder="definition 名称" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="版本">
            <el-input v-model="form.version" placeholder="v1" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="Definition 内容">
        <CodeEditor
          v-model="form.content"
          :readonly="!editing"
          title="Apptainer Definition File"
          :saving="saving"
          language="apptainer"
          @edit="editing = true"
          @save="handleSave"
          @cancel="cancelEdit"
          min-height="400px"
        />
      </el-form-item>
    </el-form>

    <!-- Build button when viewing saved definition -->
    <div v-if="!isNew && !editing" class="mt-16">
      <el-button type="primary" :icon="Cpu" @click="showBuildDialog">创建构建任务</el-button>
    </div>

    <!-- Build Dialog -->
    <el-dialog v-model="buildVisible" title="创建构建任务" width="550px">
      <el-form label-position="top">
        <el-form-item label="目标服务器">
          <ServerSelector v-model="buildForm.server_id" :project-id="definitionProjectId" />
        </el-form-item>
        <el-form-item label="工作目录">
          <el-input v-model="buildForm.workdir" placeholder="/data/builds" />
        </el-form-item>
        <el-form-item label="输出文件名">
          <el-input v-model="buildForm.output_name" :placeholder="`${form.name || 'output'}.sif`" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="buildVisible = false">取消</el-button>
        <el-button type="primary" :loading="creatingBuild" @click="handleCreateBuild">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Cpu } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import CodeEditor from '@/components/CodeEditor/index.vue'
import ProjectSelector from '@/components/ProjectSelector/index.vue'
import ServerSelector from '@/components/ServerSelector/index.vue'
import { getDefinition, createDefinition, updateDefinition, createBuildJob } from '@/api/apptainer'
import { useProjectStore } from '@/stores/project'
import { sanitizeSifFileName } from '@/utils/file'
import type { ApptainerDefinition } from '@/types/apptainer'

const route = useRoute()
const router = useRouter()
const projectStore = useProjectStore()

const isNew = computed(() => route.params.id === 'new')
const definitionProjectId = computed(() => definition.value?.project_id ?? definition.value?.project ?? null)
const definitionProjectName = computed(() => {
  const projectId = definitionProjectId.value
  return projectStore.projects.find(p => p.id === projectId)?.name || (projectId ? `项目 #${projectId}` : '-')
})
const editing = ref(true)
const saving = ref(false)
const definition = ref<ApptainerDefinition | null>(null)

const form = reactive({
  project_id: projectStore.getCurrentProjectId() as number | null,
  name: '',
  version: 'v1',
  content: `Bootstrap: docker
From: ubuntu:22.04

%post
    apt-get update
    apt-get install -y python3 python3-pip

%environment
    export LC_ALL=C

%runscript
    exec python3 "$@"
`,
})

// Build dialog
const buildVisible = ref(false)
const creatingBuild = ref(false)
const buildForm = reactive({
  server_id: null as number | null,
  workdir: '',
  output_name: '',
})

onMounted(async () => {
  if (!isNew.value) {
    editing.value = false
    const id = Number(route.params.id)
    try {
      definition.value = await getDefinition(id)
      form.project_id = definition.value.project_id ?? definition.value.project ?? null
      form.name = definition.value.name
      form.version = definition.value.version
      form.content = definition.value.content
    } catch {
      ElMessage.error('加载 definition 失败')
      router.push('/apptainer/definitions')
    }
  }
})

function cancelEdit() {
  if (isNew.value) {
    router.push('/apptainer/definitions')
  } else if (definition.value) {
    form.project_id = definition.value.project_id ?? definition.value.project ?? null
    form.name = definition.value.name
    form.version = definition.value.version
    form.content = definition.value.content
    editing.value = false
  }
}

async function handleSave() {
  if (!form.name.trim() || !form.content.trim()) {
    ElMessage.warning('请填写名称和内容')
    return
  }
  if (isNew.value && !form.project_id) {
    ElMessage.warning('请选择所属项目')
    return
  }

  saving.value = true
  try {
    if (isNew.value) {
      const def = await createDefinition({
        project_id: form.project_id!,
        name: form.name,
        version: form.version,
        content: form.content,
      } as any)
      ElMessage.success('创建成功')
      router.push(`/apptainer/definitions/${def.id}`)
    } else {
      await updateDefinition(Number(route.params.id), {
        name: form.name,
        version: form.version,
        content: form.content,
      })
      ElMessage.success('保存成功')
      editing.value = false
      // Refresh
      definition.value = await getDefinition(Number(route.params.id))
    }
  } catch (e: any) {
    if (!e.handled) ElMessage.error(e.message || '保存失败')
  } finally {
    saving.value = false
  }
}

function showBuildDialog() {
  buildForm.server_id = null
  buildForm.workdir = ''
  buildForm.output_name = sanitizeSifFileName(form.name)
  buildVisible.value = true
}

async function handleCreateBuild() {
  const projectId = definitionProjectId.value
  if (!definition.value || !projectId) {
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
      project_id: projectId,
      definition_id: definition.value.id,
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
</script>
