<template>
  <el-select
    :model-value="modelValue"
    @update:model-value="handleChange"
    placeholder="选择项目"
    filterable
    style="width: 100%"
  >
    <el-option
      v-for="project in projects"
      :key="project.id"
      :label="project.name"
      :value="project.id"
    >
      <div class="project-option">
        <span>{{ project.name }}</span>
        <span class="project-desc">{{ project.description || '' }}</span>
      </div>
    </el-option>
  </el-select>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getProjects } from '@/api/projects'
import type { Project } from '@/types/project'

const props = defineProps<{
  modelValue: number | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: number | null]
}>()

const projects = ref<Project[]>([])

async function fetchProjects() {
  try {
    projects.value = await getProjects()
  } catch {
    projects.value = []
  }
}

function handleChange(val: number | null) {
  emit('update:modelValue', val)
}

onMounted(fetchProjects)
</script>

<style scoped>
.project-option {
  display: flex;
  flex-direction: column;
}

.project-desc {
  font-size: 12px;
  color: var(--text-secondary);
}
</style>
