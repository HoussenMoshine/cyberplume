import { ref, reactive } from 'vue';
import { config } from '@/config.js';
import { handleApiError } from '@/utils/errorHandler.js';

export function useProjects() {
  const projects = ref([]);
  const loadingProjects = ref(false);
  const errorProjects = ref(null);
  const submittingProject = ref(false);
  const deletingItem = reactive({ type: null, id: null });

  const exportingProjectId = ref(null);
  const exportingFormat = ref(null);
  const exportError = ref(null);

  async function fetchProjects() {
    console.log('useProjects: Fetching projects...');
    loadingProjects.value = true;
    errorProjects.value = null;
    try {
      const response = await fetch(`${config.apiUrl}/api/projects/`, {
          headers: { 'x-api-key': config.apiKey }
      });
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || `HTTP error ${response.status}`);
      }
      projects.value = await response.json();
      console.log('useProjects: Projects fetched successfully.', projects.value.length);
    } catch (error) {
      errorProjects.value = handleApiError(error, 'récupération des projets');
      console.error('useProjects: Failed to fetch projects:', error);
    } finally {
      loadingProjects.value = false;
    }
  }

  async function addProject(projectData) {
    console.log('useProjects: Adding project...', projectData);
    submittingProject.value = true;
    errorProjects.value = null;
    try {
      const response = await fetch(`${config.apiUrl}/api/projects/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': config.apiKey
        },
        body: JSON.stringify(projectData),
      });
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || `HTTP error ${response.status}`);
      }
      const newProject = await response.json();
      projects.value.push(newProject);
      console.log('useProjects: Project added successfully.', newProject);
      return newProject;
    } catch (error) {
      errorProjects.value = handleApiError(error, 'ajout du projet');
      console.error('useProjects: Failed to add project:', error);
      return null;
    } finally {
      submittingProject.value = false;
    }
  }

  async function updateProject(projectId, projectData) {
    console.log(`useProjects: Updating project ${projectId}...`, projectData);
    submittingProject.value = true;
    errorProjects.value = null;
    try {
      const response = await fetch(`${config.apiUrl}/api/projects/${projectId}/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': config.apiKey
        },
        body: JSON.stringify(projectData),
      });
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || `HTTP error ${response.status}`);
      }
      const updatedProject = await response.json();
      const index = projects.value.findIndex(p => p.id === projectId);
      if (index !== -1) {
        projects.value[index] = updatedProject;
      }
      console.log('useProjects: Project updated successfully.', updatedProject);
      return updatedProject;
    } catch (error) {
      errorProjects.value = handleApiError(error, `mise à jour du projet ${projectId}`);
      console.error(`useProjects: Failed to update project ${projectId}:`, error);
      return null;
    } finally {
      submittingProject.value = false;
    }
  }

  async function deleteProject(projectId) {
console.log(`[useProjects] deleteProject called with projectId: ${projectId}`);
    console.log(`useProjects: Deleting project ${projectId}...`);
    deletingItem.type = 'project';
    deletingItem.id = projectId;
    errorProjects.value = null;
    try {
const apiUrl = `${config.apiUrl}/api/projects/${projectId}/`;
      console.log(`[useProjects] Attempting to DELETE: ${apiUrl}`);
      const response = await fetch(`${config.apiUrl}/api/projects/${projectId}/`, {
        method: 'DELETE',
        headers: { 'x-api-key': config.apiKey }
      });
      if (!response.ok) {
        if (response.status === 404) {
            console.warn(`useProjects: Project ${projectId} not found for deletion (maybe already deleted).`);
            projects.value = projects.value.filter(p => p.id !== projectId);
            return true;
        }
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || `HTTP error ${response.status}`);
      }
      projects.value = projects.value.filter(p => p.id !== projectId);
      console.log(`useProjects: Project ${projectId} deleted successfully.`);
      return true;
    } catch (error) {
      errorProjects.value = handleApiError(error, `suppression du projet ${projectId}`);
      console.error(`useProjects: Failed to delete project ${projectId}:`, error);
      return false;
    } finally {
      deletingItem.type = null;
      deletingItem.id = null;
    }
  }

  async function exportProject(projectId, format) {
    console.log(`useProjects: Exporting project ${projectId} as ${format}...`);
    exportingProjectId.value = projectId;
    exportingFormat.value = format;
    exportError.value = null;

    try {
      const response = await fetch(`${config.apiUrl}/api/projects/${projectId}/export/${format}`, {
        method: 'GET',
        headers: { 'x-api-key': config.apiKey }
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || `HTTP error ${response.status}`);
      }

      const disposition = response.headers.get('content-disposition');
      let filename = `projet_${projectId}.${format}`;
      if (disposition && disposition.indexOf('attachment') !== -1) {
          const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
          const matches = filenameRegex.exec(disposition);
          if (matches != null && matches[1]) {
              filename = matches[1].replace(/['"]/g, '');
          }
      }

      const blob = await response.blob();

      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();

      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url);

      console.log(`useProjects: Project ${projectId} exported successfully as ${filename}.`);
      return true;

    } catch (error) {
      exportError.value = handleApiError(error, `export du projet ${projectId} en ${format}`);
      console.error(`useProjects: Failed to export project ${projectId} as ${format}:`, error);
      return false;
    } finally {
      exportingProjectId.value = null;
      exportingFormat.value = null;
    }
  }

  function getProjectById(projectId) {
    return projects.value.find(p => p.id === projectId);
  }

  return {
    projects,
    loadingProjects,
    errorProjects,
    submittingProject,
    deletingItem,
    exportingProjectId,
    exportingFormat,
    exportError,

    fetchProjects,
    addProject,
    updateProject,
    deleteProject,
    exportProject,
    getProjectById,
  };
}