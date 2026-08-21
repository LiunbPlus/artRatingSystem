<script setup>
import { reactive, ref } from 'vue'
import AppNavbar from '../components/AppNavbar.vue'
import { request } from '../services/api.js'

const form = reactive({ old_password: '', new_password: '', confirm: '' })
const error = ref('')
const success = ref('')
async function submit() {
  error.value = ''; success.value = ''
  if (form.new_password !== form.confirm) return (error.value = '两次输入的新密码不一致')
  const body = new FormData()
  body.append('old_password', form.old_password); body.append('new_password', form.new_password)
  const { data } = await request('/api/change-password', { method: 'POST', body })
  if (!data.success) return (error.value = data.message)
  success.value = data.message
  form.old_password = form.new_password = form.confirm = ''
}
</script>

<template><AppNavbar /><main class="container"><div class="upload-form">
  <h2>🔐 修改密码</h2>
  <div v-if="error" class="alert alert-error" style="display:block">{{ error }}</div>
  <div v-if="success" class="alert alert-success" style="display:block">{{ success }}</div>
  <form @submit.prevent="submit">
    <div class="form-group"><label>原密码</label><input v-model="form.old_password" type="password" required /></div>
    <div class="form-group"><label>新密码</label><input v-model="form.new_password" type="password" required /></div>
    <div class="form-group"><label>确认新密码</label><input v-model="form.confirm" type="password" required /></div>
    <button class="btn btn-primary">确认修改</button>
  </form>
</div></main></template>
