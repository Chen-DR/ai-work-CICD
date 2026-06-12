<template>
  <div class="chat-message" :class="[role, { 'has-references': references?.length }]">
    <div class="message-avatar">
      <el-avatar :size="36" :icon="role === 'user' ? UserFilled : Promotion" />
    </div>
    <div class="message-body">
      <div class="message-header">
        <span class="message-role">{{ role === 'user' ? '用户' : 'AI 助手' }}</span>
        <span class="message-time">{{ formatTime }}</span>
      </div>
      <div class="message-content markdown-body" v-html="renderedContent" />
      <div v-if="references?.length" class="message-references">
        <el-divider content-position="left">引用来源</el-divider>
        <div v-for="ref in references" :key="ref.chunk_id" class="reference-item">
          <el-tag size="small" type="info">{{ ref.document_title }}</el-tag>
          <p class="reference-text">{{ ref.content }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { UserFilled, Promotion } from '@element-plus/icons-vue'
import { formatDate } from '@/utils/date'
import { marked } from 'marked'
import type { KnowledgeReference } from '@/types/chat'

const props = defineProps<{
  role: 'user' | 'assistant' | 'system'
  content: string
  time?: string
  references?: KnowledgeReference[]
}>()

const formatTime = computed(() => props.time ? formatDate(props.time) : '')

const renderedContent = computed(() => {
  if (props.role === 'user') return props.content.replace(/\n/g, '<br>')
  return marked(props.content, { breaks: true }) as string
})
</script>

<style scoped>
.chat-message {
  display: flex;
  gap: 12px;
  padding: 16px 0;
}

.chat-message.user {
  flex-direction: row-reverse;
}

.message-body {
  max-width: 75%;
  min-width: 200px;
}

.user .message-body {
  text-align: right;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.user .message-header {
  justify-content: flex-end;
}

.message-role {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-regular);
}

.message-time {
  font-size: 12px;
  color: var(--text-secondary);
}

.message-content {
  font-size: 14px;
  line-height: 1.7;
  color: var(--text-primary);
  background: #f0f2f5;
  padding: 12px 16px;
  border-radius: 12px;
  text-align: left;
}

.user .message-content {
  background: var(--primary-color);
  color: white;
}

.message-references {
  margin-top: 8px;
}

.reference-item {
  background: #f8f9fa;
  border-radius: 6px;
  padding: 8px 12px;
  margin-top: 8px;
}

.reference-text {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}
</style>
