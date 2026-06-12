<template>
  <div class="chat-input">
    <div class="input-toolbar">
      <el-checkbox v-model="useKnowledge" label="知识库增强" size="small" border />
    </div>
    <div class="input-area">
      <el-input
        ref="inputRef"
        v-model="inputText"
        type="textarea"
        :rows="3"
        placeholder="输入消息，按 Enter 发送（Shift+Enter 换行）"
        @keydown.enter.exact="handleSend"
        :disabled="loading"
      />
      <el-button
        type="primary"
        :icon="Promotion"
        :loading="loading"
        :disabled="!inputText.trim()"
        @click="handleSend"
        class="send-btn"
      >
        发送
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Promotion } from '@element-plus/icons-vue'

const props = defineProps<{
  loading?: boolean
}>()

const emit = defineEmits<{
  send: [message: string, useKnowledge: boolean]
}>()

const inputText = ref('')
const useKnowledge = ref(true)
const inputRef = ref()

function handleSend() {
  const text = inputText.value.trim()
  if (!text || props.loading) return
  emit('send', text, useKnowledge.value)
  inputText.value = ''
}
</script>

<style scoped>
.chat-input {
  border-top: 1px solid var(--border-color);
  padding: 16px 20px;
  background: white;
}

.input-toolbar {
  margin-bottom: 12px;
}

.input-area {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.send-btn {
  height: 76px;
}
</style>
