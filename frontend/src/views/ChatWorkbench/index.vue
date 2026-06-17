<template>
  <div class="chat-workbench">
    <!-- Left: Conversation List -->
    <div class="chat-sidebar">
      <div class="sidebar-actions">
        <el-button type="primary" :icon="Plus" class="w-full" @click="createNewConversation">
          新建对话
        </el-button>
      </div>
      <div class="conversation-list">
        <div
          v-for="conv in conversations"
          :key="conv.id"
          class="conversation-item"
          :class="{ active: conv.id === currentConversationId }"
          @click="selectConversation(conv)"
        >
          <div class="conv-info">
            <div class="conv-title truncate">{{ conv.title || '新对话' }}</div>
            <div class="conv-time">{{ formatRelativeTime(conv.created_at) }}</div>
          </div>
          <el-button
            text
            size="small"
            class="conv-delete"
            @click.stop="handleDeleteConversation(conv)"
          >
            <el-icon :size="14"><Delete /></el-icon>
          </el-button>
        </div>
        <el-empty v-if="!conversations.length" description="暂无对话" :image-size="40" />
      </div>
    </div>

    <!-- Middle: Chat Messages -->
    <div class="chat-main">
      <div v-if="!currentConversationId" class="chat-empty">
        <el-empty description="选择或创建一个对话开始" :image-size="80">
          <el-button type="primary" @click="createNewConversation">新建对话</el-button>
        </el-empty>
      </div>
      <template v-else>
        <div class="chat-messages" ref="messageContainer">
          <div v-if="messagesLoading" class="chat-loading">
            <el-icon class="is-loading" :size="20"><Loading /></el-icon>
          </div>
          <ChatMessage
            v-for="msg in messages"
            :key="msg.id"
            :role="msg.role as 'user' | 'assistant'"
            :content="msg.content"
            :time="msg.created_at"
          />
          <div v-if="completing" class="chat-thinking">
            <el-icon class="is-loading" :size="16"><Loading /></el-icon>
            <span>AI 正在思考...</span>
          </div>
        </div>
        <ChatInput
          :loading="completing"
          @send="handleSend"
        />
      </template>
    </div>

    <!-- Right: References + Actions -->
    <div class="chat-references">
      <div class="ref-actions">
        <el-button
          type="primary"
          :icon="Cpu"
          size="small"
          :disabled="!messages.length || generating"
          :loading="generating"
          @click="handleGenerateDef"
          style="width: 100%"
        >
          生成 Apptainer Definition
        </el-button>
      </div>
      <ReferencePanel :references="currentReferences" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Loading, Cpu, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import ChatMessage from '@/components/ChatPanel/ChatMessage.vue'
import ChatInput from '@/components/ChatPanel/ChatInput.vue'
import ReferencePanel from '@/components/ChatPanel/ReferencePanel.vue'
import { getConversations, createConversation, getMessages, complete, deleteConversation } from '@/api/chat'
import { generateDefinition } from '@/api/apptainer'
import { useProjectStore } from '@/stores/project'
import { formatRelativeTime } from '@/utils/date'
import type { Conversation, Message, KnowledgeReference } from '@/types/chat'

const router = useRouter()
const currentConversationId = ref<number | null>(null)
const conversations = ref<Conversation[]>([])
const messages = ref<Message[]>([])
const messagesLoading = ref(false)
const completing = ref(false)
const generating = ref(false)
const currentReferences = ref<KnowledgeReference[]>([])
const messageContainer = ref<HTMLElement>()
const projectStore = useProjectStore()

// AbortController for canceling in-flight requests
let abortController: AbortController | null = null

function scrollToBottom() {
  nextTick(() => {
    messageContainer.value?.scrollTo({
      top: messageContainer.value.scrollHeight,
      behavior: 'smooth',
    })
  })
}

async function fetchConversations() {
  const projectId = projectStore.getCurrentProjectId()
  if (!projectId) {
    ElMessage.warning('请先选择一个项目')
    return
  }
  conversations.value = await getConversations(projectId)
}

function createOptimisticMessage(text: string): Message {
  return {
    id: -Date.now(), // negative = temporary, replaced on refresh
    conversation_id: currentConversationId.value!,
    role: 'user',
    content: text,
    created_at: new Date().toISOString(),
  }
}

async function createNewConversation() {
  const projectId = projectStore.getCurrentProjectId()
  if (!projectId) {
    ElMessage.warning('请先选择一个项目')
    return
  }
  const conv = await createConversation({ project_id: projectId })
  conversations.value.unshift(conv)
  await selectConversation(conv)
}

