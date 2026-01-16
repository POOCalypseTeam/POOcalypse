# POOcalypse

**POOCalypse** est un jeu 2D en vue de dessus dans lequel on incarne un personnage dont le but est de vaincre un méchant boss qui a fait du mal à son village.<br>
Le thème est medieval fantasy et le personnage navigue dans un monde post-apocalyptique, détruit par le méchant boss POO.<br>
En collectant des artefacts et de nouvelles technologies, il sera possible de vaincre des boss de plus en plus imposants, jusqu'à POO....

## Lancer

Pour lancer via VSCode le projet, **dupliquez** (pas renommer) le fichier `launch.json.default` dans le dossier `.vscode` et enlevez l'extension *.default* sur ce second fichier.<br>
Dans l'onglet **Run And Debug**, choisir la bonne configuration, et lancer.<br>
Dans une console s'ouvre alors en mode interactif (on peut envoyer des commandes Python pendant qu'il s'exécute) le fichier `main.py`, point d'entrée du programme.<br>
Une fois fini, écrire dans la console stop(), qui fermera le serveur Web, une fois que le processus Python disparaît, on peut alors terminer la session de Degug avec *F8* ou en cliquant sur le carré rouge.<br>
Si vous voulez apporter des modifications aux configurations, modifiez dans `launch.json`, si vous pensez que ça peut être utile à tout le monde, ajoutez dans `launch.json.default` et publiez les changements.<br>

Pour lancer via la console simplement, exécuter cette commande en se situant dans le dossier `/src/` du projet, sinon adaptez la commande:
`PYTHONPATH=./libs/ python3 -i ./server/main.py`.<br>
Pour stopper le serveur, écrire la commande `stop()` dans le terminal intéractif et attendre que le processus Python soit fini, sinon les ports utilisés par le processus resteront utilisés et ne pourront pas être réutilisés.<br>