<template>
  <div class="page-container">
    <div class="page-header">
      <h2>新增服务器</h2>
      <el-button @click="$router.push('/servers')">返回列表</el-button>
    </div>

    <el-card style="max-width: 700px">
      <el-form label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="所属项目" required>
              <ProjectSelector v-model="form.project_id" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="服务器名称" required>
              <el-input v-model="form.name" placeholder="例如：GPU-Node-1" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="主机地址" required>
              <el-input v-model="form.host" placeholder="IP 或域名" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="端口" required>
              <el-input-number v-model="form.port" :min="1" :max="65535" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="用户名" required>
              <el-input v-model="form.username" placeholder="root" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="认证方式">
          <el-radio-group v-model="form.auth_type">
            <el-radio value="password">密码认证</el-radio>
            <el-radio value="ssh_key">SSH Key 认证</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item v-if="form.auth_type === 'password'" label="密码" required>
          <el-input v-model="form.password" type="password" show-password placeholder="SSH 密码" />
        </el-form-item>

        <el-form-item v-if="form.auth_type === 'ssh_key'" label="SSH 私钥" required>
          <el-input
            v-model="form.ssh_key"
            type="textarea"
            :rows="6"
            placeholder="-----BEGIN OPENSSH PRIVATE KEY-----&#10;..."
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="saving" @click="handleSave" :disabled="!form.project_id">
            保存
          </el-button>
          <el-button @click="$router.push('/servers')">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import ProjectSelector from '@/components/ProjectSelector/index.vue'
import { createServer } from '@/api/servers'
import { useProjectStore } from '@/stores/project'

const router = useRouter()
const projectStore = useProjectStore()

const saving = ref(false)

const form = reactive({
  project_id: projectStore.getCurrentProjectId() ?? undefined as any,
  name: '',
  host: '',
  port: 22,
  username: 'root',
  auth_type: 'password' as 'password' | 'ssh_key',
  password: '',
  ssh_key: '',
})

async function handleSave() {
  if (!form.project_id || !form.name || !form.host || !form.username) {
    ElMessage.warning('请填写完整信息')
    return
  }
  if (form.auth_type === 'password' && !form.password) {
    ElMessage.warning('请输入密码')
    return
  }
  if (form.auth_type === 'ssh_key' && !form.ssh_key) {
    ElMessage.warning('请输入 SSH 私钥')
    return
  }

  saving.value = true
  try {
    await createServer({
      project_id: form.project_id!,
      name: form.name,
      host: form.host,
      port: form.port,
      username: form.username,
      auth_type: form.auth_type,
      password: form.password || undefined,
      ssh_key: form.ssh_key || undefined,
    })
    ElMessage.success('服务器添加成功')
    router.push('/servers')
  } catch (e: any) {
    ElMessage.error(e.message || '保存失败')
  } finally {
    saving.value = false
  }
}
</script>
