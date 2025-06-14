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
 * @param {string} placeholderText - Texte pour l'extension Placeholder.
 */
export function useTiptapEditor(
  initialContent = '<p style="color: grey; text-align: center;">Sélectionnez un chapitre pour commencer l\'édition.</p>', 
  placeholderText = 'Commencez à écrire votre histoire ici...'
) {
  const editor = ref(null);

  const initializeEditor = (options = {}) => {
    editor.value = new Editor({
      content: options.content || initialContent,
      extensions: [
        StarterKit.configure({
          // heading: { levels: [1, 2, 3] },
        }),
        BubbleMenuExtension.configure({
          pluginKey: 'textActionsBubbleMenu',
           tippyOptions: { duration: 100, placement: 'top-start' },
        }),
        Placeholder.configure({
          placeholder: options.placeholderText || placeholderText,
        }),
        CharacterCount,
        Link.configure({
          openOnClick: true,
          autolink: true,
        }),
        Image.configure({
          // inline: true,
          // allowBase64: true,
        }),
        TextAlign.configure({
          types: ['heading', 'paragraph'],
        }),
        Underline,
        Highlight.configure({ multicolor: true }),
        TaskList,
        TaskItem.configure({
          nested: true,
        }),
        ...(options.extensions || []),
      ],
      editorProps: {
        attributes: {
          class: 'tiptap-editor',
        },
        handlePaste: (view, event, slice) => {
          const text = event.clipboardData.getData('text/plain');
          const html = event.clipboardData.getData('text/html');

          // Si du HTML est collé, laisser TipTap le gérer, sauf si c'est du texte brut qui a été converti.
          // On privilégie le texte brut si le HTML est simple (ex: juste un <p>) pour mieux gérer les sauts de ligne.
          if (html && !text.includes(html.replace(/<[^>]+>/g, ''))) {
             return false; // Laisser TipTap gérer le HTML riche
          }

          if (text) {
            event.preventDefault();
            const paragraphs = text.split(/\n{2,}/g) // Sépare par un ou plusieurs sauts de ligne
                                 .map(p => p.trim())
                                 .filter(p => p.length > 0)
                                 .map(p => `<p>${p}</p>`)
                                 .join('');
            
            editor.value.commands.insertContent(paragraphs);
            return true;
          }

          return false;
        },
      },
      // La sauvegarde automatique onBlur est supprimée pour simplifier la logique
      // et éviter les conditions de concurrence. La sauvegarde se fait manuellement (Ctrl+S, bouton)
      // ou lors du changement de chapitre (géré par useChapterContent).
      // onBlur: ({ editor: blurredEditor }) => {
      //   console.log('useTiptapEditor: Editor blurred');
      //   if (onBlurCallback) {
      //     onBlurCallback(blurredEditor); 
      //   }
      // },
    });
  };

  const destroyEditor = () => {
    if (editor.value) {
      editor.value.destroy();
      editor.value = null;
      console.log('useTiptapEditor: Editor instance destroyed.');
    }
  };

  onBeforeUnmount(() => {
    console.log('useTiptapEditor: Before unmount, destroying editor...');
    destroyEditor();
  });

  return {
    editor,
    initializeEditor, 
    destroyEditor,
  };
}