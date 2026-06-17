<template>
  <div class="page-container scripts-page">
    <div class="page-header">
      <h2>脚本管理</h2>
      <el-upload
        drag
        :auto-upload="false"
        :show-file-list="false"
        :on-change="handleFileChange"
        accept=".sh,.bash,.py"
        class="upload-inline"
      >
        <el-button type="primary" :icon="Upload">上传脚本</el-button>
      </el-upload>
    </div>

    <div class="script-workbench">
      <section class="script-list">
        <el-table :data="scripts" v-loading="loading" height="100%" empty-text="暂无脚本" highlight-current-row>
          <el-table-column prop="name" label="脚本" min-width="150">
            <template #default="{ row }">
              <el-button link type="primary" @click="selectScript(row)">{{ row.name }}</el-button>
            </template>
          </el-table-column>
          <el-table-column prop="language" label="类型" width="82">
            <template #default="{ row }">
              <el-tag size="small" :type="row.language === 'python' ? 'success' : 'info'">
                {{ row.language === 'python' ? 'Python' : 'Shell' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="142" fixed="right">
            <template #default="{ row }">
              <el-button size="small" :icon="View" @click="selectScript(row)" />
              <el-button size="small" type="danger" :icon="Delete" @click="handleDelete(row)" />
            </template>
          </el-table-column>
        </el-table>
      </section>

      <section class="script-editor">
        <div v-if="!selected" class="empty-editor">
          <el-empty description="请选择或上传脚本" />
        </div>
        <template v-else>
          <div class="editor-header">
            <div class="editor-title">
              <el-input v-model="editForm.name" class="name-input" placeholder="脚本名称" />
              <el-input v-model="editForm.description" class="desc-input" placeholder="描述（可选）" />
            </div>
            <el-button :icon="DocumentChecked" :disabled="!dirty" @click="handleSave">保存</el-button>
          </div>
          <CodeEditor
            v-model="editForm.content"
            class="code-editor"
            :language="selected.language"
            min-height="460px"
            @keydown.ctrl.s.prevent="handleSave"
          />
        </template>
      </section>

      <aside class="run-panel">
        <div class="panel-title">执行配置</div>
        <el-form label-position="top" class="run-form">
          <el-form-item label="目标服务器">
            <el-select v-model="runForm.serverId" placeholder="请选择服务器" style="width: 100%" @change="handleServerChange">
              <el-option
                v-for="server in servers"
                :key="server.id"
                :label="serverOptionLabel(server)"
                :value="server.id"
                :disabled="server.status === 'DISABLED'"
              >
                <div class="server-option">
                  <span class="status-dot" :class="server.status === 'ACTIVE' ? 'online' : 'offline'" />
                  <span class="server-main">{{ server.name }} · {{ server.host }}</span>
                  <span class="server-load">{{ serverLoadText(server) }}</span>
                </div>
              </el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="工作目录">
            <el-input v-model="runForm.cwd" placeholder="/opt/software/project" />
            <div v-if="recentCwds.length" class="quick-row">
              <span>最近：</span>
              <el-button v-for="cwd in recentCwds" :key="cwd" link type="primary" @click="runForm.cwd = cwd">
                {{ cwd }}
              </el-button>
            </div>
            <div v-if="scriptAllowedDirs.length" class="quick-row">
              <span>允许：</span>
              <el-button v-for="dir in scriptAllowedDirs" :key="dir.id" link type="primary" @click="runForm.cwd = dir.path">
                {{ dir.path }}
              </el-button>
            </div>
          </el-form-item>

          <el-form-item label="脚本参数">
            <div class="args-row">
              <el-input v-model="runForm.args" placeholder="--env production --jobs 15" />
              <el-button :icon="CollectionTag" @click="saveCurrentPreset" />
            </div>
          </el-form-item>

          <div class="preset-list">
            <div v-if="!presets.length" class="preset-empty">暂无参数预设</div>
            <div
              v-for="preset in presets"
              :key="preset.id"
              class="preset-item"
              :class="{ active: activePresetId === preset.id }"
              @click="loadPreset(preset)"
            >
              <div class="preset-main">
                <strong>{{ preset.name }}</strong>
                <span>{{ preset.args }}</span>
              </div>
              <div class="preset-meta">
                <span>{{ formatTime(preset.last_used_at || preset.created_at) }}</span>
                <el-button link type="danger" :icon="Delete" @click.stop="removePreset(preset.id)" />
              </div>
            </div>
          </div>

          <el-form-item label="超时时间（秒）">
            <el-input-number v-model="runForm.timeout" :min="1" :max="86400" style="width: 100%" />
          </el-form-item>

          <el-form-item label="执行用户">
            <el-select v-model="runForm.runAs" filterable allow-create default-first-option style="width: 100%">
              <el-option v-for="user in runAsOptions" :key="user" :label="user" :value="user" />
            </el-select>
            <div class="quick-row">
              <span v-if="selectedServer?.allow_script_root">该服务器已允许 root 执行</span>
              <span v-else>如需 root，请到服务器详情开启脚本 root 执行</span>
            </div>
          </el-form-item>

          <el-button
            v-if="isTaskRunning"
            type="danger"
            :icon="CircleClose"
            class="run-button"
            @click="handleTerminate"
          >
            终止
          </el-button>
          <el-button
            v-else
            type="primary"
            :icon="VideoPlay"
            class="run-button"
            :loading="executing"
            :disabled="!selected"
            @click="handleExecute"
          >
            执行
          </el-button>
        </el-form>
      </aside>
    </div>

    <section class="log-panel">
      <div class="log-toolbar">
        <span>执行日志</span>
        <div class="log-actions">
          <el-tag v-if="runningTask" size="small" :type="taskTagType">{{ runningTask.status }}</el-tag>
          <el-button size="small" @click="clearLogs">清空日志</el-button>
          <el-button size="small" @click="copyLogs">复制全部日志</el-button>
          <el-checkbox v-model="autoScroll" label="自动滚动" size="small" />
        </div>
      </div>
      <div ref="logBodyRef" class="log-body">
        <div v-if="!logEvents.length" class="log-placeholder">暂无执行日志</div>
        <div
          v-for="(event, index) in logEvents"
          :key="index"
          class="log-line"
          :class="[`log-${event.type}`, { ok: event.type === 'exit' && event.code === 0 }]"
        >
          <span class="log-ts">{{ event.ts || '--:--:--' }}</span>
          <span v-if="event.type === 'exit'" class="log-message">
            Exit code: {{ event.code }}
          </span>
          <span v-else class="log-message">{{ event.line || event.command?.join(' ') }}</span>
        </div>
      </div>
    </section>

    <el-dialog v-model="uploadVisible" title="上传脚本" width="520px">
      <el-form label-position="top">
        <el-form-item label="文件">{{ uploadForm.file?.name || '-' }}</el-form-item>
        <el-form-item label="脚本名称">
          <el-input v-model="uploadForm.name" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="uploadForm.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadVisible = false">取消</el-button>
        <el-button type="primary" :loading="uploading" @click="handleUpload">上传</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { CircleClose, CollectionTag, Delete, DocumentChecked, Upload, VideoPlay, View } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox, type UploadFile } from 'element-plus'
import {
  createScriptPreset,
  deleteManagedScript,
  deleteScriptPreset,
  executeManagedScript,
  getManagedScript,
  getManagedScripts,
  getScriptPresets,
  getScriptRecentCwds,
  scriptTaskLogStreamUrl,
  terminateScriptTask,
  updateManagedScript,
  uploadManagedScript,
  useScriptPreset,
} from '@/api/scripts'
import { getServerAllowedDirs, getServers } from '@/api/servers'
import CodeEditor from '@/components/CodeEditor/index.vue'
import { useProjectStore } from '@/stores/project'
import type { ManagedScript, ScriptExecutionTask, ScriptLogEvent, ScriptParamPreset } from '@/types/scripts'
import type { Server, ServerAllowedDir } from '@/types/server'

const projectStore = useProjectStore()
const scripts = ref<ManagedScript[]>([])
const servers = ref<Server[]>([])
const allowedDirs = ref<ServerAllowedDir[]>([])
const presets = ref<ScriptParamPreset[]>([])
const recentCwds = ref<string[]>([])
const selected = ref<ManagedScript | null>(null)
const loading = ref(false)
const uploading = ref(false)
const executing = ref(false)
const uploadVisible = ref(false)
const autoScroll = ref(true)
const logBodyRef = ref<HTMLElement>()
const logEvents = ref<ScriptLogEvent[]>([])
const runningTask = ref<ScriptExecutionTask | null>(null)
const activePresetId = ref<number | null>(null)
let streamAbort: AbortController | null = null

const uploadForm = reactive({
  file: null as File | null,
  name: '',
  description: '',
})

const editForm = reactive({
  name: '',
  description: '',
  content: '',
})

const originalContent = ref('')
const originalName = ref('')
const originalDescription = ref('')

const runForm = reactive({
  serverId: undefined as number | undefined,
  cwd: '/opt',
  args: '',
  timeout: 3600,
  runAs: 'slurm',
})

const dirty = computed(() => (
  editForm.name !== originalName.value ||
  editForm.description !== originalDescription.value ||
  editForm.content !== originalContent.value
))

const isTaskRunning = computed(() => runningTask.value?.status === 'RUNNING' || runningTask.value?.status === 'PENDING')
const selectedServer = computed(() => servers.value.find(item => item.id === runForm.serverId) || null)
const scriptAllowedDirs = computed(() => allowedDirs.value.filter(dir => ['script', 'general'].includes(dir.purpose)))

const runAsOptions = computed(() => {
  const values = new Set(['slurm', 'admin'])
  const server = selectedServer.value
  if (server?.username && server.username !== 'root') values.add(server.username)
  if (server?.allow_script_root) values.add('root')
  if (runForm.runAs) values.add(runForm.runAs)
  return Array.from(values)
})

const taskTagType = computed(() => {
  if (!runningTask.value) return 'info'
  if (runningTask.value.status === 'SUCCESS') return 'success'
  if (['FAILED', 'TIMEOUT'].includes(runningTask.value.status)) return 'danger'
  if (runningTask.value.status === 'CANCELLED') return 'warning'
  return 'primary'
})

watch(logEvents, async () => {
  if (!autoScroll.value) return
  await nextTick()
  if (logBodyRef.value) logBodyRef.value.scrollTop = logBodyRef.value.scrollHeight
}, { deep: true })

async function fetchScripts() {
  loading.value = true
  try {
    scripts.value = await getManagedScripts(projectStore.getCurrentProjectId() || undefined)
  } finally {
    loading.value = false
  }
}

async function fetchServers() {
  const projectId = projectStore.getCurrentProjectId()
  servers.value = await getServers(projectId || undefined)
  if (!runForm.serverId && servers.value.length) {
    runForm.serverId = servers.value[0].id
    if (servers.value[0].username !== 'root') runForm.runAs = servers.value[0].username
    await handleServerChange(runForm.serverId)
  }
}

async function refreshScriptAuxiliary(scriptId: number) {
  presets.value = await getScriptPresets(scriptId)
  recentCwds.value = await getScriptRecentCwds(scriptId)
  activePresetId.value = null
}

async function handleServerChange(serverId?: number) {
  allowedDirs.value = []
  if (!serverId) return
  const server = servers.value.find(item => item.id === serverId)
  if (server?.username && server.username !== 'root') runForm.runAs = server.username
  if (server?.username === 'root' && server.allow_script_root) runForm.runAs = 'root'
  if (runForm.runAs === 'root' && !server?.allow_script_root) {
    runForm.runAs = server?.username && server.username !== 'root' ? server.username : 'slurm'
  }
  allowedDirs.value = await getServerAllowedDirs(serverId)
  if (scriptAllowedDirs.value.length && (!runForm.cwd || runForm.cwd === '/opt')) {
    runForm.cwd = scriptAllowedDirs.value[0].path
  }
}

async function selectScript(script: ManagedScript) {
  const detail = await getManagedScript(script.id)
  selected.value = detail
  editForm.name = detail.name
  editForm.description = detail.description
  editForm.content = detail.content || ''
  originalName.value = detail.name
  originalDescription.value = detail.description
  originalContent.value = detail.content || ''
  await refreshScriptAuxiliary(detail.id)
}

function handleFileChange(file: UploadFile) {
  if (!file.raw) return
  uploadForm.file = file.raw
  uploadForm.name = file.name.replace(/\.(sh|bash|py)$/i, '')
  uploadForm.description = ''
  uploadVisible.value = true
}

async function handleUpload() {
  const projectId = projectStore.getCurrentProjectId()
  if (!projectId) {
    ElMessage.warning('请先选择项目')
    return
  }
  if (!uploadForm.file) return
  uploading.value = true
  try {
    const script = await uploadManagedScript(projectId, uploadForm.name, uploadForm.file, uploadForm.description)
    ElMessage.success('上传成功')
    uploadVisible.value = false
    await fetchScripts()
    await selectScript(script)
  } finally {
    uploading.value = false
  }
}

async function handleSave() {
  if (!selected.value || !dirty.value) return
  await ElMessageBox.confirm('保存当前脚本修改吗？', '确认', { type: 'warning' })
  const updated = await updateManagedScript(selected.value.id, {
    name: editForm.name,
    description: editForm.description,
    content: editForm.content,
  })
  ElMessage.success('保存成功')
  await fetchScripts()
  await selectScript(updated)
}

async function handleDelete(script: ManagedScript) {
  await ElMessageBox.confirm(`确定删除脚本「${script.name}」吗？`, '确认', { type: 'warning' })
  await deleteManagedScript(script.id)
  ElMessage.success('删除成功')
  if (selected.value?.id === script.id) {
    selected.value = null
    presets.value = []
    recentCwds.value = []
  }
  await fetchScripts()
}

async function saveCurrentPreset() {
  if (!selected.value) return
  if (!runForm.args.trim()) {
    ElMessage.warning('请先输入脚本参数')
    return
  }
  const { value } = await ElMessageBox.prompt('请输入预设名称', '保存参数预设', {
    inputPlaceholder: '生产环境',
    inputPattern: /^.{1,64}$/,
    inputErrorMessage: '名称不能为空且不能超过 64 个字符',
  })
  const preset = await createScriptPreset(selected.value.id, { name: value, args: runForm.args })
  activePresetId.value = preset.id
  presets.value = await getScriptPresets(selected.value.id)
  ElMessage.success('预设已保存')
}

async function loadPreset(preset: ScriptParamPreset) {
  if (!selected.value) return
  runForm.args = preset.args
  activePresetId.value = preset.id
  await useScriptPreset(selected.value.id, preset.id)
  presets.value = await getScriptPresets(selected.value.id)
}

async function removePreset(presetId: number) {
  if (!selected.value) return
  await ElMessageBox.confirm('确定删除该参数预设吗？', '确认', { type: 'warning' })
  await deleteScriptPreset(selected.value.id, presetId)
  if (activePresetId.value === presetId) activePresetId.value = null
  presets.value = await getScriptPresets(selected.value.id)
  ElMessage.success('预设已删除')
}

async function handleExecute() {
  if (!selected.value) return
  if (!runForm.serverId) {
    ElMessage.warning('请选择目标服务器')
    return
  }
  executing.value = true
  try {
    const task = await executeManagedScript(selected.value.id, {
      server_id: runForm.serverId,
      cwd: runForm.cwd,
      args: runForm.args,
      timeout: runForm.timeout,
      run_as: runForm.runAs,
    })
    runningTask.value = task
    logEvents.value = []
    await refreshScriptAuxiliary(selected.value.id)
    startLogStream(task.task_id)
  } finally {
    executing.value = false
  }
}

async function startLogStream(taskId: string) {
  streamAbort?.abort()
  streamAbort = new AbortController()
  try {
    const token = localStorage.getItem('token')
    const response = await fetch(scriptTaskLogStreamUrl(taskId), {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      signal: streamAbort.signal,
    })
    if (!response.body) return
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    while (true) {
      const { value, done } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const chunks = buffer.split('\n\n')
      buffer = chunks.pop() || ''
      for (const chunk of chunks) {
        const line = chunk.split('\n').find(item => item.startsWith('data: '))
        if (!line) continue
        const event = JSON.parse(line.slice(6)) as ScriptLogEvent
        logEvents.value.push(event)
        if (event.type === 'exit' && runningTask.value) {
          runningTask.value.status = event.code === 0 ? 'SUCCESS' : 'FAILED'
          runningTask.value.exit_code = event.code ?? null
        }
      }
    }
  } catch (error) {
    if ((error as Error).name !== 'AbortError') ElMessage.error('日志流连接中断')
  }
}

async function handleTerminate() {
  if (!runningTask.value) return
  await terminateScriptTask(runningTask.value.task_id)
  runningTask.value.status = 'CANCELLED'
  streamAbort?.abort()
  ElMessage.success('已终止')
}

function clearLogs() {
  logEvents.value = []
}

async function copyLogs() {
  const text = logEvents.value.map(event => {
    if (event.type === 'exit') return `${event.ts} Exit code: ${event.code}`
    return `${event.ts} ${event.line || event.command?.join(' ')}`
  }).join('\n')
  await navigator.clipboard.writeText(text)
  ElMessage.success('已复制')
}

function serverOptionLabel(server: Server) {
  return `${server.name}（${server.host}:${server.port}）${serverLoadText(server)}`
}

function serverLoadText(server: Server) {
  if (!server.metrics) return '负载未知'
  return `CPU ${server.metrics.cpu_percent.toFixed(0)}% · MEM ${server.metrics.mem_percent.toFixed(0)}%`
}

function formatTime(value: string) {
  if (!value) return '-'
  return new Date(value).toLocaleString()
}

onMounted(() => {
  fetchScripts()
  fetchServers()
})
onBeforeUnmount(() => streamAbort?.abort())
</script>

<style scoped>
.scripts-page {
  display: flex;
  flex-direction: column;
  min-height: 100%;
}

.upload-inline :deep(.el-upload-dragger) {
  border: 0;
  padding: 0;
  background: transparent;
}

.script-workbench {
  display: grid;
  grid-template-columns: minmax(260px, 28%) minmax(420px, 1fr) 360px;
  gap: 16px;
  min-height: 0;
  flex: 1;
}

.script-list,
.script-editor,
.run-panel,
.log-panel {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  min-height: 0;
}

.script-list {
  overflow: hidden;
}

.script-editor {
  display: flex;
  flex-direction: column;
  padding: 12px;
}

.empty-editor {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.editor-title {
  display: grid;
  grid-template-columns: minmax(160px, 260px) 1fr;
  gap: 8px;
  flex: 1;
}

.code-editor {
  flex: 1;
}

.run-panel {
  padding: 14px;
  overflow-y: auto;
}

.panel-title {
  font-size: 15px;
  font-weight: 700;
  margin-bottom: 12px;
  color: #1e293b;
}

.run-form :deep(.el-form-item) {
  margin-bottom: 14px;
}

.server-option {
  display: grid;
  grid-template-columns: 10px 1fr auto;
  align-items: center;
  gap: 8px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ef4444;
}

.status-dot.online {
  background: #22c55e;
}

.server-main,
.server-load {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.server-load {
  color: #64748b;
  font-size: 12px;
}

.quick-row {
  margin-top: 6px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
  color: #64748b;
  font-size: 12px;
  line-height: 1.4;
}

.args-row {
  display: grid;
  grid-template-columns: 1fr 32px;
  gap: 8px;
  width: 100%;
}

.preset-list {
  display: grid;
  gap: 8px;
  margin: -4px 0 14px;
}

.preset-empty {
  color: #94a3b8;
  font-size: 12px;
}

.preset-item {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
  padding: 8px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  cursor: pointer;
}

.preset-item.active {
  border-color: #409eff;
  background: #ecf5ff;
}

.preset-main {
  min-width: 0;
  display: grid;
  gap: 3px;
}

.preset-main span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #64748b;
  font-size: 12px;
}

.preset-meta {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #94a3b8;
  font-size: 12px;
}

.run-button {
  width: 100%;
}

.log-panel {
  margin-top: 16px;
  overflow: hidden;
}

.log-toolbar {
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 12px;
  border-bottom: 1px solid #e2e8f0;
  font-size: 13px;
  font-weight: 600;
}

.log-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.log-body {
  height: 240px;
  overflow-y: auto;
  background: #1e1e1e;
  padding: 12px 16px;
  font-family: "Courier New", Courier, monospace;
  font-size: 12px;
  line-height: 1.6;
}

.log-placeholder {
  color: #94a3b8;
}

.log-line {
  display: flex;
  gap: 12px;
  white-space: pre-wrap;
  word-break: break-word;
}

.log-ts {
  color: #64748b;
  flex: 0 0 64px;
}

.log-message {
  color: #d4d4d4;
}

.log-stderr .log-message,
.log-exit .log-message {
  color: #f87171;
}

.log-exit.ok .log-message {
  color: #4ade80;
}

.log-meta .log-message {
  color: #93c5fd;
}

@media (max-width: 1280px) {
  .script-workbench {
    grid-template-columns: minmax(250px, 32%) 1fr;
  }

  .run-panel {
    grid-column: 1 / -1;
  }
}

@media (max-width: 900px) {
  .script-workbench {
    grid-template-columns: 1fr;
  }

  .script-list {
    height: 260px;
  }

  .editor-header,
  .editor-title {
    grid-template-columns: 1fr;
    flex-direction: column;
  }
}
</style>
