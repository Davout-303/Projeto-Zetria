// script.js
document.addEventListener('DOMContentLoaded', function() {
    // Criar nós
    const nodes = new vis.DataSet([
        { id: 1, label: "Primeira guerra", shape: "hexagon", color: { background: "#FFE600", border: "#FFE600" } },
        { id: 2, label: "Segunda guerra", shape: "hexagon", color: { background: "#FFE600", border: "#FFE600" } },
        { id: 3, label: "Imperio Otomano", shape: "hexagon", color: { background: "#FFE600", border: "#FFE600" } },
        { id: 4, label: "O cerco de Viena", shape: "hexagon", color: { background: "#FFE600", border: "#FFE600" } },
        { id: 5, label: "Platão", shape: "hexagon", color: { background: "#FFE600", border: "#FFE600" } },
        { id: 6, label: "Aristóteles", shape: "hexagon", color: { background: "#FFE600", border: "#FFE600" } },
    ]);

    // Criar arestas
    const edges = new vis.DataSet([
        { from: 1, to: 2, color: { color: "#FFE600" } },
        { from: 1, to: 3, color: { color: "#FFE600" } },
        { from: 3, to: 4, color: { color: "#FFE600" } },
        { from: 6, to: 5, color: { color: "#FFE600" } },
    ]);

    // Configurar o container
    const container = document.getElementById("graph");
    const data = { nodes, edges };
    const options = {
        nodes: {
            shape: "hexagon",
            size: 20,
            font: { color: "#ffffff", size: 12 },
            borderWidth: 2,
        },
        edges: {
            width: 2,
            smooth: { type: "continuous" },
        },
        physics: {
            stabilization: { iterations: 100 },
            repulsion: { nodeDistance: 150 },
        },
        layout: { 
            randomSeed: 42,
        },
        interaction: {
            hover: true,
        }
    };

    // Criar a rede
    const network = new vis.Network(container, data, options);

    // Adicionar evento de clique
    network.on("click", function(params) {
        if (params.nodes.length > 0) {
            const nodeId = params.nodes[0];
            const node = nodes.get(nodeId);
            alert("Você clicou em: " + node.label);
        }
    });
});