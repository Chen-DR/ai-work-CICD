<template>
  <div class="file-uploader">
    <el-upload
      drag
      :action="uploadUrl"
      :headers="headers"
      :data="uploadData"
      :before-upload="handleBeforeUpload"
      :on-success="handleSuccess"
      :on-error="handleError"
      :on-progress="handleProgress"
      :show-file-list="true"
      :limit="1"
      :auto-upload="autoUpload"
      ref="uploadRef"
    >
      <el-icon class="upload-icon" :size="40"><UploadFilled /></el-icon>
      <div class="upload-text">
        <span>拖拽文件到此处，或<em>点击上传</em></span>
      </div>
      <template #tip>
        <div class="upload-tip">
          <p v-if="accept">支持格式：{{ accept }}</p>
          <p v-if="maxSize">最大文件大小：{{ formatFileSize(maxSize) }}</p>
        </div>
      </template>
    </el-upload>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { formatFileSize } from '@/utils/file'

const props = defineProps<{
  action: string
  accept?: string
  maxSize?: number
  data?: Record<string, unknown>
  autoUpload?: boolean
}>()

const emit = defineEmits<{
  success: [response: unknown]
  error: [error: Error]
}>()

const headers = computed(() => ({
  Authorization: `Bearer ${localStorage.getItem('token')}`,
}))

const uploadUrl = computed(() => {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1'
  return `${baseUrl}${props.action}`
})

const uploadData = computed(() => props.data || {})

function handleBeforeUpload(file: File) {
  if (props.maxSize && file.size > props.maxSize) {
    ElMessage.error(`文件大小不能超过 ${formatFileSize(props.maxSize)}`)
    return false
  }
  return true
}

function handleSuccess(response: unknown) {
  ElMessage.success('上传成功')
  emit('success', response)
}

function handleError(error: Error) {
  ElMessage.error('上传失败')
  emit('error', error)
}

function handleProgress() {
  // upload progress
}
</script>

<style scoped>
.upload-icon {
  margin-bottom: 8px;
}

.upload-text {
  font-size: 14px;
  color: var(--text-regular);

  em {
    color: var(--primary-color);
    font-style: normal;
  }
}

.upload-tip {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 8px;
}
</style>
