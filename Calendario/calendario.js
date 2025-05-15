// Inicialização quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    // Seleção de elementos do calendário
    const currentMonthEl = document.getElementById('current-month');
    const calendarDays = document.getElementById('calendar-days');
    const prevMonthBtn = document.getElementById('prev-month');
    const nextMonthBtn = document.getElementById('next-month');
    const todayBtn = document.getElementById('today-button');
    
    // Seleção de elementos do modal
    const modalOverlay = document.getElementById('modal-overlay');
    const closeModalBtn = document.getElementById('close-modal');
    const modalDate = document.getElementById('modal-date');
    const eventsList = document.getElementById('events-list');
    const eventInput = document.getElementById('event-input');
    const addEventBtn = document.getElementById('add-event-btn');
    
    // Variáveis de estado
    let currentDate = new Date();
    let selectedDate = null;
    let events = JSON.parse(localStorage.getItem('calendarEvents')) || {};
    
    // Função principal para renderizar o calendário
    function renderCalendar() {
        // Cálculos de datas para o mês atual
        const firstDay = new Date(
            currentDate.getFullYear(),
            currentDate.getMonth(),
            1
        );
        
        const lastDay = new Date(
            currentDate.getFullYear(),
            currentDate.getMonth() + 1,
            0
        );
        
        const prevLastDay = new Date(
            currentDate.getFullYear(),
            currentDate.getMonth(),
            0
        );
        
        // Informações sobre o mês
        const monthDays = lastDay.getDate();
        const prevMonthDays = prevLastDay.getDate();
        const firstDayIndex = firstDay.getDay();
        const lastDayIndex = lastDay.getDay();
        
        // Nomes dos meses
        const months = [
            "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
        ];
        
        // Atualiza o título do mês
        currentMonthEl.textContent = `${months[currentDate.getMonth()]} ${currentDate.getFullYear()}`;
        
        let days = "";
        
        // Adiciona dias do mês anterior
        for (let i = firstDayIndex; i > 0; i--) {
            days += `<div class="day other-month">${prevMonthDays - i + 1}</div>`;
        }
        
        // Adiciona dias do mês atual
        const today = new Date();
        for (let i = 1; i <= monthDays; i++) {
            const dateKey = `${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, '0')}-${String(i).padStart(2, '0')}`;
            const dayEvents = events[dateKey] || [];
            const isToday = 
                i === today.getDate() && 
                currentDate.getMonth() === today.getMonth() && 
                currentDate.getFullYear() === today.getFullYear();
            
            // Gera abreviações para os eventos do dia
            let eventAbbreviations = '';
            if (dayEvents.length > 0) {
                eventAbbreviations = '<div class="event-abbreviations">';
                for (let j = 0; j < Math.min(3, dayEvents.length); j++) {
                    const event = dayEvents[j];
                    eventAbbreviations += 
                        `<div class="event-abbreviation" title="${event}">
                            ${event.substring(0, 8).toUpperCase()}
                        </div>`;
                }
                eventAbbreviations += '</div>';
            }
            
            // Adiciona o dia ao calendário
            days += `
                <div class="day ${isToday ? 'today' : ''}">
                    <div class="day-number">${i}</div>
                    ${eventAbbreviations}
                </div>
            `;
        }
        
        // Adiciona dias do próximo mês
        for (let i = 1; i <= 6 - lastDayIndex; i++) {
            days += `<div class="day other-month">${i}</div>`;
        }
        
        // Atualiza o DOM
        calendarDays.innerHTML = days;
        setupDayClickListeners();
    }
    
    // Funções para manipulação de eventos
    function getDateKey(date) {
        return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
    }
    
    // Exibe eventos de um dia específico no modal
    function showDayEvents(date) {
        const dateKey = getDateKey(date);
        const dayEvents = events[dateKey] || [];
        
        // Formata a data para exibição
        const options = { day: 'numeric', month: 'long', year: 'numeric' };
        modalDate.textContent = date.toLocaleDateString('pt-BR', options);
        
        // Limpa e preenche a lista de eventos
        eventsList.innerHTML = '';
        dayEvents.forEach((event, index) => {
            const eventElement = document.createElement('div');
            eventElement.className = 'event-item';
            eventElement.innerHTML = `
                <span>${event}</span>
                <button class="delete-event-btn" data-index="${index}">Excluir</button>
            `;
            eventsList.appendChild(eventElement);
        });
        
        // Adiciona listeners para os botões de exclusão
        document.querySelectorAll('.delete-event-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                deleteEvent(date, parseInt(this.getAttribute('data-index')));
            });
        });
    }
    
    // Adiciona um novo evento
    function addEvent(date, eventText) {
        if (!eventText.trim()) return;
        
        const dateKey = getDateKey(date);
        if (!events[dateKey]) {
            events[dateKey] = [];
        }
        
        events[dateKey].push(eventText);
        localStorage.setItem('calendarEvents', JSON.stringify(events));
        showDayEvents(date);
        eventInput.value = '';
        renderCalendar();
    }
    
    // Remove um evento
    function deleteEvent(date, index) {
        const dateKey = getDateKey(date);
        if (events[dateKey]) {
            events[dateKey].splice(index, 1);
            localStorage.setItem('calendarEvents', JSON.stringify(events));
            showDayEvents(date);
            renderCalendar();
        }
    }
    
    // Configura listeners para os dias do calendário
    function setupDayClickListeners() {
        document.querySelectorAll('.day:not(.other-month)').forEach(day => {
            day.addEventListener('click', function() {
                const dayNumber = parseInt(this.querySelector('.day-number').textContent);
                selectedDate = new Date(
                    currentDate.getFullYear(),
                    currentDate.getMonth(),
                    dayNumber
                );
                
                showDayEvents(selectedDate);
                modalOverlay.classList.add('active');
                eventInput.focus();
            });
        });
    }
    
    // Event listeners para navegação
    prevMonthBtn.addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() - 1);
        renderCalendar();
    });
    
    nextMonthBtn.addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() + 1);
        renderCalendar();
    });
    
    todayBtn.addEventListener('click', () => {
        currentDate = new Date();
        renderCalendar();
    });
    
    // Event listeners para o modal
    closeModalBtn.addEventListener('click', () => {
        modalOverlay.classList.remove('active');
    });
    
    eventInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && selectedDate) {
            addEvent(selectedDate, eventInput.value);
        }
    });
    
    addEventBtn.addEventListener('click', () => {
        if (selectedDate) {
            addEvent(selectedDate, eventInput.value);
        }
    });
    
    modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) {
            modalOverlay.classList.remove('active');
        }
    });
    
    // Inicializa o calendário
    renderCalendar();
});