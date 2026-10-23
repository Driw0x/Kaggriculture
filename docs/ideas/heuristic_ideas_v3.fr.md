[English](heuristic_ideas_v3.md) | [Français](heuristic_ideas_v3.fr.md) | [简体中文](heuristic_ideas_v3.zh-CN.md)

[README du projet](../../README.fr.md)

<a id="heuristic-ideas-v3--unified-optimized-planner"></a>
# Idées heuristiques v3 — Planificateur optimisé unifié

[← Version précédente](heuristic_ideas_v2.fr.md) · [Version suivante →](heuristic_ideas_v4.fr.md)

> **Convention de série**
>
> `v3` est une **différence stricte par rapport à `v2`**. Il hérite de `v2` de manière complète ; puisque `v2` hérite déjà de `v1`, tout comportement de `v1` reste disponible transitivement sans faire de `v1` un parent direct supplémentaire.

<a id="identity"></a>
## Identité

|Champ|Valeur|
| --- | --- |
|Version| `v3` |
|Source originale| `detail_opti` |
|Agent associé| `chi14.py` |
|Rôle|Différence stricte par rapport à [`v2`](heuristic_ideas_v2.fr.md)|
|Améliore| [`v2`](heuristic_ideas_v2.fr.md) |
|Amélioré par| [`v4`](heuristic_ideas_v4.fr.md) |

<a id="main-idea"></a>
## Idée principale

Arrêtez de faire dépendre l'économie, le routage, la gestion du marché, la capacité et l'exécution de plusieurs approximations séparées. Faites que chaque sous-système consomme une seule prédiction partagée, un seul modèle de réservation, une seule représentation de tâche et un seul calendrier de marché validé, afin qu'une décision acceptée par une partie du planificateur soit également réalisable pour les autres.

`v3` hérite de [`v2`](heuristic_ideas_v2.fr.md) de manière complète. Puisque `v2` hérite déjà de `v1`, chaque règle de `v1` restant inchangée est disponible transitivement ; `v3` a seulement un prédécesseur direct.

<a id="core-ideas-added-in-v3"></a>
## Idées principales ajoutées dans v3

<a id="1-one-shared-forecast-for-all-planner-decisions"></a>
### 1. Une seule prédiction partagée pour toutes les décisions du planificateur

Maintenir une seule prédiction dérivée de l'état actuel jusqu'à la fin du jeu.

La prédiction projette uniquement les parties affectées après un changement et suit :

- l'état des plantes et des animaux ;
- l'arrosage, l'alimentation et les soins ;
- la survie ;
- les rendements et les dates de production ;
- la fertilisation ;
- la dégradation et la saturation ;
- les exigences de maintenance ;
- les ressources et les rendements exploitables ;
- l'occupation des tiles et la libération future.

Les logiques de production, de placement, de terrain, de routage, de marché et de fin de jeu lisent toutes cette même prédiction.

<a id="2-economy-placement-and-expansion-become-one-coherent-plan"></a>
### 2. L'économie, le placement et l'expansion deviennent une seule stratégie cohérente

La stratégie économique doit produire des engagements datés plutôt que des souhaits isolés.

Elle évalue uniquement les productions qui peuvent encore créer une valeur positive avant la fin du jeu et inclut la chaîne complète :

`production -> maintenance -> resources -> harvest -> return -> DROP -> SELL`

Elle inclut également les fonds, les embauches, les actions et les places de marché.

`DECIDE_LAND_PURCHASE()` existe encore depuis `v2`, mais désormais, elle consomme ce plan partagé au lieu de maintenir une approximation économique séparée.

<a id="3-generate-dependency-aware-taskgroup-objects-directly"></a>
### 3. Générer directement des objets `TaskGroup` sensibles aux dépendances

Remplacer la transformation en plusieurs étapes de tâches brutes vers des groupes et des logistiques par la génération directe de groupes stables.

Un objet `TaskGroup` porte :

- une position ;
- des actions ordonnées ;
- une priorité ;
- une deadline ;
- des ressources requises ;
- une valeur estimée ;
- des dépendances ;
- une affectation facultative d'ouvrier.

Les prérequis héritent de l'urgence de ce qui dépend d'eux.

Des identifiants stables empêchent la duplication de tâches lorsqu'une génération est appelée plusieurs fois sans changement de state significatif.

<a id="4-merge-routing-capacity-logistics-and-hire"></a>
### 4. Fusionner le routage, la capacité, la logistique et `HIRE`

L'affectation des travailleurs doit évaluer le coût réel d'insérer un groupe dans une route.

Le coût d'insertion inclut :

- le déplacement ;
- le temps d'action ;
- les retours ;
- l'attente des ressources ;
- le retour et `DROP` ;
- les délais ;
- les effets sur le stock ;
- les effets sur le marché.

Si un groupe important ne peut toujours pas être affecté, testez un nouveau travailleur et incluez le coût d'embauche de Fibonacci, la création, la disponibilité au tick, la capacité restante de la route, le déplacement, le retour et les délais.

Un `HIRE` est accepté uniquement s'il rend effectivement la tâche cible faisable.

