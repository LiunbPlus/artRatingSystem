<script setup>
import { useRoute, useRouter } from 'vue-router'
import { auth, logout } from '../services/auth.js'

const route = useRoute()
const router = useRouter()
const toggleTheme = () => window.toggleTheme()

async function signOut() {
  await logout()
  router.push('/login')
}
</script>

<template>
  <nav class="navbar">
    <RouterLink to="/" class="navbar-brand">🎨 “大众创享”作品一览</RouterLink>
    <ul class="navbar-nav">
      <li><RouterLink to="/" :class="{ active: route.path === '/' }">评分</RouterLink></li>
      <template v-if="auth.user?.role === 'admin'">
        <li><RouterLink to="/admin" :class="{ active: route.path === '/admin' }">管理</RouterLink></li>
        <li><RouterLink to="/admin/upload" :class="{ active: route.path === '/admin/upload' }">上传</RouterLink></li>
      </template>
      <li><button data-theme-toggle type="button" @click="toggleTheme">🌙</button></li>
      <li><span class="nav-user-info">{{ auth.user?.username }}<template v-if="auth.user?.role === 'admin'"> · 管理员</template></span></li>
      <li><RouterLink to="/change-password" :class="{ active: route.path === '/change-password' }">修改密码</RouterLink></li>
      <li><button type="button" @click="signOut">退出</button></li>
    </ul>
  </nav>
</template>
