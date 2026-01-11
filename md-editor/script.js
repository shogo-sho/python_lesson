document.addEventListener('DOMContentLoaded', () => {
    const editor = document.getElementById('editor');
    const preview = document.getElementById('preview');

    // Key for localStorage
    const STORAGE_KEY = 'markdown-content';

    // Load saved content from localStorage
    const savedContent = localStorage.getItem(STORAGE_KEY);
    if (savedContent) {
        editor.value = savedContent;
        updatePreview(savedContent);
    } else {
        // Default welcome text if empty
        const defaultText = "# Welcome to Markdown Editor\n\nStart typing on the left to see the result on the right.\n\n- [x] Real-time preview\n- [x] Dark mode\n- [x] Auto-save";
        editor.value = defaultText;
        updatePreview(defaultText);
    }

    // Event listener for real-time updates
    editor.addEventListener('input', (e) => {
        const content = e.target.value;
        updatePreview(content);
        saveContent(content);
    });

    // Function to update the preview area
    function updatePreview(markdown) {
        // marked is available globally via CDN
        preview.innerHTML = marked.parse(markdown);
    }

    // Function to save content to localStorage
    function saveContent(content) {
        localStorage.setItem(STORAGE_KEY, content);
    }
});