<a id="5-prefer-small-local-route-improvements-over-a-complex-global-solver"></a>
### 5. Privilégier des améliorations locales simples plutôt qu'un solveur global complexe

Après avoir obtenu des itinéraires faisables, essayez des mouvements ou des échanges limités entre des groupes de tâches.

Acceptez un changement uniquement s'il améliore strictement le coût de la route sans violer les délais ou les réservations.

Si un groupe combine une récolte urgente avec un remplacement optionnel, supprimez d'abord le remplacement optionnel et réessayez la récolte seule.

L'objectif est un planificateur heuristique amélioré, et non un système généraliste de VRP.

<a id="6-use-one-stock-and-market-calendar"></a>
### 6. Utiliser un seul calendrier de stock et de marché

Tous les `BUY`, `SELL`, `HIRE` et intentions de marché associées doivent être planifiés à travers un seul calendrier validé.

Le calendrier :

- ordonne les actions selon les dépendances ;
- assure que les ventes de financement se produisent avant les achats ou embauches qu'elles financent ;
- respecte la limite de 10 actions par tick ;
- simule les fonds, les stocks, les réservations et les prix ;
- rapporte les conflits aux tâches dépendantes.

La 11e commande ne doit jamais être discréditée sans être signalée.

Un achat retardé invalide les retours ou plantations dépendants. Une embauche retardée invalide la capacité de la route basée sur l'ancien tick de disponibilité.

<a id="7-replan-by-repairing-only-the-affected-future"></a>
### 7. Réplanifier en réparant uniquement l'avenir affecté

Ne reconstruisez pas de manière générale le planificateur après chaque changement d'observation.

D'abord, demandez-vous si le changement affecte la faisabilité, le signe du gain attendu ou l'action économique choisie. Si non, conservez le plan actuel.

Lorsqu'une réparation est nécessaire :

- identifiez la cause locale ;
- préservez les faits confirmés et les préfixes de routes déjà assignés ;
- préservez les travailleurs payés et les itinéraires toujours valides ;
- libérez uniquement les réservations futures invalides et les suffixes de routes affectés ;
- ré-génère uniquement les groupes de tâches affectés ;
- ré-affectez uniquement les nouveaux ou déplacés groupes.

Un problème local peut encore se propager à plusieurs itinéraires lorsqu'ils partagent la même ressource ou dépendance de marché.

<a id="8-integrate-endgame-constraints-into-every-decision"></a>
### 8. Intégrer les contraintes de fin de partie dans chaque décision

La logique de fin de partie ne doit pas être une étape finale de nettoyage.

Rejetez toute nouvelle production, animaux ou expansion dès que la chaîne de liquidation totale ne peut pas rembourser la décision avant la fin du jeu :

`installation + production + harvest + return + DROP + SELL`

Supprime également les entretiens ou les dépenses sans effet restant sur le cash, tels que des engrais tardifs inutiles, des soins, des achats ou des embauches optionnelles.

Planifie la dernière récolte, le retour, la chute et la vente en partant de la date limite de liquidation finale.

<a id="9-turn-known-edge-cases-into-explicit-verification-cases"></a>
### 9. Transforme les cas particuliers connus en cas de vérification explicite

Le planificateur doit être testé contre des invariants concrets, notamment :

- prise de nourriture exacte après soustraction des stocks déjà transportés ;
- réservation de semences empêchant une plantation simultanée ;
- disponibilité des travailleurs embauchés à partir d'un tick suivant `HIRE` ;
- libération de la capacité du bâtiment avant, et non à, un dépassement de `DROP` ;
- réparation des conflits de marché au-delà de 10 commandes au lieu de les tronquer ;
- rejet de terres lorsque aucune production supplémentaire n'est rentable ;
- rejet de terres dont les entretiens futurs sont impossibles.

<a id="key-invariants"></a>
## Invariants clés

- Chaque sous-système utilise la même prévision et réservations.
- Une génération répétée sans changement d'état ne doit pas dupliquer les travaux planifiés.
- La logistique fait partie de la faisabilité des itinéraires, et non de corrections apportées plus tard.
- Une embauche est utile uniquement si elle rend possible un travail autrement inaccessibles.
- Les dépendances de marché sont planifiées explicitement et ne sont jamais tronquées silencieusement.
- Les actions de marché retardées invalident les actions futures dépendantes.
- Le réplanification préserve les travaux validement commis et répare uniquement les suffixes affectés.
- Chaque nouvelle décision économique doit encore compléter sa chaîne complète de liquidation avant la fin du jeu.

<a id="what-v3-changes-relative-to-v2"></a>
## Quelles sont les modifications de v3 par rapport à v2

`v3` ne rajoute pas principalement de nouvelles règles de jeu. Il réorganise le planificateur afin que les règles existantes soient évaluées de manière cohérente. Son amélioration centrale est la cohérence : une seule prévision, des groupes de tâches sensibles aux dépendances, une affectation et une embauche intégrées, un calendrier de marché unique, une réparation locale et une faisabilité adaptée à la fin du jeu partout.


---

<a id="navigation"></a>
## Navigation

[← Version précédente](heuristic_ideas_v2.fr.md) · [Version suivante →](heuristic_ideas_v4.fr.md)
