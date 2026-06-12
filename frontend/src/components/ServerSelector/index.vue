<template>
  <el-select
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    :placeholder="placeholder || '选择服务器'"
    :loading="loading"
    filterable
    style="width: 100%"
  >
    <el-option
      v-for="server in servers"
      :key="server.id"
      :label="`${server.name} (${server.host}:${server.port})`"
      :value="server.id"
      :disabled="server.status !== 'ACTIVE'"
    >
      <div class="server-option">
        <span>{{ server.name }}</span>
        <span class="server-host">{{ server.host }}</span>
        <el-tag v-if="server.status !== 'ACTIVE'" size="small" type="danger" effect="plain">
          {{ server.status }}
        </el-tag>
      </div>
    </el-option>
  </el-select>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { getServers } from '@/api/servers'
import type { Server } from '@/types/server'

const props = defineProps<{
  modelValue: number | null
  projectId?: number | null
  placeholder?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: number | null]
}>()

const servers = ref<Server[]>([])
const loading = ref(false)

async function fetchServers() {
  if (!props.projectId) return
  loading.value = true
  try {
    servers.value = await getServers(props.projectId)
  } catch {
    servers.value = []
  } finally {
    loading.value = false
  }
}

watch(() => props.projectId, () => {
  servers.value = []
  fetchServers()
}, { immediate: true })
</script>

<style scoped>
.server-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.server-host {
  color: var(--text-secondary);
  font-size: 12px;
}
</style>