async function selectConversation(conv: Conversation) {
  currentConversationId.value = conv.id
  currentReferences.value = []
  await loadMessages(conv.id)
}

async function handleDeleteConversation(conv: Conversation) {
  try {
    await ElMessageBox.confirm(`确定删除对话「${conv.title || '新对话'}」吗？`, '确认', {
      type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消',
    })
    await deleteConversation(conv.id)
    conversations.value = conversations.value.filter(c => c.id !== conv.id)
    if (currentConversationId.value === conv.id) {
      currentConversationId.value = null
      messages.value = []
      currentReferences.value = []
    }
    ElMessage.success('对话已删除')
  } catch {
    // cancelled
  }
}

async function loadMessages(conversationId: number) {
  messagesLoading.value = true
  try {
    messages.value = await getMessages(conversationId)
    scrollToBottom()
  } finally {
    messagesLoading.value = false
  }
}

async function handleSend(text: string, useKnowledge: boolean) {
  const projectId = projectStore.getCurrentProjectId()
  if (!projectId || !currentConversationId.value) return
  const conversationId = currentConversationId.value
  const wasFirstMessage = messages.value.length === 0

  // Cancel any previous in-flight request
  abortController?.abort()
  abortController = new AbortController()

  // Add optimistic user message
  const optimisticMsg = createOptimisticMessage(text)
  messages.value.push(optimisticMsg)
  scrollToBottom()

  completing.value = true
  try {
    const result = await complete({
      project_id: projectId,
      conversation_id: conversationId,
      message: text,
      use_knowledge: useKnowledge,
    })

    if (currentConversationId.value !== conversationId) return

    // Replace the temporary user message with persisted user + assistant messages.
    messages.value = await getMessages(conversationId)
    currentReferences.value = result.references || []

    // If first exchange, refresh conversation list to get AI-generated title
    if (wasFirstMessage) {
      await fetchConversations()
    }

    scrollToBottom()
  } catch (e: any) {
    // Remove optimistic message on failure
    messages.value = messages.value.filter(m => m.id !== optimisticMsg.id)
    if (e.name !== 'CanceledError' && !e.handled) {
      ElMessage.error(e.message || '对话请求失败')
    }
  } finally {
    completing.value = false
    abortController = null
  }
}

async function handleGenerateDef() {
  const projectId = projectStore.getCurrentProjectId()
  if (!projectId || !currentConversationId.value) {
    ElMessage.warning('请先选择项目和对话')
    return
  }

  generating.value = true
  try {
    const def = await generateDefinition({
      project_id: projectId,
      conversation_id: currentConversationId.value,
      requirement: '',
      use_knowledge: true,
    })
    ElMessage.success('Definition 生成成功！')
    router.push(`/apptainer/definitions/${def.id}`)
  } catch (e: any) {
    if (!e.handled) ElMessage.error(e.message || '生成失败')
  } finally {
    generating.value = false
  }
}

onMounted(fetchConversations)
onUnmounted(() => abortController?.abort())
</script>

<style scoped>
.chat-workbench {
  height: 100%;
  display: flex;
  overflow: hidden;
}

/* --- Sidebar --- */
.chat-sidebar {
  width: 260px;
  border-right: 1px solid var(--border-color);
  background: var(--card-bg);
  display: flex;
  flex-direction: column;
}

.sidebar-actions {
  padding: 12px;
  border-bottom: 1px solid var(--border-color);
}

.conversation-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.conversation-item {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 10px 8px 10px 12px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  margin-bottom: 2px;
  transition: background var(--transition-fast);
}

.conversation-item:hover .conv-delete {
  opacity: 1;
}

.conv-info {
  flex: 1;
  min-width: 0;
}

.conv-delete {
  opacity: 0;
  flex-shrink: 0;
  color: var(--text-secondary);
  transition: opacity var(--transition-fast);
  padding: 4px;
}

.conv-delete:hover {
  color: var(--danger-color);
}

.conversation-item:hover {
  background: var(--border-light);
}

.conversation-item.active {
  background: var(--primary-bg);
  color: var(--primary-color);
}

.conv-title {
  font-size: 14px;
  font-weight: 500;
}

.conv-time {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 4px;
}

/* --- Main --- */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
}

.chat-loading,
.chat-thinking {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  padding: 16px;
}

.chat-thinking span {
  color: var(--text-secondary);
  font-size: 14px;
}

/* --- References + Actions --- */
.chat-references {
  width: 280px;
  border-left: 1px solid var(--border-color);
  background: var(--card-bg);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.ref-actions {
  padding: 12px;
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
}

.ref-actions + .reference-panel {
  flex: 1;
  overflow-y: auto;
}
</style>
