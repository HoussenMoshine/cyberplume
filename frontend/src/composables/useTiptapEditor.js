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
 * Insère du texte brut dans l'éditeur en créant des paragraphes pour chaque ligne.
 * @param {import('@tiptap/vue-3').Editor} editorInstance - L'instance de l'éditeur.
 * @param {string} text - Le texte à insérer.
 * @param {boolean} deleteSelection - Faut-il supprimer la sélection actuelle ?
 */
function insertTextAsParagraphs(editorInstance, text, deleteSelection = false) {
  if (!editorInstance || !text) return;

  const { state, dispatch } = editorInstance.view;
  let tr = state.tr;

  if (deleteSelection) {
    tr = tr.deleteSelection();
  }

  const lines = text.split('\n');

  lines.forEach((line, index) => {
    const trimmedLine = line.trim();
    // Ne pas créer de paragraphe pour la première ligne si le curseur est déjà
    // au début d'un bloc vide, pour éviter un paragraphe vide en haut.
    const { from } = tr.selection;
    const isFirstLine = index === 0;
    const isCursorAtStartOfEmptyBlock = from === tr.doc.resolve(from).start() && tr.doc.nodeAt(from - 1)?.content.size === 0;

    if (!isFirstLine || !isCursorAtStartOfEmptyBlock) {
       tr = tr.split(tr.selection.from, 1);
    }
    
    if (trimmedLine) {
      tr = tr.insertText(trimmedLine, tr.selection.from);
    }
  });

  dispatch(tr);
}


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
          event.preventDefault();
          const text = event.clipboardData.getData('text/plain');
          insertTextAsParagraphs(editor.value, text, true);
          return true;
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

  const applySuggestion = (suggestion) => {
    if (!editor.value || !suggestion) return;

    const { original_text, suggested_text } = suggestion;

    const content = editor.value.getHTML();
    
    // On ne peut pas se fier aux index car ils sont basés sur le texte brut
    // et non sur le HTML de l'éditeur. On va donc remplacer la première
    // occurrence du texte original. C'est une solution imparfaite mais
    // plus robuste que le calcul d'index.
    
    // Pour éviter de remplacer du HTML, on travaille sur le texte brut de l'éditeur
    const textContent = editor.value.getText();
    const startIndex = textContent.indexOf(original_text);

    if (startIndex === -1) {
        console.error("Le texte original de la suggestion n'a pas été trouvé dans l'éditeur.", suggestion);
        // On pourrait afficher un snackbar ici pour informer l'utilisateur.
        return;
    }

    // Les index de Tiptap sont 1-based.
    const from = startIndex + 1;
    const to = from + original_text.length;

    editor.value
      .chain()
      .focus()
      .setTextSelection({ from, to })
      .insertContent(suggested_text)
      .run();
  };

  // Exposer la fonction d'insertion pour les actions IA
  const insertAIText = (text) => {
    if (!editor.value) return;
    const deleteSel = !editor.value.state.selection.empty;
    insertTextAsParagraphs(editor.value, text, deleteSel);
  };

  return {
    editor,
    initializeEditor, 
    destroyEditor,
    applySuggestion,
    insertAIText, // Exposer la nouvelle fonction d'insertion
  };
}