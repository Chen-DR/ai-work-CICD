import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login/index.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    component: () => import('@/components/AppLayout/index.vue'),
    meta: { requiresAuth: true },
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard/index.vue'),
        meta: { title: '驾驶舱', icon: 'Odometer', hideTopBar: true },
      },
      {
        path: 'projects',
        name: 'Projects',
        component: () => import('@/views/Projects/index.vue'),
        meta: { title: '项目管理', icon: 'Folder' },
      },
      {
        path: 'chat',
        name: 'ChatWorkbench',
        component: () => import('@/views/ChatWorkbench/index.vue'),
        meta: { title: '对话工作台', icon: 'ChatDotSquare' },
      },
      {
        path: 'knowledge',
        name: 'KnowledgeBase',
        component: () => import('@/views/KnowledgeBase/index.vue'),
        meta: { title: '知识库', icon: 'Notebook' },
      },
      {
        path: 'apptainer/definitions',
        name: 'ApptainerDefinitionList',
        component: () => import('@/views/Apptainer/DefinitionList.vue'),
        meta: { title: 'Definition 列表', icon: 'Document' },
      },
      {
        path: 'apptainer/definitions/:id',
        name: 'ApptainerDefinitionEditor',
        component: () => import('@/views/Apptainer/DefinitionEditor.vue'),
        meta: { title: 'Definition 编辑器', icon: 'Edit' },
      },
      {
        path: 'apptainer/build-jobs',
        name: 'ApptainerBuildJobList',
        component: () => import('@/views/Apptainer/BuildJobList.vue'),
        meta: { title: '构建任务', icon: 'Cpu' },
      },
      {
        path: 'apptainer/build-jobs/:id',
        name: 'ApptainerBuildJobDetail',
        component: () => import('@/views/Apptainer/BuildJobDetail.vue'),
        meta: { title: '构建详情', icon: 'InfoFilled' },
      },
      {
        path: 'benchmark/scripts',
        name: 'BenchmarkScriptList',
        component: () => import('@/views/Benchmark/ScriptList.vue'),
        meta: { title: '压测脚本', icon: 'Files' },
      },
      {
        path: 'benchmark/scripts/upload',
        name: 'BenchmarkScriptUpload',
        component: () => import('@/views/Benchmark/ScriptUpload.vue'),
        meta: { title: '上传脚本', icon: 'Upload' },
      },
      {
        path: 'benchmark/jobs',
        name: 'BenchmarkJobList',
        component: () => import('@/views/Benchmark/JobList.vue'),
        meta: { title: '压测任务', icon: 'DataBoard' },
      },
      {
        path: 'benchmark/jobs/:id',
        name: 'BenchmarkJobDetail',
        component: () => import('@/views/Benchmark/JobDetail.vue'),
        meta: { title: '压测详情', icon: 'InfoFilled' },
      },
      {
        path: 'servers',
        name: 'Servers',
        component: () => import('@/views/Servers/ServerList.vue'),
        meta: { title: '服务器管理', icon: 'Monitor' },
      },
      {
        path: 'servers/new',
        name: 'ServerForm',
        component: () => import('@/views/Servers/ServerForm.vue'),
        meta: { title: '新增服务器', icon: 'Plus' },
      },
      {
        path: 'servers/:id',
        name: 'ServerDetail',
        component: () => import('@/views/Servers/ServerDetail.vue'),
        meta: { title: '服务器详情', icon: 'InfoFilled' },
      },
      {
        path: 'artifacts',
        name: 'Artifacts',
        component: () => import('@/views/Artifacts/index.vue'),
        meta: { title: '文件产物', icon: 'FolderOpened' },
      },
      {
        path: 'audit-logs',
        name: 'AuditLogs',
        component: () => import('@/views/AuditLogs/index.vue'),
        meta: { title: '审计日志', icon: 'List' },
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/Settings/index.vue'),
        meta: { title: '系统设置', icon: 'Setting' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  const userStore = useUserStore()

  if (to.meta.requiresAuth !== false && !userStore.isLoggedIn()) {
    next('/login')
  } else if (to.path === '/login' && userStore.isLoggedIn()) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
