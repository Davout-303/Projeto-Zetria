
class ZetriaAPI {
    constructor() {
        this.baseURL = window.location.origin;
    }

    
    async getFlashcards(notaId = null) {
        try {
            const url = notaId ? `/api/flashcards?nota_id=${notaId}` : '/api/flashcards';
            const response = await fetch(url);
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Erro ao buscar flashcards:', error);
            return { success: false, error: error.message };
        }
    }

    async createFlashcard(notaId, frontContent, backContent) {
        try {
            const response = await fetch('/api/flashcards', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    nota_id: notaId,
                    front_content: frontContent,
                    back_content: backContent
                })
            });
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Erro ao criar flashcard:', error);
            return { success: false, error: error.message };
        }
    }

    
    async getTasks() {
        try {
            const response = await fetch('/api/tasks');
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Erro ao buscar tarefas:', error);
            return { success: false, error: error.message };
        }
    }

    async createTask(title, description, dueDate, recurring = false, recurrenceRule = '') {
        try {
            const response = await fetch('/api/tasks', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    title: title,
                    description: description,
                    due_date: dueDate,
                    recurring: recurring,
                    recurrence_rule: recurrenceRule
                })
            });
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Erro ao criar tarefa:', error);
            return { success: false, error: error.message };
        }
    }

    async updateTask(taskId, completed) {
        try {
            const response = await fetch(`/api/tasks/${taskId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    completed: completed
                })
            });
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Erro ao atualizar tarefa:', error);
            return { success: false, error: error.message };
        }
    }

    async deleteTask(taskId) {
        try {
            const response = await fetch(`/api/tasks/${taskId}`, {
                method: 'DELETE'
            });
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Erro ao deletar tarefa:', error);
            return { success: false, error: error.message };
        }
    }
}


const zetriaAPI = new ZetriaAPI();


function showMessage(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    const container = document.querySelector('.container') || document.body;
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR') + ' ' + date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
}


async function loadFlashcards(notaId = null) {
    const result = await zetriaAPI.getFlashcards(notaId);
    if (result.success) {
        displayFlashcards(result.flashcards);
    } else {
        showMessage('Erro ao carregar flashcards: ' + result.error, 'danger');
    }
}

function displayFlashcards(flashcards) {
    const container = document.getElementById('flashcards-container');
    if (!container) return;

    container.innerHTML = '';
    
    if (flashcards.length === 0) {
        container.innerHTML = '<p>Nenhum flashcard encontrado.</p>';
        return;
    }

    flashcards.forEach(flashcard => {
        const flashcardElement = createFlashcardElement(flashcard);
        container.appendChild(flashcardElement);
    });
}

function createFlashcardElement(flashcard) {
    const div = document.createElement('div');
    div.className = 'flashcard';
    div.innerHTML = `
        <div class="flashcard-inner">
            <div class="flashcard-front">
                <p>${flashcard.front_content}</p>
            </div>
            <div class="flashcard-back">
                <p>${flashcard.back_content}</p>
            </div>
        </div>
    `;
    
    div.addEventListener('click', () => {
        div.classList.toggle('flipped');
    });
    
    return div;
}


async function loadTasks() {
    const result = await zetriaAPI.getTasks();
    if (result.success) {
        displayTasks(result.tasks);
    } else {
        showMessage('Erro ao carregar tarefas: ' + result.error, 'danger');
    }
}

function displayTasks(tasks) {
    const container = document.getElementById('tasks-container');
    if (!container) return;

    container.innerHTML = '';
    
    if (tasks.length === 0) {
        container.innerHTML = '<p>Nenhuma tarefa encontrada.</p>';
        return;
    }

    tasks.forEach(task => {
        const taskElement = createTaskElement(task);
        container.appendChild(taskElement);
    });
}

function createTaskElement(task) {
    const div = document.createElement('div');
    div.className = `task-item ${task.completed ? 'completed' : ''}`;
    div.innerHTML = `
        <div class="task-content">
            <h4>${task.title}</h4>
            <p>${task.description || ''}</p>
            ${task.due_date ? `<small>Prazo: ${formatDate(task.due_date)}</small>` : ''}
        </div>
        <div class="task-actions">
            <button onclick="toggleTask(${task.id}, ${!task.completed})" class="btn-toggle">
                ${task.completed ? 'Reabrir' : 'Concluir'}
            </button>
            <button onclick="deleteTaskConfirm(${task.id})" class="btn-delete">Excluir</button>
        </div>
    `;
    
    return div;
}

async function toggleTask(taskId, completed) {
    const result = await zetriaAPI.updateTask(taskId, completed);
    if (result.success) {
        showMessage('Tarefa atualizada com sucesso!', 'success');
        loadTasks(); 
    } else {
        showMessage('Erro ao atualizar tarefa: ' + result.error, 'danger');
    }
}

async function deleteTaskConfirm(taskId) {
    if (confirm('Tem certeza que deseja excluir esta tarefa?')) {
        const result = await zetriaAPI.deleteTask(taskId);
        if (result.success) {
            showMessage('Tarefa excluída com sucesso!', 'success');
            loadTasks(); 
        } else {
            showMessage('Erro ao excluir tarefa: ' + result.error, 'danger');
        }
    }
}


function setupFlashcardForm() {
    const form = document.getElementById('flashcard-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(form);
        const notaId = formData.get('nota_id');
        const frontContent = formData.get('front_content');
        const backContent = formData.get('back_content');
        
        const result = await zetriaAPI.createFlashcard(notaId, frontContent, backContent);
        if (result.success) {
            showMessage('Flashcard criado com sucesso!', 'success');
            form.reset();
            loadFlashcards(); 
        } else {
            showMessage('Erro ao criar flashcard: ' + result.error, 'danger');
        }
    });
}

function setupTaskForm() {
    const form = document.getElementById('task-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(form);
        const title = formData.get('title');
        const description = formData.get('description');
        const dueDate = formData.get('due_date');
        const recurring = formData.get('recurring') === 'on';
        const recurrenceRule = formData.get('recurrence_rule');
        
        const result = await zetriaAPI.createTask(title, description, dueDate, recurring, recurrenceRule);
        if (result.success) {
            showMessage('Tarefa criada com sucesso!', 'success');
            form.reset();
            loadTasks(); 
        } else {
            showMessage('Erro ao criar tarefa: ' + result.error, 'danger');
        }
    });
}


document.addEventListener('DOMContentLoaded', function() {
    
    setupFlashcardForm();
    setupTaskForm();
    
    
    if (document.getElementById('flashcards-container')) {
        loadFlashcards();
    }
    
    if (document.getElementById('tasks-container')) {
        loadTasks();
    }
});

