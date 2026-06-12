<template>
  <div class="report-viewer">
    <div v-if="!reportUrl" class="report-empty">
      <el-empty description="暂无报告" :image-size="60" />
    </div>
    <iframe v-else :src="reportUrl" class="report-iframe" />
  </div>
</template>

<script setup lang="ts">
defineProps<{
  reportUrl?: string | null
}>()
</script>

<style scoped>
.report-viewer {
  height: 100%;
  min-height: 400px;
}

.report-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.report-iframe {
  width: 100%;
  height: 100%;
  border: none;
  min-height: 600px;
}
</style>
