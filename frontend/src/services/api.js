const API_BASE = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '')

export async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    credentials: 'include',
    ...options,
  })
  let data
  try {
    data = await response.json()
  } catch {
    data = { success: false, message: '服务器返回了无法解析的数据' }
  }
  if (response.status === 401) {
    localStorage.removeItem('art-user')
    if (!location.pathname.startsWith('/login')) location.href = '/login'
  }
  if (!response.ok && !data.message) data.message = `请求失败（${response.status}）`
  return { response, data }
}

export function mediaUrl(path) {
  if (!path || /^(https?:)?\/\//.test(path)) return path
  return `${API_BASE}${path}`
}
