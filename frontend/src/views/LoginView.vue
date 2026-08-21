<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { request } from '../services/api.js'
import { setUser } from '../services/auth.js'

const router = useRouter()
const form = reactive({ username: '', password: '' })
const error = ref('')
const submitting = ref(false)
const toggleTheme = () => window.toggleTheme()

async function submit() {
  error.value = ''
  submitting.value = true
  const body = new FormData()
  body.append('username', form.username)
  body.append('password', form.password)
  const { data } = await request('/api/login', { method: 'POST', body })
  submitting.value = false
  if (!data.success) return (error.value = data.message)
  setUser(data.user)
  router.push(data.user.role === 'admin' ? '/admin' : '/')
}
</script>

<template>
  <main class="auth-page">
    <div class="auth-card">
      <div style="text-align:right;margin-bottom:8px"><button data-theme-toggle type="button" style="background:none;border:0;font-size:1.2rem" @click="toggleTheme">🌙</button></div>
      <h1>🎨 “大众创享”作品一览</h1><p class="subtitle">登录以继续</p>
      <div v-if="error" class="alert alert-error" style="display:block">{{ error }}</div>
      <form @submit.prevent="submit">
        <div class="form-group"><label>用户名</label><input v-model.trim="form.username" required autofocus placeholder="请输入用户名" /></div>
        <div class="form-group"><label>密码</label><input v-model="form.password" type="password" required placeholder="请输入密码" /></div>
        <button class="btn btn-primary" :disabled="submitting">{{ submitting ? '登录中…' : '登录' }}</button>
      </form>
      <p class="auth-footer">还没有账号？<RouterLink to="/register">使用邀请码注册</RouterLink></p>
    </div>
  </main>
</template>
