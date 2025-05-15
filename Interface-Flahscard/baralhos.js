document.addEventListener("DOMContentLoaded", function() {
    // Elementos do DOM
    const deckList = document.getElementById('deck-list');
    const searchInput = document.querySelector('.search-input');
    const createDeckBtn = document.querySelector('.action-button:first-child');
    
    // Array para armazenar os baralhos
    let decks = [];

    // Carrega baralhos do localStorage
    function loadDecks() {
        const savedDecks = localStorage.getItem('decks');
        if (savedDecks) {
            decks = JSON.parse(savedDecks);
            renderDecks();
        } else {
            // Decks iniciais (opcional)
            decks = [
                {name: "Segunda guerra mundial", cards: []},
                {name: "Guerra fria", cards: []},
                {name: "Revolução Industrial", cards: []},
                {name: "Geografia do Brasil", cards: []}
            ];
            saveDecks();
            renderDecks();
        }
    }

    // Renderiza a lista de baralhos
    function renderDecks(filteredDecks = null) {
        deckList.innerHTML = '';
        const decksToRender = filteredDecks || decks;
        
        decksToRender.forEach((deck, index) => {
            const deckElement = document.createElement('div');
            deckElement.className = 'search-term';
            deckElement.innerHTML = `
                <span class="deck-name" data-index="${index}">${deck.name}</span>
                <div class="term-icons">
                    <i class="fas fa-edit edit-deck" title="Editar" data-index="${index}"></i>
                    <i class="fas fa-trash-alt delete-deck" title="Excluir" data-index="${index}"></i>
                </div>
            `;
            deckList.appendChild(deckElement);
        });

        // Adiciona eventos
        addDeckNameEvents();
        addEditEvents();
        addDeleteEvents();
    }

    // Adiciona evento de clique nos nomes dos decks
    function addDeckNameEvents() {
        document.querySelectorAll('.deck-name').forEach(deckName => {
            deckName.addEventListener('click', function() {
                const index = this.getAttribute('data-index');
                openDeck(index);
            });
        });
    }

    // Redireciona para a interface do deck
    function openDeck(index) {
        // Armazena o deck selecionado no localStorage
        localStorage.setItem('selectedDeck', JSON.stringify(decks[index]));
        // Redireciona para a página dos flashcards
        window.location.href = 'interface.flashcard2.html';
    }

    // Adiciona evento de edição
    function addEditEvents() {
        document.querySelectorAll('.edit-deck').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.stopPropagation(); // Previne que o evento do deck-name seja acionado
                const index = this.getAttribute('data-index');
                editDeck(index);
            });
        });
    }

    // Adiciona evento de exclusão
    function addDeleteEvents() {
        document.querySelectorAll('.delete-deck').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.stopPropagation(); // Previne que o evento do deck-name seja acionado
                const index = this.getAttribute('data-index');
                deleteDeck(index);
            });
        });
    }

    // Cria novo baralho
    function createNewDeck() {
        const deckName = prompt("Digite o nome do novo baralho:");
        if (deckName && deckName.trim()) {
            decks.push({
                name: deckName.trim(),
                cards: []
            });
            saveDecks();
            renderDecks();
        }
    }

    // Edita baralho existente
    function editDeck(index) {
        const newName = prompt("Editar nome do baralho:", decks[index].name);
        if (newName && newName.trim()) {
            decks[index].name = newName.trim();
            saveDecks();
            renderDecks();
        }
    }

    // Exclui baralho
    function deleteDeck(index) {
        if (confirm(`Tem certeza que deseja excluir o baralho "${decks[index].name}"?`)) {
            decks.splice(index, 1);
            saveDecks();
            renderDecks();
        }
    }

    // Filtra baralhos
    function filterDecks(searchTerm) {
        const filtered = decks.filter(deck => 
            deck.name.toLowerCase().includes(searchTerm.toLowerCase())
        );
        renderDecks(filtered);
    }

    // Salva no localStorage
    function saveDecks() {
        localStorage.setItem('decks', JSON.stringify(decks));
    }

    // Event Listeners
    createDeckBtn.addEventListener('click', createNewDeck);
    
    searchInput.addEventListener('input', function() {
        filterDecks(this.value);
    });

    // Inicialização
    loadDecks();
});