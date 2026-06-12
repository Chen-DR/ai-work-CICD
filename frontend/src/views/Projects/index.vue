<template>
  <div class="page-container">
    <div class="page-header">
      <h2>项目管理</h2>
      <el-button type="primary" @click="showCreateDialog">
        <el-icon><Plus /></el-icon> 新建项目
      </el-button>
    </div>

    <el-table :data="projects" v-loading="loading" stripe empty-text="暂无项目">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="项目名称" min-width="150" />
      <el-table-column prop="description" label="描述" show-overflow-tooltip />
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="selectProject(row)">切换</el-button>
          <el-button size="small" @click="showEditDialog(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingId ? '编辑项目' : '新建项目'"
      width="500px"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="项目名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="项目描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getProjects, createProject, updateProject, deleteProject } from '@/api/projects'
import { useProjectStore } from '@/stores/project'
import { useRouter } from 'vue-router'
import type { Project } from '@/types/project'
import type { FormInstance } from 'element-plus'

const router = useRouter()
const projectStore = useProjectStore()

const projects = ref<Project[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const saving = ref(false)
const formRef = ref<FormInstance>()

const form = reactive({
  name: '',
  description: '',
})

const rules = {
  name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
}

async function fetchProjects() {
  loading.value = true
  try {
    projects.value = await getProjects()
    projectStore.projects = projects.value
  } finally {
    loading.value = false
  }
}

function showCreateDialog() {
  editingId.value = null
  form.name = ''
  form.description = ''
  dialogVisible.value = true
}

function showEditDialog(project: Project) {
  editingId.value = project.id
  form.name = project.name
  form.description = project.description
  dialogVisible.value = true
}

async function handleSave() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    if (editingId.value) {
      await updateProject(editingId.value, form)
      ElMessage.success('更新成功')
    } else {
      await createProject(form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    await fetchProjects()
  } finally {
    saving.value = false
  }
}

async function handleDelete(project: Project) {
  try {
    await ElMessageBox.confirm(`确定删除项目「${project.name}」吗？`, '确认', {
      type: 'warning',
    })
    await deleteProject(project.id)
    ElMessage.success('删除成功')
    await fetchProjects()
  } catch {
    // cancelled
  }
}

function selectProject(project: Project) {
  projectStore.setCurrentProject(project)
  ElMessage.success(`已切换到项目：${project.name}`)
  router.push('/dashboard')
}

onMounted(fetchProjects)
</script>
