<script setup>
import { computed, reactive, ref } from 'vue'
import AppNavbar from '../components/AppNavbar.vue'
import { request } from '../services/api.js'

const form = reactive({ category: '', title: '', author_name: '', contact: '', description: '', text_content: '' })
const files = ref([])
const previews = ref([])
const error = ref('')
const success = ref('')
const uploading = ref(false)
const input = ref(null)
const totalSize = computed(() => (files.value.reduce((sum, file) => sum + file.size, 0) / 1048576).toFixed(1))

function choose(event) {
  files.value = [...event.target.files]
  previews.value.forEach(URL.revokeObjectURL)
  previews.value = files.value.slice(0, 5).map(URL.createObjectURL)
}
function drop(event) {
  files.value = [...event.dataTransfer.files]
  previews.value.forEach(URL.revokeObjectURL)
  previews.value = files.value.slice(0, 5).map(URL.createObjectURL)
}
async function submit() {
  error.value = ''; success.value = ''
  if (form.category !== 'text' && !files.value.length) return (error.value = '请上传文件')
  uploading.value = true
  const body = new FormData()
  Object.entries(form).forEach(([key, value]) => body.append(key, value))
  files.value.forEach(file => body.append('files', file))
  const { data } = await request('/api/works/upload', { method: 'POST', body })
  uploading.value = false
  if (!data.success) return (error.value = data.message)
  success.value = data.message
  Object.assign(form, { category: '', title: '', author_name: '', contact: '', description: '', text_content: '' })
  files.value = []; previews.value = []; if (input.value) input.value.value = ''
  window.scrollTo(0, 0)
}
</script>

<template><AppNavbar /><main class="container"><div class="upload-form">
  <h2>📤 上传新作品</h2>
  <div v-if="error" class="alert alert-error" style="display:block">{{ error }}</div>
  <div v-if="success" class="alert alert-success" style="display:block">✅ {{ success }}</div>
  <form @submit.prevent="submit">
    <div class="form-group"><label>作品分类 *</label><select v-model="form.category" required><option value="">-- 请选择 --</option><option value="photo">📷 摄影</option><option value="text">📝 文字</option><option value="video">🎬 视频</option><option value="object">📦 手工</option></select></div>
    <div class="form-group"><label>作品标题 *</label><input v-model.trim="form.title" required placeholder="请输入作品标题" /></div>
    <div class="form-group"><label>作者姓名 *</label><input v-model.trim="form.author_name" required placeholder="请输入作者姓名" /></div>
    <div class="form-group"><label>联系方式</label><input v-model.trim="form.contact" placeholder="手机号/邮箱/微信等（选填）" /></div>
    <div class="form-group"><label>作品简介</label><textarea v-model="form.description" rows="3" placeholder="简要介绍作品（选填）" /></div>
    <div v-if="form.category === 'text'" class="form-group"><label>文字内容 *</label><textarea v-model="form.text_content" required rows="8" placeholder="请输入文字作品内容…" /></div>
    <div v-else class="form-group"><label>上传文件 *</label>
      <div class="file-upload-zone" @click="input?.click()" @dragover.prevent @drop.prevent.stop="drop">
        <div v-if="!files.length"><div class="upload-icon">📁</div><div class="upload-text">点击或拖拽文件到此处<br><small>{{ form.category === 'video' ? '视频：MP4 格式' : '摄影/手工：JPG、PNG（可多选，第一张为封面）' }}</small></div></div>
        <template v-else><video v-if="form.category === 'video'" class="preview" :src="previews[0]" controls @click.stop /><div v-else class="preview-grid" style="display:flex"><img v-for="src in previews" :key="src" :src="src" /></div><div style="font-size:.85rem;color:var(--text-secondary);margin-top:8px">共 {{ files.length }} 个文件，总大小 {{ totalSize }} MB</div></template>
        <input ref="input" type="file" hidden multiple :accept="form.category === 'video' ? '.mp4' : '.jpg,.jpeg,.png'" @change="choose" />
      </div>
    </div>
    <button class="btn btn-primary" :disabled="uploading">{{ uploading ? '上传中… 请勿刷新页面' : '上传作品' }}</button>
  </form>
</div></main></template>
