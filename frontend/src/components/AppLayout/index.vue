<template>
  <el-container class="app-layout">
    <!-- ======== SIDEBAR ======== -->
    <el-aside
      :width="appStore.sidebarMode === 'expanded' ? '240px' : '64px'"
      class="app-sidebar"
    >
      <div class="sidebar-header">
        <span class="sidebar-logo-icon">AI</span>
        <span v-show="appStore.sidebarMode === 'expanded'" class="sidebar-logo-text">AI-Ops</span>
      </div>

      <el-scrollbar class="sidebar-scroll">
        <el-menu
          :default-active="route.path"
          :collapse="appStore.sidebarMode === 'collapsed'"
          router
          class="sidebar-menu"
        >
          <template v-for="item in menuItems" :key="item.path || item.group || item.divider">
            <div v-if="item.divider && appStore.sidebarMode === 'expanded'" class="menu-divider">
              <span>{{ item.divider }}</span>
            </div>
            <el-sub-menu v-else-if="item.children" :index="item.group!">
              <template #title>
                <el-icon><component :is="item.icon" /></el-icon>
                <span>{{ item.label }}</span>
              </template>
              <el-menu-item v-for="child in item.children" :key="child.path" :index="child.path">
                {{ child.label }}
              </el-menu-item>
            </el-sub-menu>
            <el-menu-item v-else-if="item.path" :index="item.path">
              <el-icon><component :is="item.icon" /></el-icon>
              <template #title>{{ item.label }}</template>
            </el-menu-item>
          </template>
        </el-menu>
      </el-scrollbar>

      <div class="sidebar-footer">
        <el-button text class="collapse-btn" @click="appStore.toggleSidebar">
          <el-icon><Fold v-if="appStore.sidebarMode === 'expanded'" /><Expand v-else /></el-icon>
        </el-button>
      </div>
    </el-aside>

    <el-container>
      <!-- ======== HEADER ======== -->
      <el-header v-if="!route.meta?.hideTopBar" class="app-header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/dashboard' }">驾驶舱</el-breadcrumb-item>
            <el-breadcrumb-item v-if="route.meta.title && route.path !== '/dashboard'">
              {{ route.meta.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>

          <!-- Current project indicator -->
          <el-dropdown
            v-if="projectStore.projects.length"
            @command="switchProject"
            trigger="click"
          >
            <span class="project-badge">
              <el-icon :size="14"><FolderOpened /></el-icon>
              <span>{{ projectStore.currentProject?.name || '选择项目' }}</span>
              <el-icon :size="12"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item
                  v-for="p in projectStore.projects"
                  :key="p.id"
                  :command="p.id"
                >
                  <span :class="{ 'text-primary': p.id === projectStore.currentProject?.id }">
                    {{ p.name }}
                  </span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <span v-else class="project-badge project-badge--empty" @click="router.push('/projects')">
            <el-icon :size="14"><FolderOpened /></el-icon>
            <span>未选择项目</span>
          </span>
        </div>

        <div class="header-right">
          <el-dropdown trigger="click">
            <span class="user-info">
              <el-avatar :size="28" :icon="UserFilled" style="background: #6366f1" />
              <span class="username">{{ userStore.user?.display_name || userStore.user?.username || '用户' }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="handleLogout">
                  <el-icon><SwitchButton /></el-icon> 退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { useUserStore } from '@/stores/user'
import { useProjectStore } from '@/stores/project'
import { logout } from '@/api/auth'
import {
  Odometer, Folder, ChatDotSquare, Notebook, Cpu, Files,
  DataBoard, Monitor, FolderOpened, List, Setting,
  Fold, Expand, UserFilled, SwitchButton, ArrowDown,
} from '@element-plus/icons-vue'
import type { Component } from 'vue'

interface MenuChild { path: string; label: string }
interface MenuItem {
  path?: string; label: string; icon?: Component
  group?: string; divider?: string; children?: MenuChild[]
}

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()
const userStore = useUserStore()
const projectStore = useProjectStore()

function switchProject(projectId: number) {
  const p = projectStore.projects.find(x => x.id === projectId)
  if (p) projectStore.setCurrentProject(p)
}

const menuItems: MenuItem[] = [
  { path: '/dashboard', label: '驾驶舱', icon: Odometer },
  { path: '/projects', label: '项目管理', icon: Folder },
  { divider: 'AI 能力', label: '' } as any,
  { path: '/chat', label: '对话工作台', icon: ChatDotSquare },
  { path: '/knowledge', label: '知识库', icon: Notebook },
  {
    group: 'apptainer', label: 'Apptainer', icon: Cpu,
    children: [
      { path: '/apptainer/definitions', label: 'Definition 管理' },
      { path: '/apptainer/build-jobs', label: '构建任务' },
    ],
  },
  { divider: '运维能力', label: '' } as any,
  { path: '/scripts', label: '脚本管理', icon: Files },
  {
    group: 'benchmark', label: '压测', icon: DataBoard,
    children: [
      { path: '/benchmark/scripts', label: '压测脚本' },
      { path: '/benchmark/jobs', label: '压测任务' },
    ],
  },
  { path: '/servers', label: '服务器管理', icon: Monitor },
  { divider: '系统', label: '' } as any,
  { path: '/artifacts', label: '文件产物', icon: FolderOpened },
  { path: '/audit-logs', label: '审计日志', icon: List },
  { path: '/settings', label: '系统设置', icon: Setting },
]

async function handleLogout() {
  try { await logout() } catch { /* ignore */ }
  userStore.clearUser()
  router.push('/login')
}
</script>

<style scoped>
.app-layout { height: 100vh; background: #f0f4f8; }

/* ── Sidebar ── */
.app-sidebar {
  background: #fff; transition: width var(--transition-normal);
  overflow: hidden; display: flex; flex-direction: column;
  border-right: 1px solid #e2e8f0; box-shadow: 1px 0 3px rgba(0,0,0,0.02);
}
.sidebar-header {
  height: var(--header-height); display: flex; align-items: center;
  justify-content: center; gap: 10px; flex-shrink: 0;
  border-bottom: 1px solid #f1f5f9;
}
.sidebar-logo-icon {
  display: inline-flex; align-items: center; justify-content: center;
  width: 30px; height: 30px; border-radius: 7px;
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  color: #fff; font-size: 12px; font-weight: 800; flex-shrink: 0;
}
.sidebar-logo-text { font-size: 18px; font-weight: 700; color: #1e293b; }
.sidebar-scroll { flex: 1; }
.sidebar-menu { border-right: none; background: transparent; }
.sidebar-menu :deep(.el-menu-item),
.sidebar-menu :deep(.el-sub-menu__title) {
  color: #64748b; height: 40px; line-height: 40px; font-size: 13px;
  margin: 2px 8px; width: auto; border-radius: 6px; transition: all 0.2s;
}
.sidebar-menu :deep(.el-menu-item:hover),
.sidebar-menu :deep(.el-sub-menu__title:hover) { background: #f1f5f9; color: #334155; }
.sidebar-menu :deep(.el-menu-item.is-active) {
  color: #6366f1; background: rgba(99,102,241,0.07); font-weight: 500;
}
.sidebar-menu :deep(.el-menu-item.is-active) .el-icon { color: #6366f1; }
.sidebar-menu :deep(.el-sub-menu.is-active>.el-sub-menu__title) { color: #6366f1; }
.sidebar-menu :deep(.el-sub-menu__title .el-icon) { color: #94a3b8; }
.sidebar-menu :deep(.el-menu .el-menu-item) { padding-left: 52px !important; }
.sidebar-menu :deep(.el-menu--collapse .el-menu-item) {
  margin: 2px auto; width: 48px; border-radius: 8px; justify-content: center; padding: 0 !important;
}
.menu-divider {
  padding: 16px 16px 4px; font-size: 10px; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.06em; color: #94a3b8;
}
.sidebar-footer { flex-shrink: 0; display: flex; justify-content: center; padding: 8px; border-top: 1px solid #f1f5f9; }
.collapse-btn { color: #94a3b8; width: 100%; }
.collapse-btn:hover { color: #6366f1; }

/* ── Header ── */
.app-header {
  height: var(--header-height); background: rgba(255,255,255,0.85);
  border-bottom: 1px solid #e2e8f0; backdrop-filter: blur(12px);
  display: flex; align-items: center; justify-content: space-between; padding: 0 24px;
}
:deep(.el-breadcrumb__inner) { color: #94a3b8 !important; font-size: 13px; }
:deep(.el-breadcrumb__inner.is-link) { color: #94a3b8 !important; }
:deep(.el-breadcrumb__item:last-child .el-breadcrumb__inner) { color: #1e293b !important; }
.header-left { display: flex; align-items: center; gap: 12px; }
.header-right { display: flex; align-items: center; }

/* ── Project Badge ── */
.project-badge {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 4px 10px; border-radius: 6px; cursor: pointer;
  font-size: 13px; font-weight: 500; color: #6366f1;
  background: rgba(99,102,241,0.06); transition: background 0.2s;
  white-space: nowrap; max-width: 200px;
}
.project-badge:hover { background: rgba(99,102,241,0.12); }
.project-badge--empty { color: #94a3b8; background: transparent; }
.project-badge--empty:hover { background: #f1f5f9; }

.user-info {
  display: flex; align-items: center; gap: 8px; cursor: pointer;
  padding: 4px 10px; border-radius: 8px; transition: background 0.2s;
}
.user-info:hover { background: rgba(99,102,241,0.1); }
.username { font-size: 13px; color: #1e293b; max-width: 120px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* ── Main ── */
.app-main { background: #f0f4f8; padding: 0; overflow: hidden; }
</style>
