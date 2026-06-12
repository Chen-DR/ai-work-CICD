<template>
  <div class="page-container">
    <div class="page-header">
      <h2>知识库</h2>
      <div class="flex-center">
        <el-button @click="showSearchPanel = !showSearchPanel">
          <el-icon><Search /></el-icon> 测试检索
        </el-button>
        <el-upload
          :action="uploadAction"
          :headers="uploadHeaders"
          :data="{ project_id: projectStore.getCurrentProjectId() }"
          :on-success="handleUploadSuccess"
          :on-error="handleUploadError"
          :show-file-list="false"
          accept=".txt,.md,.log,.sh,.def,.json,.yaml,.yml"
        >
          <el-button type="primary" :icon="Upload">上传文档</el-button>
        </el-upload>
      </div>
    </div>

    <el-table :data="documents" v-loading="loading" stripe empty-text="暂无文档，请上传">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="file_name" label="文件名" min-width="180" />
      <el-table-column prop="title" label="标题" min-width="150" />
      <el-table-column label="状态" width="120">
        <template #default="{ row }">
          <JobStatusTag :status="row.status" />
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="上传时间" width="180" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button
            size="small"
            :disabled="row.status === 'PARSING'"
            @click="handleParse(row)"
          >
            重新解析
          </el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Search Panel -->
    <el-drawer v-model="showSearchPanel" title="测试知识库检索" size="400px">
      <el-form>
        <el-form-item label="查询内容">
          <el-input v-model="searchQuery" type="textarea" :rows="3" placeholder="输入检索内容" />
        </el-form-item>
        <el-form-item label="返回数量">
          <el-input-number v-model="searchTopK" :min="1" :max="20" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="searching" @click="handleSearch">检索</el-button>
        </el-form-item>
      </el-form>
      <div v-if="searchResults.length" class="search-results">
        <h4>检索结果 ({{ searchResults.length }})</h4>
        <div v-for="chunk in searchResults" :key="chunk.id" class="search-result-item">
          <el-tag size="small" type="info">{{ chunk.metadata?.file_name || '未知' }}</el-tag>
          <p class="result-content">{{ chunk.content }}</p>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Search, Upload } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import JobStatusTag from '@/components/JobStatusTag/index.vue'
import { getDocuments, deleteDocument, parseDocument, searchKnowledge } from '@/api/knowledge'
import { useProjectStore } from '@/stores/project'
import type { KnowledgeDocument, KnowledgeChunk } from '@/types/knowledge'

const projectStore = useProjectStore()

const documents = ref<KnowledgeDocument[]>([])
const loading = ref(false)
const showSearchPanel = ref(false)
const searchQuery = ref('')
const searchTopK = ref(5)
const searching = ref(false)
const searchResults = ref<KnowledgeChunk[]>([])

const uploadAction = computed(() => {
  const base = import.meta.env.VITE_API_BASE_URL || '/api/v1'
  return `${base}/knowledge/documents/`
})

const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${localStorage.getItem('token')}`,
}))

async function fetchDocuments() {
  const projectId = projectStore.getCurrentProjectId()
  loading.value = true
  try {
    documents.value = await getDocuments(projectId || undefined)
  } finally {
    loading.value = false
  }
}

function handleUploadSuccess() {
  ElMessage.success('上传成功')
  fetchDocuments()
}

function handleUploadError() {
  ElMessage.error('上传失败')
}

async function handleParse(doc: KnowledgeDocument) {
  try {
    await parseDocument(doc.id)
    ElMessage.success('开始解析')
    fetchDocuments()
  } catch {
    ElMessage.error('解析失败')
  }
}

async function handleDelete(doc: KnowledgeDocument) {
  try {
    await ElMessageBox.confirm(`确定删除「${doc.file_name}」吗？`, '确认', { type: 'warning' })
    await deleteDocument(doc.id)
    ElMessage.success('删除成功')
    fetchDocuments()
  } catch {
    // cancelled
  }
}

async function handleSearch() {
  const projectId = projectStore.getCurrentProjectId()
  if (!projectId || !searchQuery.value.trim()) return

  searching.value = true
  try {
    const result = await searchKnowledge({
      project_id: projectId,
      query: searchQuery.value,
      top_k: searchTopK.value,
    })
    searchResults.value = result.chunks || []
  } finally {
    searching.value = false
  }
}

onMounted(fetchDocuments)
</script>

<style scoped>
.search-results {
  margin-top: 16px;
}

.search-result-item {
  background: #f8f9fa;
  border-radius: 6px;
  padding: 12px;
  margin-top: 8px;
}

.result-content {
  font-size: 13px;
  color: var(--text-regular);
  margin-top: 6px;
  line-height: 1.6;
}
</style>
