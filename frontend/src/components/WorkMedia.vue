<script setup>
import { computed, ref, watch } from 'vue'
import { mediaUrl } from '../services/api.js'

const props = defineProps({ work: { type: Object, required: true }, compact: Boolean })
const index = ref(0)
const images = computed(() => {
  const paths = props.work.images?.length ? props.work.images : (props.work.file_path ? [props.work.file_path] : [])
  return paths.map(mediaUrl)
})
watch(() => props.work.id, () => { index.value = 0 })
function move(step) { index.value = (index.value + step + images.value.length) % images.value.length }
</script>

<template>
  <div v-if="work.category === 'text'" :class="compact ? 'browse-text' : 'text-display'">
    {{ compact && work.text_content?.length > 80 ? work.text_content.slice(0, 80) + '…' : (work.text_content || '（无内容）') }}
  </div>
  <div v-else-if="work.category === 'video'" :class="compact ? 'browse-placeholder' : ''">
    <span v-if="compact">🎬</span>
    <video v-else controls preload="metadata" style="width:100%;max-height:500px"><source :src="mediaUrl(work.file_path)" type="video/mp4" />您的浏览器不支持视频播放</video>
  </div>
  <div v-else-if="images.length" :class="{ gallery: images.length > 1 }">
    <img :src="compact ? mediaUrl(work.thumbnail_path || work.file_path) : images[index]" :alt="work.title" loading="lazy" />
    <template v-if="!compact && images.length > 1">
      <button class="gallery-nav prev" type="button" title="上一张" @click.stop="move(-1)">‹</button>
      <button class="gallery-nav next" type="button" title="下一张" @click.stop="move(1)">›</button>
      <div class="gallery-dots"><button v-for="(_, i) in images" :key="i" type="button" class="dot" :class="{ active: i === index }" @click.stop="index = i" /></div>
    </template>
  </div>
  <div v-else class="browse-placeholder">📷</div>
</template>
