<template>
  <el-tag :type="tagType" :hit="false" size="small">
    {{ statusText }}
  </el-tag>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  status: string
}>()

const statusMap: Record<string, { type: string; text: string }> = {
  PENDING: { type: 'info', text: '等待执行' },
  VALIDATING: { type: 'warning', text: '校验中' },
  UPLOADING: { type: 'warning', text: '上传中' },
  RUNNING: { type: 'primary', text: '运行中' },
  COLLECTING: { type: 'warning', text: '收集中' },
  SUCCESS: { type: 'success', text: '成功' },
  FAILED: { type: 'danger', text: '失败' },
  CANCELLED: { type: 'info', text: '已取消' },
  TIMEOUT: { type: 'danger', text: '超时' },
  ACTIVE: { type: 'success', text: '可用' },
  DISABLED: { type: 'info', text: '禁用' },
  UNKNOWN: { type: 'warning', text: '未知' },
  UPLOADED: { type: 'info', text: '已上传' },
  PARSING: { type: 'warning', text: '解析中' },
  READY: { type: 'success', text: '可用' },
}

const tagType = computed(() => statusMap[props.status]?.type || 'info')
const statusText = computed(() => statusMap[props.status]?.text || props.status)
</script>
