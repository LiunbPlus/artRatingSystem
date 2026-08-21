import { reactive } from 'vue'
import { request } from './api.js'

function storedUser() {
  try { return JSON.parse(localStorage.getItem('art-user')) }
  catch { return null }
}

export const auth = reactive({ user: storedUser() })

export function setUser(user) {
  auth.user = user
  if (user) localStorage.setItem('art-user', JSON.stringify(user))
  else localStorage.removeItem('art-user')
}

export async function logout() {
  await request('/api/logout', { method: 'POST' })
  setUser(null)
}
