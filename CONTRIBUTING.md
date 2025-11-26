# GitHub

## Cloner le projet

En ouvrant VSCode, cherchez "Cloner le projet" : https://github.com/POOcalypseTeam/POOcalypse.

Attention, si vous pouvez pas vous connecter à votre compte GitHub, il faut utiliser un token, celui qui vous a été donné. Pour l'utiliser il faut aller dans un terminal et taper :<br>
<code>git remote set-url origin https://%USER%:%TOKEN%@github.com/POOCalypseTeam/POOcalypse.git</code> en remplacant `%TOKEN%` par le token, et `%USER%` par votre nom d'utilisateur, si vous voulez éviter de taper le token manuellement, remplacez `%TOKEN%` par <code>$(cat chemin/relatif/vers/token)</code><br>
Puis ensuite il faut config une adresse mail et un nom d'utilisateur, l'adresse peut etre vide mais au moins le nom d'utilisateur:<br>
<code>git config user.name "NOM" && git config user.email "EMAIL"</code>

Prendre connaissance de `README.md`.

## Synchroniser 

À chaque fois que vous retournez sur le projet, il faut synchroniser les changements avec ce qui a été envoyé sur le serveur. Donc il faut aller dans l'onglet à gauche (pour les gens normalement constitués) représentant deux branches qui se séparent. Dans la partie du bas il faut cliquer sur le bouton Pull (tirer les changements du serveur), les fichiers en local seront actualisés.

## Enregistrer changements

Une fois que les changements ont été faits, il faut les publier, pour faire ça, il faut retourner dans l'onglet de Git, vos changements seront listés et il faut maintenant donner une courte description aux changements puis cliquer sur Commit, les changements sont donc enregistrés.

## Envoyer changements

Maintenant que les changements sont enregistrés, il ne reste plus qu'à Push (pousser les commits sur le serveur). Pour faire cette étape, il faut bien que vous pensiez à vous connectez à votre compte GitHub, ou à enregistrer le token dans l'url de l'origin (étape plus haut).

## Branches

En gros pour pouvoir bosser à plusieurs sur le projet il faut faire des branches, sinon si plusieurs personnes avancent de leur côté et qu'on veut ensuite rejoindre leurs changements c'est pas trop possible facilement. *Ex: Deux personnes A et B travaillent sur des features différentes, la personne A fini et envoie ses changements, puis la personne B fini mais n'a pas les changements de la personne A, comment on fait ?* C'est là qu'interviennent les branches, en pratique chaque feature est sur une branche, et on fait tous les commits des features sur une branche. C'est seulement une fois finie que la branche va être Merge à master ou à main (branche principale pour GitHub), on fait ça en utilisant des Pull Request, ça permet de gérer les conflits (2 fichiers modifiés par plusieurs branches) plus facilement. Aussi ça permet de lancer des tests automatiques via GitHub avec les Actions, par exemple pour faire des doctests mais plus poussés avec un serveur par exemple, enfin bref on verra si on utilise ça ou pas.<br>
Ainsi la branche master contient une version finale dont on est sûr qu'elle marche et a des features qu'on peut qualifier de complètes, du moins c'est la version la plus finale qu'on pourrait avoir.

D'ailleurs pour créer une nouvelle branche c'est :<br>
<code>git branch NOM_BRANCHE COMMIT_DEPART</code>, ça permet de baser une branche à partir d'un commit, pour savoir l'id du commit il faut le choisir dans <code>git log</code>, logiquement c'est un truc assez long en hexadécimal.


# Structure

Voici la structure des dossiers du projet, à noter qu'elle n'est pas définitive étant donnée l'avancée du projet.

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

- `./tilesets/` : Visuels pour la map
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

