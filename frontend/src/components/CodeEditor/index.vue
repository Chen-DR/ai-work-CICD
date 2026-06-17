<template>
  <div class="code-editor">
    <div class="editor-header" v-if="title">
      <span class="editor-title">{{ title }}</span>
      <div class="editor-actions">
        <el-button v-if="readonly" size="small" type="primary" @click="$emit('edit')">
          <el-icon><Edit /></el-icon> 编辑
        </el-button>
        <el-button v-if="!readonly" size="small" type="success" @click="$emit('save')" :loading="saving">
          <el-icon><Check /></el-icon> 保存
        </el-button>
        <el-button v-if="!readonly" size="small" @click="$emit('cancel')">
          取消
        </el-button>
        <el-button size="small" @click="handleCopy">
          <el-icon><CopyDocument /></el-icon> {{ copied ? '已复制' : '复制' }}
        </el-button>
      </div>
    </div>

    <div class="editor-surface" :style="{ minHeight }">
      <pre ref="highlightRef" class="highlight-layer" aria-hidden="true"><code><span
        v-for="(line, lineIndex) in highlightedLines"
        :key="lineIndex"
        class="code-line"
      ><template v-if="line.length"><span
        v-for="(token, tokenIndex) in line"
        :key="tokenIndex"
        :class="token.className"
      >{{ token.text }}</span></template><template v-else>&nbsp;</template>{{ lineIndex < highlightedLines.length - 1 ? '\n' : '' }}</span></code></pre>
      <textarea
        ref="editorRef"
        :value="modelValue"
        @input="handleInput"
        @keydown="$emit('keydown', $event)"
        @scroll="syncScroll"
        class="editor-textarea"
        :readonly="readonly"
        spellcheck="false"
        :style="{ minHeight }"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { Edit, Check, CopyDocument } from '@element-plus/icons-vue'

type Token = { text: string; className?: string }

