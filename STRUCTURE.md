# Structure

À partir du dossier racine :

# `/src/`

Source du projet pour le site et le serveur Web

## `./content/`

Contenu pour le projet, ne changent pas pendant le gameplay.<br>
Pour que les ressources s'accèdent entre elles, on utilise un chemin relatif, à partir de l'emplacement du fichier qui cherche un autre fichier.<br>
Pour qu'un fichier Python accède aux ressources, on écrit par exemple : <code>content/pages/index.html</code>.

### `./pages/`

HTML

### `./styles/`

CSS

### `./scripts`

JS

### `./assets/`

Ressources visuelles :

- `./tilesheets/` : Visuels pour la map
- `./spritesheets/` : Visuels pour les personnages
- `./gui/` : Visuels pour l’interface

### `./data/`

Ressources autres (JSON) :


- `./attributes/` : Attributs
    - `./characters/` : Attributs sur les personnages
        - `./enemies/` : Attributs sur les ennemis
        - `./bosses/` : Attributs sur les boss
        - `./npc/` : Attributs sur les personnages non-jouable
        - `./player/` : Attributs sur le joueur
    - `./common/` : Attributs divers
    - `./worlds/` : Attributs sur les mondes

- `./databases/` : Bases de données

- `./lang/` : Textes :
    - `./fr/` : Français
        - `./dialogs/` : Dialogues
    - `./en/` : Anglais
        - `./dialogs/` : Dialogues

## `./libs/`

Librairies, comme WSinter.

## `./server/`

Gère les requêtes HTTP, le jeu, etc. Tout le code Python y est.<br>
Afin d'utiliser des fichiers à l'intérieur des sous-dossiers, on écrit : <code>import subfolder.file</code> et pour utiliser des éléments du fichier : <code>subfolder.file.function(subfolder.file.variable)</code>.<br>
**Ainsi, un fichier plus bas dans l'arborescence ne peut pas dépendre d'un fichier plus haut que lui.**<br>
*Exemple: Un fichier dans `/src/server/accounts/` ne peut pas dépendre d'un fichier dans `/src/server/` ou pire dans `/src/server/web/`.*

### `./accounts/`

Gère la connexion et la création de comptes

### `./graphics`

Gère l’affichage

- `./characters/` Gère l’affichage des personnages
- `./effects/` : Gère l’affichage des effets, sorts, mana, etc.
- `./world/` : Gère l’affichage du monde

### `./multiplayer/`

Gère s’il y en a un, le multijoueur

### `./resources/`

Gère l’accès aux ressources

### `./web/`

Gestionnaire de WSinter
