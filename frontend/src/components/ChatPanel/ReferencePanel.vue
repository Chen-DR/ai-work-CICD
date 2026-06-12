<template>
  <div class="reference-panel">
    <h4 class="panel-title">知识库引用</h4>
    <div v-if="!references?.length" class="empty-state">
      <el-empty description="暂无引用" :image-size="60" />
    </div>
    <div v-else class="reference-list">
      <div v-for="ref in references" :key="ref.chunk_id" class="ref-card">
        <div class="ref-header">
          <el-tag size="small" type="info">{{ ref.document_title }}</el-tag>
        </div>
        <p class="ref-content">{{ ref.content }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { KnowledgeReference } from '@/types/chat'

defineProps<{
  references?: KnowledgeReference[]
}>()
</script>

<style scoped>
.reference-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 16px;
}

.panel-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--text-primary);
}

.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.reference-list {
  overflow-y: auto;
  flex: 1;
}

.ref-card {
  background: #f8f9fa;
  border-radius: 6px;
  padding: 10px 12px;
  margin-bottom: 8px;
  border: 1px solid var(--border-color);
}

.ref-header {
  margin-bottom: 6px;
}

.ref-content {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.6;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 5;
  -webkit-box-orient: vertical;
}
</style>
