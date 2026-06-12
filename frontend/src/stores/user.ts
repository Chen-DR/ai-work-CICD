import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { User } from '@/types/user'
import { getCurrentUser } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(JSON.parse(localStorage.getItem('user') || 'null'))
  const token = ref<string | null>(localStorage.getItem('token'))

  function setUser(userData: User, userToken: string) {
    user.value = userData
    token.value = userToken
    localStorage.setItem('user', JSON.stringify(userData))
    localStorage.setItem('token', userToken)
  }

  function clearUser() {
    user.value = null
    token.value = null
    localStorage.removeItem('user')
    localStorage.removeItem('token')
  }

  async function fetchCurrentUser() {
    try {
      const userData = await getCurrentUser()
      user.value = userData
      localStorage.setItem('user', JSON.stringify(userData))
    } catch {
      clearUser()
    }
  }

  const isLoggedIn = () => !!token.value

  const isAdmin = () => user.value?.role === 'admin'

  const hasPermission = (roles: string[]) => {
    if (!user.value) return false
    if (user.value.role === 'admin') return true
    return roles.includes(user.value.role)
  }

  return {
    user,
    token,
    setUser,
    clearUser,
    fetchCurrentUser,
    isLoggedIn,
    isAdmin,
    hasPermission,
  }
})
