# Jeu basé sur le jeu de la vie de John Conway

Voilà, faudra faire des ajouts ici pour que nous mêmes sachions ce qu'on doit faire mdr, j'ai déjà commencé un document où j'ajoute mes idées mais voilà

## Lancer

Pour lancer via VSCode le projet, **dupliquez** (pas renommer) le fichier `launch.json.default` dans le dossier `.vscode` et enlevez l'extension *.default* sur ce second fichier.<br>
Dans l'onglet **Run And Debug**, choisir la bonne configuration, et lancer.<br>
Dans une console s'ouvre alors en mode interactif (on peut envoyer des commandes Python pendant qu'il s'exécute) le fichier `main.py`, point d'entrée du programme.<br>
Une fois fini, écrire dans la console stop(), qui fermera le serveur Web, une fois que le processus Python disparaît, on peut alors terminer la session de Degug avec *F8* ou en cliquant sur le carré rouge.<br>
Si vous voulez apporter des modifications aux configurations, modifiez dans `launch.json`, si vous pensez que ça peut être utile à tout le monde, ajoutez dans `launch.json.default` et publiez les changements.<br>

Pour lancer via la console simplement, exécuter cette commande en se situant dans le dossier `/src/` du projet, sinon adaptez la commande:
`PYTHONPATH=./libs/ python3 -i ./server/main.py`.<br>
Pour stopper le serveur, écrire la commande `stop()` dans le terminal intéractif et attendre que le processus Python soit fini, sinon les ports utilisés par le processus resteront utilisés et ne pourront pas être réutilisés.<br>
