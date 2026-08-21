<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import AppNavbar from '../components/AppNavbar.vue'
import { mediaUrl, request } from '../services/api.js'

const catNames = { photo: '摄影', text: '文字', video: '视频', object: '手工' }
const catClasses = { photo: 'cat-photo', text: 'cat-text', video: 'cat-video', object: 'cat-object' }
const filters = reactive({ category: 'all', sort_by: 'created_at', sort_order: 'DESC' })
const works = ref([]), users = ref([]), invites = ref([])
const editing = ref(null), inviteMessage = ref('')

async function loadWorks() {
  const query = new URLSearchParams(filters).toString()
  const { data } = await request(`/api/works?${query}`); works.value = data.works || []
}
async function loadUsers() { const { data } = await request('/api/admin/users'); users.value = data.users || [] }
async function loadInvites() { const { data } = await request('/api/admin/invite-codes'); invites.value = data.invite_codes || [] }
async function generateInvites(count) {
  const body = new FormData(); body.append('count', count)
  const { data } = await request('/api/admin/invite-codes', { method: 'POST', body })
  if (!data.success) return alert(data.message)
  inviteMessage.value = `已生成 ${data.codes.length} 个邀请码`; await loadInvites()
}
async function openEdit(id) { const { data } = await request(`/api/works/${id}`); editing.value = { ...data.work } }
async function saveEdit() {
  const body = new FormData()
  for (const key of ['title', 'author_name', 'contact', 'description', 'text_content']) body.append(key, editing.value[key] || '')
  const { data } = await request(`/api/works/${editing.value.id}`, { method: 'PUT', body })
  if (!data.success) return alert(data.message)
  editing.value = null; await loadWorks()
}
async function toggleHidden(work) {
  if (!confirm(`确定要${work.is_hidden ? '公开' : '隐藏'}这件作品吗？`)) return
  await request(`/api/works/${work.id}/toggle-hidden`, { method: 'POST' }); await loadWorks()
}
async function deleteWork(work) {
  if (!confirm(`确定删除作品“${work.title}”吗？此操作不可恢复。`)) return
  const { data } = await request(`/api/works/${work.id}`, { method: 'DELETE' })
  if (!data.success) return alert(data.message)
  await loadWorks()
}
watch(filters, loadWorks, { deep: true })
onMounted(() => Promise.all([loadWorks(), loadUsers(), loadInvites()]))
</script>

<template><AppNavbar /><main class="container">
  <div class="admin-header"><h2>管理后台</h2><RouterLink to="/admin/upload" class="btn btn-primary btn-sm">＋ 上传新作品</RouterLink></div>
  <section class="invite-section"><h3>🎟️ 邀请码管理</h3><p style="color:var(--text-secondary);font-size:.85rem;margin-bottom:12px">每个邀请码仅可注册一个评委账号</p><div style="display:flex;gap:8px;margin-bottom:16px"><button class="btn btn-primary btn-sm" @click="generateInvites(1)">生成 1 个</button><button class="btn btn-outline btn-sm" @click="generateInvites(5)">生成 5 个</button><button class="btn btn-outline btn-sm" @click="generateInvites(10)">生成 10 个</button><span style="color:#10b981">{{ inviteMessage }}</span></div><div class="invite-codes-list"><span v-for="code in invites" :key="code.id" class="invite-code-item" :class="{ used: code.is_used }" :title="code.is_used ? `已被 ${code.used_by_name || '用户'} 使用` : '可用'">{{ code.code }}</span><span v-if="!invites.length">暂无邀请码</span></div></section>

  <div class="admin-header"><h2>👥 账号管理</h2></div><div class="works-table" style="margin-bottom:36px"><table><thead><tr><th>ID</th><th>用户名</th><th>角色</th><th>注册时间</th><th>评分次数</th></tr></thead><tbody><tr v-for="user in users" :key="user.id"><td>{{ user.id }}</td><td><strong>{{ user.username }}</strong></td><td><span class="badge" :class="user.role === 'admin' ? 'badge-visible' : 'badge-neutral'">{{ user.role === 'admin' ? '管理员' : '评委' }}</span></td><td>{{ user.created_at }}</td><td>{{ user.rating_count }}</td></tr></tbody></table></div>

  <div class="admin-header"><h2>📋 作品管理</h2></div><div class="admin-toolbar"><select v-model="filters.category"><option value="all">全部分类</option><option value="photo">📷 摄影</option><option value="text">📝 文字</option><option value="video">🎬 视频</option><option value="object">📦 手工</option></select><select v-model="filters.sort_by"><option value="created_at">按上传时间</option><option value="title">按标题</option><option value="author_name">按作者</option><option value="category">按分类</option></select><select v-model="filters.sort_order"><option value="DESC">降序</option><option value="ASC">升序</option></select><button class="btn btn-outline btn-sm" @click="loadWorks">刷新</button></div>
  <div class="works-table"><table><thead><tr><th>缩略图</th><th>标题</th><th>作者</th><th>分类</th><th>评分/人数</th><th>状态</th><th>上传时间</th><th>操作</th></tr></thead><tbody><tr v-for="work in works" :key="work.id"><td><span v-if="work.category === 'text'">📝</span><span v-else-if="work.category === 'video'">🎬</span><img v-else class="thumb-sm" :src="mediaUrl(work.thumbnail_path || work.file_path)" alt="" /></td><td><strong>{{ work.title }}</strong></td><td>{{ work.author_name }}</td><td><span class="card-category" :class="catClasses[work.category]">{{ catNames[work.category] }}</span></td><td><span class="avg-score">{{ work.stats?.overall_avg != null ? work.stats.overall_avg + '分' : '-' }}</span> / {{ work.stats?.count || 0 }}人</td><td><span class="badge" :class="work.is_hidden ? 'badge-hidden' : 'badge-visible'">{{ work.is_hidden ? '已隐藏' : '公开' }}</span></td><td>{{ work.created_at }}</td><td><div class="actions"><button class="btn btn-outline btn-sm" @click="openEdit(work.id)">编辑</button><button class="btn btn-outline btn-sm" @click="toggleHidden(work)">{{ work.is_hidden ? '公开' : '隐藏' }}</button><button class="btn btn-danger btn-sm" @click="deleteWork(work)">删除</button></div></td></tr></tbody></table></div>
</main>
<div v-if="editing" class="modal-overlay" style="display:flex"><div class="modal"><h3>✏️ 编辑作品信息</h3><div class="form-group"><label>标题</label><input v-model="editing.title" /></div><div class="form-group"><label>作者</label><input v-model="editing.author_name" /></div><div class="form-group"><label>联系方式</label><input v-model="editing.contact" /></div><div class="form-group"><label>简介</label><textarea v-model="editing.description" rows="3" /></div><div v-if="editing.category === 'text'" class="form-group"><label>文字内容</label><textarea v-model="editing.text_content" rows="5" /></div><div class="modal-actions"><button class="btn btn-outline" @click="editing = null">取消</button><button class="btn btn-primary" @click="saveEdit">保存</button></div></div></div>
</template>
