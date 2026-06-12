<template>
  <div class="page-container">
    <div class="page-header">
      <h2>上传压测脚本</h2>
      <el-button @click="$router.push('/benchmark/scripts')">返回列表</el-button>
    </div>

    <el-card style="max-width: 600px">
      <el-form label-position="top">
        <el-form-item label="所属项目">
          <ProjectSelector v-model="form.project_id" />
        </el-form-item>
        <el-form-item label="脚本名称">
          <el-input v-model="form.name" placeholder="脚本名称" />
        </el-form-item>
        <el-form-item label="脚本类型">
          <el-select v-model="form.script_type" style="width: 100%">
            <el-option label="CPU" value="cpu" />
            <el-option label="硬盘" value="disk" />
            <el-option label="GPU" value="gpu" />
            <el-option label="混合" value="mixed" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="脚本描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="脚本用途说明" />
        </el-form-item>
        <el-form-item label="脚本文件">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :on-change="handleFileChange"
            :limit="1"
            accept=".sh,.py,.pl,.rb,.js,.bat,.exe"
          >
            <el-button type="primary">选择文件</el-button>
            <template #tip>
              <p style="font-size: 12px; color: var(--text-secondary)">支持 .sh .py .pl .rb 等脚本文件</p>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="uploading" @click="handleUpload" :disabled="!selectedFile">
            {{ uploading ? '上传中...' : '上传' }}
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import ProjectSelector from '@/components/ProjectSelector/index.vue'
import { uploadScript } from '@/api/benchmark'
import { useProjectStore } from '@/stores/project'

const router = useRouter()
const projectStore = useProjectStore()

const selectedFile = ref<File | null>(null)
const uploading = ref(false)
const uploadRef = ref()

const form = reactive({
  project_id: projectStore.getCurrentProjectId() ?? undefined as any,
  name: '',
  script_type: 'cpu',
  description: '',
})

function handleFileChange(file: any) {
  selectedFile.value = file.raw
}

async function handleUpload() {
  if (!form.name.trim()) {
    ElMessage.warning('请输入脚本名称')
    return
  }
  if (!selectedFile.value || !form.project_id) {
    ElMessage.warning('请选择项目和文件')
    return
  }

  uploading.value = true
  try {
    await uploadScript(
      form.project_id!,
      form.name.trim(),
      form.script_type,
      selectedFile.value,
      form.description
    )
    ElMessage.success('上传成功')
    router.push('/benchmark/scripts')
  } catch (e: any) {
    ElMessage.error(e.message || '上传失败')
  } finally {
    uploading.value = false
  }
}
</script>
