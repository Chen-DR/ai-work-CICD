<template>
  <div class="code-editor">
    <div class="editor-header" v-if="title">
      <span class="editor-title">{{ title }}</span>
      <div class="editor-actions">
        <el-button v-if="readonly" size="small" type="primary" @click="$emit('edit')">
          <el-icon><Edit /></el-icon> 编辑
        </el-button>
        <el-button v-if="!readonly" size="small" type="success" @click="$emit('save')" :loading="saving">
          <el-icon><Check /></el-icon> 保存
        </el-button>
        <el-button v-if="!readonly" size="small" @click="$emit('cancel')">
          取消
        </el-button>
        <el-button size="small" @click="handleCopy">
          <el-icon><CopyDocument /></el-icon> {{ copied ? '已复制' : '复制' }}
        </el-button>
      </div>
    </div>
    <textarea
      ref="editorRef"
      :value="modelValue"
      @input="handleInput"
      class="editor-textarea"
      :readonly="readonly"
      spellcheck="false"
      :style="{ minHeight: minHeight }"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Edit, Check, CopyDocument } from '@element-plus/icons-vue'

const props = defineProps<{
  modelValue: string
  readonly?: boolean
  title?: string
  saving?: boolean
  minHeight?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
  save: []
  edit: []
  cancel: []
}>()

const copied = ref(false)
const editorRef = ref<HTMLTextAreaElement>()

function handleInput(e: Event) {
  emit('update:modelValue', (e.target as HTMLTextAreaElement).value)
}

async function handleCopy() {
  try {
    await navigator.clipboard.writeText(props.modelValue)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  } catch {
    // fallback
    const textarea = editorRef.value
    if (textarea) {
      textarea.select()
      document.execCommand('copy')
      copied.value = true
      setTimeout(() => { copied.value = false }, 2000)
    }
  }
}
</script>

<style scoped>
.code-editor {
  border: 1px solid var(--border-color);
  border-radius: 6px;
  overflow: hidden;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f8f9fa;
  border-bottom: 1px solid var(--border-color);
}

.editor-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-regular);
}

.editor-actions {
  display: flex;
  gap: 8px;
}

.editor-textarea {
  width: 100%;
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
  line-height: 1.6;
  padding: 16px;
  border: none;
  outline: none;
  resize: vertical;
  background: #1e1e1e;
  color: #d4d4d4;
  tab-size: 4;
}

.editor-textarea:read-only {
  cursor: default;
}

.editor-textarea:focus {
  outline: none;
}
</style>
