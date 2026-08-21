import { createRouter, createWebHistory } from 'vue-router'
import { auth } from '../services/auth.js'

const routes = [
  { path: '/', component: () => import('../views/HomeView.vue'), meta: { auth: true } },
  { path: '/login', component: () => import('../views/LoginView.vue'), meta: { guest: true } },
  { path: '/register', component: () => import('../views/RegisterView.vue'), meta: { guest: true } },
  { path: '/admin', component: () => import('../views/AdminView.vue'), meta: { auth: true, admin: true } },
  { path: '/admin/upload', component: () => import('../views/UploadView.vue'), meta: { auth: true, admin: true } },
  { path: '/change-password', component: () => import('../views/ChangePasswordView.vue'), meta: { auth: true } },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({ history: createWebHistory(), routes })
router.beforeEach((to) => {
  if (to.meta.auth && !auth.user) return '/login'
  if (to.meta.admin && auth.user?.role !== 'admin') return '/'
  if (to.meta.guest && auth.user) return auth.user.role === 'admin' ? '/admin' : '/'
})

export default router
