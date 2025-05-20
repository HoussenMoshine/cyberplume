<template>
  <div class="scenes-container pl-4 pr-1">
    <v-progress-linear v-if="loadingScenes" indeterminate color="secondary" height="2"></v-progress-linear>
    <v-alert v-if="errorScenes" type="warning" density="compact" variant="tonal" class="my-1">
      Erreur scènes: {{ errorScenes }}
    </v-alert>

    <template v-if="!loadingScenes && !errorScenes">
      <template v-if="localScenes && localScenes.length > 0">
         <draggable
           v-model="localScenes"
           item-key="id"
           tag="div"
           handle=".drag-handle"
           @end="$emit('reordered', localScenes)"
           ghost-class="ghost-item"
           drag-class="drag-item"
         >
           <template #item="{ element: scene }">
              <v-list-item
                :key="scene.id"
                link
                density="compact"
                min-height="40px"
                class="list-item-hover-actions scene-item pl-2 pr-1 py-1"
                @click.stop="$emit('select-scene', scene.id)"
              >
                <template v-slot:prepend>
                  <!-- Utilisation directe de l'icône importée -->
                  <IconGripVertical size="18" class="drag-handle mr-2" title="Réordonner" />
                  <!-- Utilisation directe de l'icône importée -->
                  <IconMovie size="18" class="mr-2" />
                </template>
                <v-list-item-title class="text-body-2 text-medium-emphasis">
                   {{ scene.title }}
                </v-list-item-title>
                <template v-slot:append>
                  <v-menu location="bottom end">
                    <template v-slot:activator="{ props: sceneMenuProps }">
                      <v-btn
                        icon
                        density="compact"
                        variant="text"
                        v-bind="sceneMenuProps"
                        @click.stop
                        title="Actions Scène"
                        size="small"
                        class="action-menu-btn"
                      >
                        <!-- Utilisation directe de l'icône importée -->
                        <IconDotsVertical size="20" />
                      </v-btn>
                    </template>
                    <v-list density="compact">
                      <v-list-item @click.stop="$emit('open-edit', scene)" title="Modifier la scène">
                        <template v-slot:prepend>
                          <IconPencil size="18" class="mr-3"/>
                        </template>
                        <v-list-item-title>Modifier</v-list-item-title>
                      </v-list-item>
                      <v-list-item @click.stop="openDeleteConfirmDialog('scene', scene)" title="Supprimer la scène" class="text-error">
                        <template v-slot:prepend>
                          <IconTrash size="18" class="mr-3"/>
                        </template>
                        <v-list-item-title>Supprimer</v-list-item-title>
                      </v-list-item>
                    </v-list>
                  </v-menu>
                </template>
              </v-list-item>
           </template>
         </draggable>
      </template>
      <v-list-item v-else dense class="pl-2 py-1">
         <v-list-item-title class="text-caption font-italic text-disabled">Aucune scène</v-list-item-title>
      </v-list-item>
    </template>

    <!-- Dialogues spécifiques aux scènes -->
    <AddSceneDialog
      :show="showAddSceneDialog"
      :loading="submittingScene"
      :error="addSceneError"
      :chapterTitle="chapterTitleForNewScene"
      @close="handleAddSceneDialogClose"
      @save="handleAddSceneDialogSave"
    />

    <EditSceneDialog
      :show="showEditSceneDialog"
      :loading="submittingScene"
      :error="editSceneError"
      :initialTitle="editingScene?.title || ''"
      :initialOrder="editingScene?.order ?? 0"
      @close="closeEditSceneDialog"
      @save="submitEditScene"
    />

    <DeleteConfirmDialog
      :show="showDeleteConfirmDialog"
      :loading="!!deletingSceneId || deletingItem"
      :deleteTarget="deleteTarget"
      @close="closeDeleteConfirmDialog"
      @confirm="confirmDelete"
    />

  </div>
</template>

<script setup>
import { defineProps, defineEmits, ref, watch, reactive } from 'vue';
import draggable from 'vuedraggable';
import {
  VListItem, VListItemTitle, VBtn, VProgressLinear, VAlert, VMenu, VList // VIcon n'est plus importé
} from 'vuetify/components';
import AddSceneDialog from './dialogs/AddSceneDialog.vue';
import EditSceneDialog from './dialogs/EditSceneDialog.vue';
import DeleteConfirmDialog from './dialogs/DeleteConfirmDialog.vue';
import { useScenes } from '@/composables/useScenes.js';

// Import des icônes Tabler nécessaires (importation nommée)
import {
  IconGripVertical, IconMovie, IconDotsVertical, IconPencil, IconTrash
} from '@tabler/icons-vue';

