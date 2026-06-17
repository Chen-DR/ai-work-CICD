<template>
  <div class="page-container">
    <div class="page-header">
      <h2>文件产物</h2>
    </div>

    <div class="search-bar">
      <el-select v-model="filterType" placeholder="筛选类型" clearable style="width: 200px">
        <el-option label="知识库文件" value="knowledge_file" />
        <el-option label="Apptainer Def" value="apptainer_def" />
        <el-option label="构建日志" value="build_log" />
        <el-option label="SIF 路径" value="sif_path_record" />
        <el-option label="压测脚本" value="benchmark_script" />
        <el-option label="压测日志" value="benchmark_log" />
        <el-option label="压测报告" value="benchmark_report" />
        <el-option label="脚本日志" value="script_log" />
        <el-option label="脚本产物" value="script_output" />
      </el-select>
    </div>

    <el-table :data="filteredArtifacts" v-loading="loading" stripe empty-text="暂无文件产物">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="file_name" label="文件名" min-width="200" show-overflow-tooltip />
      <el-table-column label="类型" width="130">
        <template #default="{ row }">
          <el-tag size="small">{{ artifactTypeLabel(row.artifact_type) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="文件大小" width="100">
        <template #default="{ row }">{{ formatFileSize(row.file_size) }}</template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" @click="handleDownload(row)">下载</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getArtifacts, downloadArtifact, deleteArtifact } from '@/api/artifacts'
import { formatFileSize, downloadBlob } from '@/utils/file'
import type { Artifact, ArtifactType } from '@/types/artifact'

const loading = ref(false)
const artifacts = ref<Artifact[]>([])
const filterType = ref('')

const filteredArtifacts = computed(() => {
  if (!filterType.value) return artifacts.value
  return artifacts.value.filter(a => a.artifact_type === filterType.value)
})

function artifactTypeLabel(type: ArtifactType): string {
  const map: Record<ArtifactType, string> = {
    knowledge_file: '知识库文件',
    apptainer_def: 'Apptainer Def',
    build_log: '构建日志',
    sif_path_record: 'SIF 路径',
    benchmark_script: '压测脚本',
    benchmark_log: '压测日志',
    benchmark_report: '压测报告',
    script_log: '脚本日志',
    script_output: '脚本产物',
  }
  return map[type] || type
}

async function fetchArtifacts() {
  loading.value = true
  try {
    artifacts.value = await getArtifacts()
  } finally {
    loading.value = false
  }
}

async function handleDownload(artifact: Artifact) {
  try {
    const blob = await downloadArtifact(artifact.id) as unknown as Blob
    downloadBlob(blob, artifact.file_name)
  } catch {
    ElMessage.error('下载失败')
  }
}

async function handleDelete(artifact: Artifact) {
  try {
    await ElMessageBox.confirm(`确定删除「${artifact.file_name}」吗？`, '确认', { type: 'warning' })
    await deleteArtifact(artifact.id)
    ElMessage.success('删除成功')
    await fetchArtifacts()
  } catch {
    // cancelled
  }
}

onMounted(fetchArtifacts)
</script>
