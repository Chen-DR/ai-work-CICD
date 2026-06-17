<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <div class="login-logo">
          <span class="logo-icon">AI</span>
        </div>
        <h1 class="login-title">AI-Ops 平台</h1>
        <p class="login-subtitle">容器打包与服务器压测管理平台</p>
      </div>
      <div class="auth-switch">
        <el-segmented v-model="mode" :options="modeOptions" />
      </div>
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        @keyup.enter="handleSubmit"
        size="large"
      >
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名"
            :prefix-icon="User"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        <template v-if="mode === 'register'">
          <el-form-item prop="confirm_password">
            <el-input
              v-model="form.confirm_password"
              type="password"
              placeholder="确认密码"
              :prefix-icon="Lock"
              show-password
            />
          </el-form-item>
          <el-form-item prop="display_name">
            <el-input
              v-model="form.display_name"
              placeholder="显示名称（可选）"
              :prefix-icon="User"
            />
          </el-form-item>
        </template>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleSubmit" class="login-btn">
            {{ buttonText }}
          </el-button>
        </el-form-item>
      </el-form>
      <div v-if="error" class="login-error">
        <el-alert :title="error" type="error" show-icon :closable="false" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, reactive, watch } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock } from '@element-plus/icons-vue'
import { login, register } from '@/api/auth'
import { useUserStore } from '@/stores/user'
import type { FormInstance } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref<FormInstance>()
const loading = ref(false)
const error = ref('')
const mode = ref<'login' | 'register'>('login')
const modeOptions = [
  { label: '登录', value: 'login' },
  { label: '注册', value: 'register' },
]

const form = reactive({
  username: '',
  password: '',
  confirm_password: '',
  display_name: '',
})

const validateConfirmPassword = (_rule: any, value: string, callback: (error?: Error) => void) => {
  if (mode.value !== 'register') {
    callback()
    return
  }
  if (!value) {
    callback(new Error('请再次输入密码'))
    return
  }
  if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
    return
  }
  callback()
}

const validatePassword = (_rule: any, value: string, callback: (error?: Error) => void) => {
  if (!value) {
    callback(new Error('请输入密码'))
    return
  }
  if (mode.value === 'register' && value.length < 6) {
    callback(new Error('密码至少 6 位'))
    return
  }
  callback()
}

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ validator: validatePassword, trigger: 'blur' }],
  confirm_password: [{ validator: validateConfirmPassword, trigger: 'blur' }],
  display_name: [{ max: 128, message: '显示名称不能超过 128 个字符', trigger: 'blur' }],
}

const buttonText = computed(() => {
  if (loading.value) return mode.value === 'login' ? '登录中...' : '注册中...'
  return mode.value === 'login' ? '登 录' : '注 册'
})

watch(mode, () => {
  error.value = ''
  formRef.value?.clearValidate()
})

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  error.value = ''
  try {
    const result = mode.value === 'login'
      ? await login({ username: form.username, password: form.password })
      : await register({
          username: form.username,
          password: form.password,
          confirm_password: form.confirm_password,
          display_name: form.display_name,
        })
    userStore.setUser(result.user, result.token)
    router.push('/dashboard')
  } catch (e: any) {
    error.value = e.message || (mode.value === 'login' ? '登录失败，请检查用户名和密码' : '注册失败，请检查输入信息')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1e293b 0%, #334155 40%, #1e1b4b 100%);
  position: relative;
  overflow: hidden;
}

/* Subtle grid background */
.login-page::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(99, 102, 241, 0.08) 1px, transparent 1px),
    linear-gradient(90deg, rgba(99, 102, 241, 0.08) 1px, transparent 1px);
  background-size: 60px 60px;
}

.login-card {
  width: 400px;
  padding: 40px;
  background: var(--card-bg);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  border: 1px solid var(--border-color);
  position: relative;
}

.login-header {
  text-align: center;
  margin-bottom: 24px;
}

.login-logo {
  margin-bottom: 16px;
}

.logo-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: var(--radius-lg);
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  color: white;
  font-size: 20px;
  font-weight: 800;
  letter-spacing: 0.02em;
}

.login-title {
  font-size: 26px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.login-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
}

.auth-switch {
  display: flex;
  justify-content: center;
  margin-bottom: 24px;
}

.login-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
}

.login-error {
  margin-top: 16px;
}
</style>
