# Structure base de données

Tous les mondes sont stockées dans la même base de données, `mondes.db`

Une première table `worlds` stocke les différents mondes:

```SQL
CREATE TABLE worlds (
    name VARCHAR PRIMARY KEY,
    layer_count INT,

);
```

On crée aussi une table `layers` qui contient les couches de chaque monde :
```SQL
CREATE TABLE layers (
    world VARCHAR,
    layer_index INT,
    tilesheet TEXT, -- Chemin vers le dossier des images, exemple: "assets/tilesheets/interior/"
    PRIMARY KEY (world, layer_index)
);
```

Puis une autre table stocke les blocs, eux-mêmes contenant des tiles, des NPC ou des ennemis :

```SQL
CREATE TABLE blocks (
    block_id INTEGER PRIMARY KEY AUTOINCREMENT,
    block_x INT,
    block_y INT,
    world VARCHAR,
    layer_index INT,
    FOREIGN KEY (world, layer_index) REFERENCES layers(world, layer_index)
);

CREATE TABLE tiles (
    tile_id INTEGER PRIMARY KEY AUTOINCREMENT,
    block_id INT,
    x INT,
    y INT,
    image_name TEXT, -- Par exemple: "interior_001.png", pour récupérer le fichier image: layer.tilesheet + image_name
    FOREIGN KEY (block_id) REFERENCES blocks(block_id)
);

CREATE TABLE NPCs (
    npc_id INTEGER PRIMARY KEY AUTOINCREMENT,
    block_id INT,
    x INT,
    y INT,
    npc_name VARCHAR, -- On suppose pour l'instant que les dialogues sont récupérés par rapport au nom des NPC, chaque nom étant donc unique
    npc_image TEXT,
    FOREIGN KEY (block_id) REFERENCES blocks(block_id)
);

CREATE TABLE ennemies (
    ennemy_id INTEGER PRIMARY KEY AUTOINCREMENT,
    block_id INT,
    x INT,
    y INT,
    ennemy_type VARCHAR, -- Suppose qu'il existe une table avec les types d'ennemis et leurs attributs
    FOREIGN KEY (block_id) REFERENCES blocks(block_id)
);
```
