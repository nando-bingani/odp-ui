import {Editor} from 'https://esm.sh/@tiptap/core'
import Document from 'https://esm.sh/@tiptap/extension-document'
import Paragraph from 'https://esm.sh/@tiptap/extension-paragraph'
import Text from 'https://esm.sh/@tiptap/extension-text'
import Bold from 'https://esm.sh/@tiptap/extension-bold'
import Italic from 'https://esm.sh/@tiptap/extension-italic'
import Underline from 'https://esm.sh/@tiptap/extension-underline'
import Subscript from 'https://esm.sh/@tiptap/extension-subscript'
import Superscript from 'https://esm.sh/@tiptap/extension-superscript'

export function createEditor(elementId, content) {
    return new Editor({
        element: document.querySelector(`#${elementId}`),
        content: content,
        extensions: [
            Document,
            Paragraph,
            Text,
            Bold,
            Italic,
            Underline,
            Subscript,
            Superscript,
        ],
        editorProps: {
            attributes: {
                class: 'prose prose-sm sm:prose lg:prose-lg xl:prose-2xl mx-auto focus:outline-none ' +
                    'border',
            },
        },
    });
}
