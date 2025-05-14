// Configuração do marked
marked.setOptions({
  breaks: true,
  gfm: true,
});

const editor = document.getElementById("editor");
const preview = document.getElementById("preview");

// Debounce para melhorar performance
let updateTimeout;
const updatePreview = () => {
  preview.innerHTML = marked.parse(editor.value);
};

const debouncedUpdate = () => {
  clearTimeout(updateTimeout);
  updateTimeout = setTimeout(updatePreview, 100);
};

// Atualiza o preview quando o conteúdo muda
editor.addEventListener("input", debouncedUpdate);

// Atualiza o preview inicial
updatePreview();

// Mantém o scroll sincronizado
editor.addEventListener("scroll", () => {
  preview.scrollTop = editor.scrollTop;
});

// Garante que o editor sempre tenha foco
editor.addEventListener("blur", () => {
  editor.focus();
});

// Foca no editor quando a página carrega
window.addEventListener("load", () => {
  editor.focus();
});

// Suporte básico para tabulação
editor.addEventListener("keydown", (e) => {
  if (e.key === "Tab") {
    e.preventDefault();
    const start = editor.selectionStart;
    const end = editor.selectionEnd;
    editor.value =
      editor.value.substring(0, start) + "    " + editor.value.substring(end);
    editor.selectionStart = editor.selectionEnd = start + 4;
    updatePreview();
  }
});
