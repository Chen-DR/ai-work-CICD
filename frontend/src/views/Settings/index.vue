<template>
  <div class="page-container">
    <div class="page-header">
      <h2>系统设置</h2>
    </div>

    <el-card class="mb-16">
      <template #header><span>个人信息</span></template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="用户名">{{ userStore.user?.username }}</el-descriptions-item>
        <el-descriptions-item label="显示名">{{ userStore.user?.display_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="角色">
          <el-tag size="small">{{ userStore.user?.role }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="登录状态">
          <el-tag type="success" size="small">已登录</el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card class="mb-16">
      <template #header><span>系统信息</span></template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="前端版本">v1.0.0</el-descriptions-item>
        <el-descriptions-item label="技术栈">
          Vue 3 + TypeScript + Element Plus
        </el-descriptions-item>
        <el-descriptions-item label="后端框架">Django + DRF</el-descriptions-item>
        <el-descriptions-item label="数据库">SQLite</el-descriptions-item>
        <el-descriptions-item label="异步任务">Celery + Redis</el-descriptions-item>
        <el-descriptions-item label="AI 模型">DeepSeek</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card class="mb-16">
      <template #header><span>主题设置</span></template>
      <el-form label-position="top">
        <el-form-item label="侧边栏模式">
          <el-radio-group :model-value="appStore.sidebarMode" @change="appStore.toggleSidebar">
            <el-radio value="expanded">展开</el-radio>
            <el-radio value="collapsed">收起</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { useUserStore } from '@/stores/user'
import { useAppStore } from '@/stores/app'

const userStore = useUserStore()
const appStore = useAppStore()
</script>