const props = withDefaults(defineProps<{
  modelValue: string
  readonly?: boolean
  title?: string
  saving?: boolean
  minHeight?: string
  language?: 'shell' | 'python' | 'apptainer' | string
}>(), {
  minHeight: '320px',
  language: 'shell',
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
  save: []
  edit: []
  cancel: []
  keydown: [event: KeyboardEvent]
}>()

const copied = ref(false)
const editorRef = ref<HTMLTextAreaElement>()
const highlightRef = ref<HTMLPreElement>()

const shellKeywords = new Set([
  'if', 'then', 'else', 'elif', 'fi', 'for', 'while', 'do', 'done', 'case', 'esac',
  'function', 'local', 'export', 'readonly', 'return', 'exit', 'set', 'source',
])
const pythonKeywords = new Set([
  'and', 'as', 'assert', 'break', 'class', 'continue', 'def', 'elif', 'else', 'except',
  'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'not',
  'or', 'pass', 'raise', 'return', 'try', 'while', 'with', 'yield',
])

const highlightedLines = computed(() => {
  const lines = (props.modelValue || '').split('\n')
  return lines.map(line => highlightLine(line))
})

function highlightLine(line: string): Token[] {
  if (props.language === 'python') return highlightGeneric(line, pythonKeywords, /#.*/)
  if (props.language === 'apptainer') return highlightApptainer(line)
  return highlightGeneric(line, shellKeywords, /#.*/)
}

function highlightApptainer(line: string): Token[] {
  if (/^\s*%[a-zA-Z_]+/.test(line)) {
    const match = line.match(/^(\s*)(%[a-zA-Z_]+)(.*)$/)
    if (!match) return [{ text: line }]
    return [
      { text: match[1] },
      { text: match[2], className: 'tok-directive' },
      ...highlightGeneric(match[3], shellKeywords, /#.*/),
    ]
  }
  if (/^\s*(Bootstrap|From|Stage):/.test(line)) {
    const match = line.match(/^(\s*)([A-Za-z]+:)(.*)$/)
    if (!match) return [{ text: line }]
    return [
      { text: match[1] },
      { text: match[2], className: 'tok-directive' },
      { text: match[3], className: 'tok-string' },
    ]
  }
  return highlightGeneric(line, shellKeywords, /#.*/)
}

function highlightGeneric(line: string, keywords: Set<string>, commentPattern: RegExp): Token[] {
  const comment = line.match(commentPattern)
  const source = comment && comment.index !== undefined ? line.slice(0, comment.index) : line
  const tokens = tokenizeSource(source, keywords)
  if (comment && comment.index !== undefined) {
    tokens.push({ text: line.slice(comment.index), className: 'tok-comment' })
  }
  return tokens
}

function tokenizeSource(source: string, keywords: Set<string>): Token[] {
  const tokens: Token[] = []
  const pattern = /("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|\b\d+(?:\.\d+)?\b|\$[A-Za-z_][A-Za-z0-9_]*|\b[A-Za-z_][A-Za-z0-9_]*\b)/g
  let lastIndex = 0
  for (const match of source.matchAll(pattern)) {
    const index = match.index || 0
    if (index > lastIndex) tokens.push({ text: source.slice(lastIndex, index) })
    const text = match[0]
    if (text.startsWith('"') || text.startsWith("'")) {
      tokens.push({ text, className: 'tok-string' })
    } else if (text.startsWith('$')) {
      tokens.push({ text, className: 'tok-variable' })
    } else if (/^\d/.test(text)) {
      tokens.push({ text, className: 'tok-number' })
    } else if (keywords.has(text)) {
      tokens.push({ text, className: 'tok-keyword' })
    } else {
      tokens.push({ text })
    }
    lastIndex = index + text.length
  }
  if (lastIndex < source.length) tokens.push({ text: source.slice(lastIndex) })
  return tokens
}

function handleInput(e: Event) {
  emit('update:modelValue', (e.target as HTMLTextAreaElement).value)
}

function syncScroll() {
  if (!editorRef.value || !highlightRef.value) return
  highlightRef.value.scrollTop = editorRef.value.scrollTop
  highlightRef.value.scrollLeft = editorRef.value.scrollLeft
}

async function handleCopy() {
  try {
    await navigator.clipboard.writeText(props.modelValue)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  } catch {
    const textarea = editorRef.value
    if (textarea) {
      textarea.select()
      document.execCommand('copy')
      copied.value = true
      setTimeout(() => { copied.value = false }, 2000)
    }
  }
}
</script>

<style scoped>
.code-editor {
  border: 1px solid var(--border-color);
  border-radius: 6px;
  overflow: hidden;
  background: #1e1e1e;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f8f9fa;
  border-bottom: 1px solid var(--border-color);
}

.editor-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-regular);
}

.editor-actions {
  display: flex;
  gap: 8px;
}

.editor-surface {
  position: relative;
  min-height: 320px;
  background: #1e1e1e;
}

.highlight-layer,
.editor-textarea {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  min-height: inherit;
  margin: 0;
  padding: 16px;
  border: none;
  outline: none;
  overflow: auto;
  white-space: pre;
  word-break: normal;
  overflow-wrap: normal;
  tab-size: 4;
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
  line-height: 1.6;
}

.highlight-layer {
  color: #d4d4d4;
  pointer-events: none;
}

.editor-textarea {
  resize: vertical;
  background: transparent;
  color: transparent;
  caret-color: #ffffff;
  -webkit-text-fill-color: transparent;
}

.editor-textarea::selection {
  background: rgba(86, 156, 214, 0.35);
}

.editor-textarea:read-only {
  cursor: default;
}

.code-line {
  min-height: 1.6em;
}

.tok-keyword,
.tok-directive {
  color: #c586c0;
}

.tok-string {
  color: #ce9178;
}

.tok-comment {
  color: #6a9955;
}

.tok-variable {
  color: #9cdcfe;
}

.tok-number {
  color: #b5cea8;
}
</style>
