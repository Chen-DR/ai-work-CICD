import { defineStore } from 'pinia'
import { ref } from 'vue'

export type ThemeMode = 'light' | 'dark'
export type SidebarMode = 'expanded' | 'collapsed'

export const useAppStore = defineStore('app', () => {
  const sidebarMode = ref<SidebarMode>('expanded')
  const themeMode = ref<ThemeMode>('light')
  const pageLoading = ref(false)

  function toggleSidebar() {
    sidebarMode.value = sidebarMode.value === 'expanded' ? 'collapsed' : 'expanded'
  }

  function setTheme(mode: ThemeMode) {
    themeMode.value = mode
    document.documentElement.setAttribute('data-theme', mode)
  }

  function setPageLoading(loading: boolean) {
    pageLoading.value = loading
  }

  return {
    sidebarMode,
    themeMode,
    pageLoading,
    toggleSidebar,
    setTheme,
    setPageLoading,
  }
})
