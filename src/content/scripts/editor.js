board = document.getElementById("board");

worldSelect = document.getElementById("world");
layerContainer = document.getElementById("layers");
selected = null;
indexInput = document.getElementById("index");
collisionsCheck = document.getElementById("collisions");
createLayerButton = document.getElementById("add");

tileset = document.getElementById("tileset");
tilesetSelect = document.getElementById("tileset-choice");
brush = null;

worldSelect.addEventListener("change", (event) => {
    transmettre("world_changed", event.target.value);
});

function addLayers(layers) {
    layers.forEach(element => {
        addLayer(element);
    });
}

function addLayer(layer) {
    // layer: [index: int, tileset: str, collisions: boolean]
    parent = document.createElement("div");
    parent.classList.add("layer");
    parent.id = "layer_option_" + String(layer[0])
    
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
        if (selected != null && selected != undefined)
        {
            selected.classList.remove("selected");
        }
        this.classList.add("selected");
        selected = this;
        transmettre("layer_changed", this.children[0].innerText);
    });
    layerContainer.appendChild(parent);
}

add.addEventListener("click", (_) => {
    let index = indexInput.value;
    // On verifie qu'il n'y ait pas d'autres couche avec le meme indice
    let children = layerContainer.children;
    for (let i = 0; i < children.length; i++)
    {
        if (children[i].children[0].innerText == index)
        {
            return;
        }
    }
    let tileset = tilesetSelect.value;
    let collisions = collisionsCheck.value;
    addLayer([index, tileset, collisions]);

    // On les ajoute au div#board
    /*layer = document.createElement("div");
    layer.id = "layer_" + String(index);
    // On multiplie par 2 pour laisser de la place au joueur si besoin
    layer.style["z-index"] = index * 2;
    board.appendChild(layer);*/

    transmettre("create_layer", [index, tileset, collisions])
});

window.addEventListener("keyup", (event) => {
    if (event.key == "Backspace" || event.key == "Delete") {
        if (confirm("Voulez-vous vraiment supprimer cette couche ?\nCette action sera définitive!")) {
            transmettre("delete_layer", selected.children[0].innerText);
        }
    }
});

function addTilesEvent() {
    children = tileset.children;
    for (let i = 0; i < children.length; i++) {
        children[i].addEventListener("click", (e) => {
            if (brush != null && brush != undefined) {
                brush.classList.remove("brush");
            }
            e.target.classList.add("brush");
            brush = e.target;
            src = e.target.src;
            // On ne recupere que le fichier image
            transmettre("tile_changed", src.substring(src.lastIndexOf("/") + 1));
        });
    }
}
