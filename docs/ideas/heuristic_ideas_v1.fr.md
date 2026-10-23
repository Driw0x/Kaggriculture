[English](heuristic_ideas_v1.md) | [Français](heuristic_ideas_v1.fr.md) | [简体中文](heuristic_ideas_v1.zh-CN.md)

[README du projet](../../README.fr.md)

<a id="heuristic-ideas-v1--corrected-daily-planner"></a>
# Idées heuristiques v1 — Planificateur quotidien corrigé

[Version précédente : aucune](#) · [Version suivante →](heuristic_ideas_v2.fr.md)

> **Convention de série**
>
> - `v1` est la base complète de la série d'idées heuristiques.
> - `v2`, `v3` et `v4` sont des **deltas stricts par rapport à la version immédiatement précédente**.
> - Un delta hérite de son prédécesseur directement sans modification, sauf s'il ajoute, remplace ou corrige une règle.
> - L'héritage est transitif : les versions ultérieures n'utilisent pas les versions anciennes comme parents de conception parallèles.
> - [`heuristic_ideas_final.md`](heuristic_ideas_final.fr.md) est l'image complète autonome après la chaîne entière et n'a pas d'agent associé.

<a id="identity"></a>
## Identité

|Champ|Valeur|
| --- | --- |
|Version| `v1` |
|Source originale| `detail_corrige` |
|Agent associé| `chi12.py` |
|Rôle|Base complète du planificateur heuristique|
|Amélioré par| [`v2`](heuristic_ideas_v2.fr.md) |

<a id="main-idea"></a>
## Idée principale

Construire chaque jour à partir de l'état actuel du jeu, transformer les besoins en tâches priorisées, regrouper les actions liées, ajouter les logistiques nécessaires, assigner des itinéraires et des ouvriers, puis exécuter tout en réparant localement le plan lorsque l'état observé change.

<a id="core-ideas"></a>
## Idées fondamentales

<a id="1-plan-every-day-from-the-real-state"></a>
### 1. Planifier chaque jour à partir de l'état réel

Au début de chaque jour, lire l'état actuel et reconstruire le travail utile à partir de ce qui existe effectivement : plantes, animaux, mauvaises herbes, stocks, ouvriers, capacité de la grange, besoins du marché et possibilités de production.

Le pipeline quotidien est conceptuellement :

`economy -> tasks -> placement -> priorities -> bundles -> logistics -> routes -> capacity/HIRE -> execution/replanning`

<a id="2-survival-work-comes-before-optimization"></a>
### 2. Le travail de survie précède l'optimisation

Les tâches de maintenance obligatoires ne doivent pas être sacrifiées pour des profits optionnels :

- arroser les plantes lorsque la journée manquée entraînerait un problème de survie ;
- alimenter les animaux lorsque la journée manquée les rendrait échappés ;
- récolter avant que les produits ne soient perdus ou que les animaux atteignent la saturation de stock ;
- protéger l'arrosage obligatoire du jour de plantation.

Ces actions sont traitées comme `CRITICAL`.

<a id="3-separate-survival-production-yield-preparation-and-secondary-work"></a>
### 3. Séparer le travail de survie, la production, la rendement, la préparation et les tâches secondaires

Les tâches ne sont pas toutes équivalentes. Le planificateur distingue :

- `CRITICAL` : empêche la perte ou l'échec ;
- `PRODUCTION` : récolte, plantation, construction, placement ou alimentation productive obligatoires ;
- `YIELD` : fertilisation, soins et arrosage utile bonus ;
- `PREPARATION` : excavation ou installation nécessaires pour la production future ;
- `SECONDARY` : collecte d'engrais non urgente ou suppression des mauvaises herbes.

Les délais et la valeur économique affinent l'ordre au sein de ces catégories.

<a id="4-place-production-to-reduce-future-maintenance-cost"></a>
### 4. Placer la production pour réduire les coûts de maintenance futurs

La sélection des emplacements ne repose pas uniquement sur la disponibilité d'un espace libre. Les emplacements candidats sont évalués selon :

- distance par rapport à la grange ;
- visites de maintenance futures ;
- proximité avec des productions similaires ;
- obstruction des itinéraires ;
- occupation de l'espace.

Les productions à forte maintenance doivent rester proches des itinéraires efficaces et de l'accès à la grange. Les animaux sont donc plus sensibles à la localisation que les cultures temporaires simples.

<a id="5-keep-dependent-actions-together"></a>
### 5. Garder les actions dépendantes ensemble

Les actions concernant la même case doivent former un groupe chaque fois que possible.

Les groupes typiques incluent :

- `DIG -> PLANT -> WATER`;
- `BUILD -> PLACE -> FEED -> CARE` pour un nouvel animal ;
- `HARVEST -> optional DIG -> PLANT -> optional FERTILIZE -> WATER` lors du réplantage.

Le planneur doit préserver les contraintes d'ordre, en particulier `FERTILIZE before WATER` et `WATER before HARVEST` lorsqu'elles sont pertinentes.

<a id="6-treat-logistics-as-part-of-the-plan"></a>
### 6. Traiter la logistique comme une partie du plan

Un itinéraire n'est seulement faisable si le travailleur dispose des ressources nécessaires pour l'exécuter.

Le planneur doit donc :

- réserver des graines, du fertilisant, des animaux et de la nourriture ;
- créer des dépendances d'achat lorsque les stocks sont manquants ;
- calculer les quantités exactes à récupérer ;
- charger les ressources de l'itinéraire avant que le travailleur ne quitte la zone du hangar ;
- suivre l'inventaire futur du travailleur après les récoltes ;
- planifier les retours et les actions `DROP` lorsque nécessaire.

<a id="7-protect-shed-capacity-before-a-required-drop"></a>
### 7. Protéger la capacité du hangar avant une chute obligatoire

La pression de stockage doit être résolue avant qu'elle ne bloque la production requise.

Si une action planifiée `DROP` provoquerait un dépassement du hangar, le planneur doit libérer de la capacité à l'avance en vendant des stocks, en insérant une chute précoce ou en redistribuant les itinéraires.

Une récolte requise ne doit pas être reportée uniquement pour éviter la pression du hangar.

<a id="8-build-routes-around-urgency-and-locality"></a>
### 8. Construire des itinéraires autour de l'urgence et de la proximité

Les itinéraires commencent par la tâche la plus urgente et ajoutent des travaux proches et compatibles tout en préservant les délais.

L'équilibre d'insertion inclut :

- la distance de trajet ;
- le coût de l'action ;
- le risque de délai ;
- les opportunités dans la même zone ;
- les opportunités dans le même type.

L'objectif n'est pas un routage globalment optimal, mais des itinéraires pratiques qui permettent d'accomplir des travaux importants à temps.

<a id="9-hire-exists-to-make-planned-work-feasible"></a>
### 9. HIRE existe pour rendre les travaux planifiés faisables

La planification de la capacité détermine si les travailleurs existants peuvent exécuter tous les itinéraires importants. Si ce n'est pas le cas, le planneur peut planifier des actions `HIRE` et assigner les nouveaux travailleurs après leur tour de disponibilité.

Un itinéraire est finalisé uniquement après vérification de :

- l'apparition et la disponibilité des travailleurs ;
- les retours ;
- le temps de trajet et d'action ;
- le retour au hangar ;
- les délais ;
- les dépendances du marché ;
- la capacité du hangar.

<a id="10-replan-locally-when-reality-differs-from-the-plan"></a>
### 10. Réplanifier localement lorsque la réalité diffère du plan

L'exécution vérifie continuellement si les hypothèses restent vraies.

Les changements importants incluent :

- nouvelles boutiques ou des modifications significatives des prix ;
- des actions des adversaires ;
- des mauvaises herbes inattendues ;
- des résultats différents de récolte ou de production ;
- des échecs de `BUY` ou de `HIRE` ;
- des travailleurs en retard par rapport au calendrier ;
- l'insuffisance de l'inventaire ou de la saturation du hangar.

Lorsque quelque chose change, préserve le travail accompli, les embauches payées et les itinéraires valides autant que possible, et reconstruis uniquement les travaux futurs affectés.

<a id="11-respect-the-market-order-limit"></a>
### 11. Respecter la limite de l'ordre de marché

Les actions `SELL`, `BUY` et `HIRE` partagent la limite de marché de 10 commandes par tour.

Les commandes identiques peuvent être fusionnées lorsque cela est légal. Si la limite est dépassée, les commandes critiques en termes de dépendance et de deadline doivent être conservées avant les commandes économiques de moindre priorité.

<a id="12-end-of-game-liquidation-is-explicit"></a>
### 12. La liquidation à la fin du jeu est explicite

La dernière journée n'est pas traitée comme une journée normale.

Avec `episodeSteps = 720`, la liquidation et le dernier `DROP` doivent être terminés au plus tard le jour 29, heure 22. Le planificateur doit se terminer sans oublier une récolte importante et sans laisser un inventaire de travaileur éloigné de la grange.

<a id="key-invariants"></a>
## Invariants clés

- N'oubliez jamais de faire arroser une culture nouvellement plantée.
- N'oubliez jamais que les tâches de survie `WATER` ou `FEED` ne doivent pas être dépassées par des tâches optionnelles.
- N'organisez jamais un itinéraire sans les ressources nécessaires pour le compléter.
- N'allowez jamais qu'une exigence `DROP` dépasse la capacité de la grange.
- N'annulez jamais une récolte requise uniquement parce que la planification de stockage est mauvaise.
- Ne exécutez jamais plus de 10 commandes de marché en une seule étape.
- Conservez les travaux déjà effectués ou encore valides lors de la replanification.
- Terminez la liquidation finale au dernier tick jouable de la dernière journée.

<a id="what-v1-establishes"></a>
## Ce que v1 établit

`v1` est le planificateur de référence complet. Son seul successeur direct est [`v2`](heuristic_ideas_v2.fr.md). Toute autre comportement ultérieur est hérité de manière transitive par la chaîne de versions plutôt que de considérer `v1` comme un parent parallèle.


---

<a id="navigation"></a>
## Navigation

Version précédente : aucune · [Version suivante →](heuristic_ideas_v2.fr.md)
