import { ref, onMounted, onBeforeUnmount } from 'vue';
import { Editor } from '@tiptap/vue-3';
import StarterKit from '@tiptap/starter-kit';
import BubbleMenuExtension from '@tiptap/extension-bubble-menu';
import Placeholder from '@tiptap/extension-placeholder';
import CharacterCount from '@tiptap/extension-character-count';
import Link from '@tiptap/extension-link';
import Image from '@tiptap/extension-image';
import TextAlign from '@tiptap/extension-text-align';
import Underline from '@tiptap/extension-underline';
import Highlight from '@tiptap/extension-highlight';
import TaskList from '@tiptap/extension-task-list';
import TaskItem from '@tiptap/extension-task-item';

/**
 * Composable pour gérer l'instance de l'éditeur TipTap.
 * @param {string|object} initialContent - Le contenu initial de l'éditeur.
 * @param {Function} onBlurCallback - Callback à exécuter lors de l'événement blur de l'éditeur.
 * @param {string} placeholderText - Texte pour l'extension Placeholder.
 */
export function useTiptapEditor(
  initialContent = '<p style="color: grey; text-align: center;">Sélectionnez un chapitre pour commencer l\'édition.</p>', 
  onBlurCallback = null,
  placeholderText = 'Commencez à écrire votre histoire ici...' // Ajout du paramètre
) {
  const editor = ref(null);

  const initializeEditor = (options = {}) => { // Permettre de passer des options supplémentaires
    editor.value = new Editor({
      content: options.content || initialContent,
      extensions: [
        StarterKit.configure({
          // Configurer StarterKit si nécessaire, par exemple pour désactiver certaines extensions par défaut
          // heading: { levels: [1, 2, 3] },
        }),
        BubbleMenuExtension.configure({
          pluginKey: 'textActionsBubbleMenu', // Clé unique pour éviter les conflits
           tippyOptions: { duration: 100, placement: 'top-start' },
        }),
        Placeholder.configure({
          placeholder: options.placeholderText || placeholderText,
        }),
        CharacterCount, // Pas de configuration spécifique nécessaire pour le moment
        Link.configure({
          openOnClick: true, // Comportement commun
          autolink: true,
        }),
        Image.configure({
          // inline: true, // si vous voulez des images en ligne
          // allowBase64: true, // si vous prévoyez d'utiliser des images en base64
        }),
        TextAlign.configure({
          types: ['heading', 'paragraph'], // Appliquer l'alignement aux titres et paragraphes
        }),
        Underline,
        Highlight.configure({ multicolor: true }), // Permettre plusieurs couleurs de surlignage
        TaskList,
        TaskItem.configure({
          nested: true, // Permettre les tâches imbriquées
        }),
        ...(options.extensions || []), // Permettre d'ajouter d'autres extensions dynamiquement
      ],
      editorProps: {
        attributes: {
          class: 'tiptap-editor', 
        },
      },
      onBlur: ({ editor: blurredEditor }) => {
        console.log('useTiptapEditor: Editor blurred');
        if (onBlurCallback) {
          onBlurCallback(blurredEditor); 
        }
      },
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
  // L'initialisation est maintenant appelée par EditorComponent après avoir passé les options
  // onMounted(() => {
  //   console.log('useTiptapEditor: Mounted, editor will be initialized by parent component.');
  //   // initializeEditor(); // Ne plus initialiser ici directement
  // });

  onBeforeUnmount(() => {
    console.log('useTiptapEditor: Before unmount, destroying editor...');
    destroyEditor();
  });

  // Exposer l'instance de l'éditeur et les fonctions de contrôle
  return {
    editor,
    initializeEditor, 
    destroyEditor,
  };
}