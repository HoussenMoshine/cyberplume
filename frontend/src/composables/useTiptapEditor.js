import { ref, onMounted, onBeforeUnmount } from 'vue';
import { Editor } from '@tiptap/vue-3';
import StarterKit from '@tiptap/starter-kit';
import BubbleMenuExtension from '@tiptap/extension-bubble-menu';

/**
 * Composable pour gérer l'instance de l'éditeur TipTap.
 * @param {string|object} initialContent - Le contenu initial de l'éditeur.
 * @param {Function} onBlurCallback - Callback à exécuter lors de l'événement blur de l'éditeur.
 */
export function useTiptapEditor(initialContent = '<p style="color: grey; text-align: center;">Sélectionnez un chapitre ou une scène pour commencer l\'édition.</p>', onBlurCallback = null) {
  const editor = ref(null);

  const initializeEditor = () => {
    editor.value = new Editor({
      content: initialContent,
      extensions: [
        StarterKit,
        BubbleMenuExtension.configure({
          // Options si nécessaires, par exemple pour le pluginKey ou tippyOptions
          // pluginKey: 'bubbleMenuUniqueKey', // Si plusieurs bubble menus sont utilisés
          // tippyOptions: { duration: 100, placement: 'top-start' }, // Déplacé ici si spécifique à ce menu
        }),
      ],
      editorProps: {
        attributes: {
          class: 'tiptap-editor', // Assurez-vous que ce style est défini globalement ou dans le composant parent
        },
      },
      onBlur: ({ editor: blurredEditor }) => {
        console.log('useTiptapEditor: Editor blurred');
        if (onBlurCallback) {
          onBlurCallback(blurredEditor); // Appeler le callback fourni
        }
      },
      // onCreate: ({ editor }) => { console.log('Editor created'); },
      // onUpdate: ({ editor }) => { console.log('Editor updated'); },
      // onDestroy: () => { console.log('Editor destroyed'); },
    });
  };

  const destroyEditor = () => {
    if (editor.value) {
      editor.value.destroy();
      editor.value = null;
      console.log('useTiptapEditor: Editor instance destroyed.');
    }
  };

  // Gérer le cycle de vie dans le composable
  onMounted(() => {
    console.log('useTiptapEditor: Mounted, initializing editor...');
    initializeEditor();
  });

  onBeforeUnmount(() => {
    console.log('useTiptapEditor: Before unmount, destroying editor...');
    // Note: La sauvegarde avant destruction sera gérée par useChapterContent
    destroyEditor();
  });

  // Exposer l'instance de l'éditeur et les fonctions de contrôle
  return {
    editor,
    initializeEditor, // Peut être utile si on veut réinitialiser avec un contenu différent
    destroyEditor,
  };
}