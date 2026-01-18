worldSelect = document.getElementById("world");
layerContainer = document.getElementById("layers");

worldSelect.addEventListener("change", (event) => {
    transmettre("world_changed", event.target.value);
});

function addLayers(layers) {
    layers.forEach(element => {
        addLayer(element);
    });
    layerContainer.children[0].classList.add("selected");
}

function addLayer(layer) {
    // layer: [index: int, tileset: str, collisions: boolean]
    parent = document.createElement("div");
    parent.classList.add("layer");
    
    layerText = document.createElement("p");
    layerText.innerText = layer[0];
    
    tilesetText = document.createElement("p");
    tilesetText.innerText = layer[1];
    
    enabledInput = document.createElement("input");
    enabledInput["type"] = "checkbox";
    enabledInput["name"] = "enabled";
    enabledInput["id"] = "enabled-" + layer[0];
    
    parent.appendChild(layerText);
    parent.appendChild(tilesetText);
    parent.appendChild(enabledInput);
    // On utilise function(event) et pas (event) =>
    // Sinon il n'y a pas de `this` et event.target se réfère à l'élément clické
    // Donc pas forcément parent, mais peut-être le texte enfant
    parent.addEventListener("click", function(_) {
        transmettre("layer_change", this.children[0].innerText);
    });
    layerContainer.appendChild(parent);
}