const props = defineProps({
  scenes: {
    type: Array,
    default: () => []
  },
  loadingScenes: {
    type: Boolean,
    default: false
  },
  errorScenes: {
    type: [String, null],
    default: null
  },
  chapterId: {
    type: Number,
    required: true
  },
  chapterTitleForNewScene: {
    type: String,
    default: ''
  }
});

const emit = defineEmits([
  'reordered',
  'select-scene',
  'open-add-scene',
  'open-edit', // Ajouter l'événement open-edit
  'open-delete' // Ajouter l'événement open-delete
]);

// Create a local reactive copy of the scenes prop
const localScenes = ref([...props.scenes]);

// Watch for changes in the scenes prop and update the local copy
watch(() => props.scenes, (newScenes) => {
  localScenes.value = [...newScenes];
}, { deep: true });

// Use composable for scene logic
const {
  submittingScene, deletingSceneId, addScene, updateScene, deleteScene,
} = useScenes();

// --- State (local) for Dialogs ---
const showAddSceneDialog = ref(false);
const addSceneError = ref(null);
const showEditSceneDialog = ref(false);
const editingScene = ref(null);
const editSceneError = ref(null);
const showDeleteConfirmDialog = ref(false);
const deleteTarget = reactive({ type: null, item: null });
const deletingItem = ref(false);


// --- Methods for Dialogs ---
const openAddSceneDialog = () => { // Cette fonction n'est pas appelée ici mais gardée pour référence
  addSceneError.value = null;
  showAddSceneDialog.value = true;
};

const handleAddSceneDialogClose = () => {
  showAddSceneDialog.value = false;
  addSceneError.value = null;
};

const handleAddSceneDialogSave = async (sceneData) => {
  addSceneError.value = null;
  const newScene = await addScene(props.chapterId, sceneData);
  if (newScene) {
    handleAddSceneDialogClose();
  } else {
    addSceneError.value = 'Erreur lors de l\'ajout de la scène.';
  }
};

const openEditSceneDialog = (scene) => {
  editingScene.value = { ...scene };
  editSceneError.value = null;
  showEditSceneDialog.value = true;
  // Émettre l'événement pour que le parent (ChapterList) puisse le gérer si nécessaire
  emit('open-edit', scene);
};

const closeEditSceneDialog = () => {
  showEditSceneDialog.value = false;
  editingScene.value = null;
  editSceneError.value = null;
};

const submitEditScene = async (sceneData) => {
  editSceneError.value = null;
  if (!editingScene.value) return;
  const success = await updateScene(editingScene.value.id, sceneData);
  if (success) {
    closeEditSceneDialog();
  } else {
    editSceneError.value = 'Erreur lors de la modification de la scène.';
  }
};

const openDeleteConfirmDialog = (type, item) => {
  deleteTarget.type = type;
  deleteTarget.item = item;
  showDeleteConfirmDialog.value = true;
   // Émettre l'événement pour que le parent (ChapterList) puisse le gérer si nécessaire
  emit('open-delete', type, item);
};

const closeDeleteConfirmDialog = () => {
  showDeleteConfirmDialog.value = false;
  deleteTarget.type = null;
  deleteTarget.item = null;
};

const confirmDelete = async () => {
  if (!deleteTarget.item || !deleteTarget.type) return;

  deletingItem.value = true;
  let success = false;
  if (deleteTarget.type === 'scene') {
    success = await deleteScene(deleteTarget.item.id);
  }
  // Ajoutez ici la logique pour d'autres types si nécessaire

  deletingItem.value = false;
  if (success) {
    closeDeleteConfirmDialog();
  } else {
    // Gérer l'erreur (peut-être afficher un message dans le dialogue)
    console.error(`Erreur lors de la suppression de ${deleteTarget.type}`);
  }
};

</script>

<style scoped>
.scenes-container {
  /* Styles pour le conteneur des scènes */
}

.list-item-hover-actions {
  position: relative;
}

.action-menu-btn {
  opacity: 0; /* Caché par défaut */
  transition: opacity 0.2s ease-in-out;
}

.list-item-hover-actions:hover .action-menu-btn {
  opacity: 1; /* Visible au survol */
}

.drag-handle {
  cursor: grab;
}

.ghost-item {
  opacity: 0.5;
  background-color: rgba(var(--v-theme-primary), 0.05); /* Updated background color */
}

.drag-item {
  background-color: rgba(var(--v-theme-primary), 0.1); /* Updated background color */
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}
</style>