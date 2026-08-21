<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import AppNavbar from '../components/AppNavbar.vue'
import WorkMedia from '../components/WorkMedia.vue'
import { request } from '../services/api.js'

const categories = [
  ['all', '全部'], ['photo', '📷 摄影'], ['text', '📝 文字'], ['video', '🎬 视频'], ['object', '📦 手工'],
]
const catNames = { photo: '摄影', text: '文字', video: '视频', object: '手工' }
const catClasses = { photo: 'cat-photo', text: 'cat-text', video: 'cat-video', object: 'cat-object' }
const view = ref('browse')
const category = ref('all')
const works = ref([])
const loading = ref(false)
const currentIndex = ref(0)
const dimensions = ref([])
const scores = reactive({})
const detail = ref(null)
const error = ref('')

const current = computed(() => works.value[currentIndex.value])
const progress = computed(() => {
  if (loading.value) return '加载中…'
  if (view.value === 'browse') return works.value.length ? `共 ${works.value.length} 件作品 · 已评 ${works.value.filter(w => w.rated).length} 件` : '暂无作品'
  return current.value ? `第 ${works.value.length - currentIndex.value} / ${works.value.length} 件待评分` : '已完成'
})

async function load() {
  loading.value = true; error.value = ''; currentIndex.value = 0
  const path = view.value === 'browse' ? '/api/works' : '/api/works/unrated'
  const { data } = await request(`${path}?category=${category.value}`)
  loading.value = false
  if (!data.success) return (error.value = data.message || '加载失败')
  works.value = data.works || []
  if (view.value === 'rate' && current.value) await loadDimensions()
}
async function loadDimensions() {
  Object.keys(scores).forEach(key => delete scores[key])
  const { data } = await request(`/api/works/${current.value.id}/dimensions`)
  dimensions.value = data.dimensions || []
}
async function switchView(next) { view.value = next; await load() }
async function goRate(work) {
  view.value = 'rate'; await load()
  const index = works.value.findIndex(item => item.id === work.id)
  if (index > 0) { const [target] = works.value.splice(index, 1); works.value.unshift(target) }
  if (current.value) await loadDimensions()
}
async function skip() { currentIndex.value++; if (current.value) await loadDimensions() }
async function submitRating() {
  if (dimensions.value.some(dim => !scores[dim])) return alert('请为每个维度都打分')
  const { data } = await request(`/api/works/${current.value.id}/rate`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ scores }),
  })
  if (!data.success) return alert(data.message)
  await skip()
}
async function openDetail(id) {
  const { data } = await request(`/api/works/${id}`)
  if (data.success) detail.value = data.work
}
watch(category, load)
onMounted(load)
</script>

<template>
  <AppNavbar />
  <main class="container">
    <div class="cards-header"><h2>作品评审</h2><div class="stats">{{ progress }}</div></div>
    <div class="view-switch">
      <button :class="{ active: view === 'browse' }" @click="switchView('browse')">📋 浏览全部</button>
      <button :class="{ active: view === 'rate' }" @click="switchView('rate')">⭐ 去评分</button>
    </div>
    <div class="category-filter" style="margin-bottom:24px">
      <button v-for="item in categories" :key="item[0]" :class="{ active: category === item[0] }" @click="category = item[0]">{{ item[1] }}</button>
    </div>
    <div v-if="error" class="alert alert-error" style="display:block">{{ error }}</div>
    <div v-if="loading" class="empty-state"><p>加载中…</p></div>

    <div v-else-if="view === 'browse'" class="browse-grid">
      <div v-if="!works.length" class="empty-state" style="grid-column:1/-1"><div class="icon">🖼️</div><h3>暂无作品</h3><p>该分类下暂无作品</p></div>
      <article v-for="work in works" :key="work.id" class="browse-card" title="点击查看详情" @click="openDetail(work.id)">
        <div class="browse-media"><WorkMedia :work="work" compact /></div>
        <div class="browse-body">
          <span class="card-category" :class="catClasses[work.category]">{{ catNames[work.category] }}</span>
          <div class="browse-title">{{ work.title }}</div><div class="browse-author">{{ work.author_name }}</div>
          <div class="browse-stats"><span class="avg-score">{{ work.stats?.overall_avg ?? '-' }}分</span><span class="browse-rcount"> / {{ work.stats?.count || 0 }}人</span><span v-if="work.my_avg != null" class="my-score">我的 {{ work.my_avg }}分</span></div>
          <div class="browse-actions"><span v-if="work.rated" class="badge badge-visible">✓ 已评分</span><button v-else class="btn btn-primary btn-sm" @click.stop="goRate(work)">去评分</button></div>
        </div>
      </article>
    </div>

    <div v-else class="card-stack">
      <div v-if="!current" class="empty-state"><div class="icon">✅</div><h3>所有作品已评分完毕</h3><p>当前分类暂无待评分作品</p></div>
      <template v-else>
        <article class="work-card"><div class="card-media"><WorkMedia :work="current" /></div><div class="card-body"><span class="card-category" :class="catClasses[current.category]">{{ catNames[current.category] }}</span><div class="card-title">{{ current.title }}</div><div class="card-desc">{{ current.description || '暂无简介' }}</div></div></article>
        <section class="rating-panel"><h3>⭐ 为这件作品评分（1-10分）</h3>
          <div v-for="dim in dimensions" :key="dim" class="dimension-row"><span class="dim-label">{{ dim }}</span><div class="stars"><button v-for="score in 10" :key="score" type="button" class="star" :class="{ selected: score <= scores[dim] }" :title="`${score}分`" @click="scores[dim] = score">★</button></div></div>
          <div class="rating-actions"><button class="btn btn-outline" @click="skip">跳过 ▶</button><button class="btn btn-primary" @click="submitRating">提交评分</button></div>
        </section>
      </template>
    </div>
  </main>

  <div v-if="detail" class="modal-overlay" style="display:flex" @click.self="detail = null"><div class="modal-content"><button class="modal-close" @click="detail = null">×</button><div class="modal-media"><WorkMedia :work="detail" /></div><div class="modal-body"><span class="card-category" :class="catClasses[detail.category]">{{ catNames[detail.category] }}</span><div class="card-title">{{ detail.title }}</div><div class="modal-author">作者：{{ detail.author_name }}</div><div v-if="detail.description" class="card-desc">{{ detail.description }}</div></div></div></div>
</template>
