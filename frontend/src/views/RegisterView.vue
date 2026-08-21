<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { request } from '../services/api.js'
import { setUser } from '../services/auth.js'

const router = useRouter()
const form = reactive({ username: '', password: '', invite_code: '' })
const error = ref('')
const toggleTheme = () => window.toggleTheme()

async function submit() {
  error.value = ''
  if (!/^\d{4}$/.test(form.password)) return (error.value = '密码必须为4位纯数字（0-9）')
  const body = new FormData()
  Object.entries(form).forEach(([key, value]) => body.append(key, value))
  const { data } = await request('/api/register', { method: 'POST', body })
  if (!data.success) return (error.value = data.message)
  setUser(data.user)
  router.push('/')
}
</script>

<template>
  <main class="auth-page"><div class="auth-card">
    <div style="text-align:right;margin-bottom:8px"><button data-theme-toggle type="button" style="background:none;border:0;font-size:1.2rem" @click="toggleTheme">🌙</button></div>
    <h1>🎨 评委注册</h1><p class="subtitle">需要有效邀请码才能注册</p>
    <div v-if="error" class="alert alert-error" style="display:block">{{ error }}</div>
    <form @submit.prevent="submit">
      <div class="form-group"><label>用户名</label><input v-model.trim="form.username" required minlength="2" placeholder="请设置用户名（至少2字符）" /></div>
      <div class="form-group"><label>密码</label><input v-model="form.password" type="password" required maxlength="4" inputmode="numeric" placeholder="请输入4位数字密码" /><div class="pwd-hint">⚠️ 密码仅支持 <strong>4 位纯数字</strong></div></div>
      <div class="form-group"><label>邀请码</label><input v-model.trim="form.invite_code" required placeholder="请输入邀请码" /></div>
      <button class="btn btn-primary">注册</button>
    </form>
    <p class="auth-footer">已有账号？<RouterLink to="/login">返回登录</RouterLink></p>
  </div></main>
</template>
