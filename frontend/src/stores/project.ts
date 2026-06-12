import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Project } from '@/types/project'
import { getProjects } from '@/api/projects'

export const useProjectStore = defineStore('project', () => {
  const projects = ref<Project[]>([])
  const currentProject = ref<Project | null>(null)

  async function fetchProjects() {
    projects.value = await getProjects()
  }

  function setCurrentProject(project: Project | null) {
    currentProject.value = project
    if (project) {
      localStorage.setItem('currentProjectId', String(project.id))
    } else {
      localStorage.removeItem('currentProjectId')
    }
  }

  function getCurrentProjectId(): number | null {
    return currentProject.value?.id ?? (Number(localStorage.getItem('currentProjectId')) || null)
  }

  return {
    projects,
    currentProject,
    fetchProjects,
    setCurrentProject,
    getCurrentProjectId,
  }
})
