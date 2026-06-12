<template>
  <div class="log-viewer" ref="logContainer">
    <div class="log-toolbar">
      <span class="log-title">{{ title || '运行日志' }}</span>
      <div class="log-actions">
        <el-button size="small" @click="handleRefresh" :loading="refreshing">
          <el-icon><Refresh /></el-icon>
        </el-button>
        <el-button size="small" @click="handleCopy">
          <el-icon><CopyDocument /></el-icon>
        </el-button>
        <el-checkbox v-model="autoScroll" label="自动滚动" size="small" />
      </div>
    </div>
    <div class="log-content">
      <div v-if="!logs" class="log-empty">
        <el-empty description="暂无日志" :image-size="40" />
      </div>
      <pre v-else class="log-text" ref="logText">{{ logs }}</pre>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { Refresh, CopyDocument } from '@element-plus/icons-vue'

const props = defineProps<{
  logs: string | null
  loading?: boolean
  title?: string
}>()

const emit = defineEmits<{
  refresh: []
}>()

const autoScroll = ref(true)
const refreshing = ref(false)
const logText = ref<HTMLElement>()
const logContainer = ref<HTMLElement>()

watch(() => props.logs, async () => {
  if (autoScroll.value) {
    await nextTick()
    if (logContainer.value) {
      logContainer.value.scrollTop = logContainer.value.scrollHeight
    }
  }
})

async function handleRefresh() {
  refreshing.value = true
  emit('refresh')
  await nextTick()
  refreshing.value = false
}

async function handleCopy() {
  if (props.logs) {
    try {
      await navigator.clipboard.writeText(props.logs)
    } catch {
      // ignore
    }
  }
}
</script>

<style scoped>
.log-viewer {
  border: 1px solid var(--border-color);
  border-radius: 6px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.log-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f8f9fa;
  border-bottom: 1px solid var(--border-color);
}

.log-title {
  font-size: 13px;
  font-weight: 600;
}

.log-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.log-content {
  overflow-y: auto;
  max-height: 500px;
  min-height: 200px;
  background: #1e1e1e;
}

.log-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}

.log-text {
  font-family: 'Courier New', Courier, monospace;
  font-size: 12px;
  line-height: 1.6;
  padding: 16px;
  margin: 0;
  color: #d4d4d4;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>
