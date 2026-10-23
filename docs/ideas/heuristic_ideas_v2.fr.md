[English](heuristic_ideas_v2.md) | [Français](heuristic_ideas_v2.fr.md) | [简体中文](heuristic_ideas_v2.zh-CN.md)

[README du projet](../../README.fr.md)

<a id="heuristic-ideas-v2--planned-land-expansion"></a>
# Idées heuristiques v2 — Expansion de terrain planifiée

[← Version précédente](heuristic_ideas_v1.fr.md) · [Version suivante →](heuristic_ideas_v3.fr.md)

> **Convention de série**
>
> `v2` est une **différence stricte par rapport à `v1`**. Il hérite de `v1` de manière complète et modifie uniquement les règles explicitement documentées ici. L'héritage ultérieur est transitif via `v2`.

<a id="identity"></a>
## Identité

|Champ|Valeur|
| --- | --- |
|Version| `v2` |
|Source originale| `detail_improve` |
|Agent associé| `chi13.py` |
|Rôle|Différence stricte par rapport à [`v1`](heuristic_ideas_v1.fr.md)|
|Améliore| [`v1`](heuristic_ideas_v1.fr.md) |
|Amélioré par| [`v3`](heuristic_ideas_v3.fr.md) |

<a id="main-idea"></a>
## Idée principale

Ne pas acheter de terrain parce que le champ actuel semble complet. Acheter du terrain uniquement lorsque la production supplémentaire rentable ne peut pas s'inscrire dans les terrains existants et qu'un plan d'exploitation concret prouve que l'achat reste viable et rentable après avoir tenu compte des coûts de terrain, du travail, des transports, de la maintenance et des contraintes de fin de jeu.

`v2` hérite de [`v1`](heuristic_ideas_v1.fr.md) de manière complète. Seules les ajouts, remplacements et corrections rédigés dans ce fichier modifient la conception héritée.

<a id="core-ideas-added-in-v2"></a>
## Idées principales ajoutées dans v2

<a id="1-separate-land-purchase-from-placement"></a>
### 1. Séparer l'achat de terrain de sa mise en place

`CHOOSE_PLACEMENTS()` doit placer uniquement la production sur des terrains déjà disponibles.

Il ne doit plus décider seul d'acheter du terrain lorsqu'aucune case n'est trouvée. L'expansion de terrain devient une décision stratégique explicite prise avant la génération des tâches quotidiennes normales.

Cela évite de transformer une échec local de placement en une acquisition coûteuse automatique.

<a id="2-compare-expansion-against-a-no-purchase-baseline"></a>
### 2. Comparer l'expansion à une base sans achat

Avant de considérer de nouveaux terrains, construire le meilleur plan utilisant uniquement les terrains déjà débloqués.

Cette base doit inclure :

- des cases libres ;
- des excavations utiles ;
- des structures vides compatibles ;
- des cases qui deviendront libres après récolte ou fin de vie ;
- des rotations faisables avant la fin du jeu ;
- des embauches nécessaires ;
- la maintenance ;
- des ventes réalisables.

Seulement la production encore rentable mais qui ne peut pas s'inscrire dans cette base crée un besoin réel de terrain.

<a id="3-a-full-field-is-not-enough-to-justify-buy_land"></a>
### 3. Un champ complet n'est pas suffisant pour justifier `BUY_LAND`

Deux anti-modèles sont rejetés explicitement :

- le fait que le champ semble complet ne prouve pas qu'un terrain supplémentaire est nécessaire ;
- un manque de travailleurs ne prouve pas un manque de terrains.

L'expansion doit répondre à un problème de capacité de production, et non masquer un problème de routage ou de main-d'œuvre.

<a id="4-reserve-a-concrete-exploitation-plan-before-purchase"></a>
### 4. Réservé un plan d'exploitation concret avant l'achat

Pour le quadrant légal suivant, simuler l'achat sur un état copié et réserver comment les nouvelles cases seraient effectivement utilisées.

Ce plan simulé doit inclure :

- la production future exacte ;
- des semences ou des animaux ;
- le moment d'installation ;
- la maintenance future ;
- les embauches nécessaires ;
- le routage et les déplacements ;
- les ventes attendues avant la fin du jeu ;
- le coût total du terrain.

L'achat est valide uniquement si ce plan est faisable et produit un gain net positif par rapport à la situation actuelle du terrain.

<a id="5-validate-cash-labor-routing-and-deadlines-together"></a>
### 5. Valider les fonds, le travail, les itinéraires et les délais ensemble

Une liste de cultures apparemment rentable est insuffisante.

L'extension doit être rejetée lorsque :

- l'installation se produit trop tard ;
- le service de maintenance ne peut pas être assuré ;
- les fonds deviennent insuffisants ;
- la capacité au travail est insuffisante ;
- les itinéraires ne s'adaptent pas ;
- la valeur attendue ne rembourse pas le coût du terrain.

Cela transforme `BUY_LAND` en un engagement pleinement planifié au lieu d'un achat spéculatif.

<a id="6-do-not-place-production-on-unconfirmed-land"></a>
### 6. Ne pas placer la production sur un terrain non confirmé

Une production dépendant d'un `BUY_LAND` en attente reste uniquement une réservation.

Aucune mise en place réelle ni aucun itinéraire ne peut cibler une tile `LOCKED` avant que l'achat ne soit observé comme confirmé.

Si aucune mise en place valide n'existe sur le terrain actuellement disponible, reportez ou annulez cette production au lieu de prétendre que le terrain futur existe déjà.

<a id="7-confirm-expansion-from-observations-not-assumptions"></a>
### 7. Confirmer l'extension à partir d'observations, pas d'assumptions

Un achat de terrain est considéré comme réel uniquement lorsque des tiles nouvellement débloquées apparaissent dans l'état observé.

Après confirmation :

- détecter les nouvelles tiles ;
- enregistrer le coût réel ;
- revalider le plan d'exploitation réservé ;
- supprimer les utilisations dont les hypothèses ne sont plus valables ;
- intégrer immédiatement les nouvelles tiles dans la planification normale.

Si l'achat n'a pas été confirmé, supprimez les réservations dépendantes et réplantez.

<a id="8-treat-sunk-land-cost-correctly"></a>
### 8. Traiter correctement le coût d'investissement perdu

Après confirmation de l'achat, ne gardez pas une production non rentable simplement pour justifier les frais déjà déjoués sur le terrain.

La décision initiale d'achat et la meilleure décision après achat sont des questions distinctes. Une fois le coût perdu, la future production doit être évaluée sur sa valeur restante.

<a id="9-buy_land-is-a-real-market-dependency"></a>
### 9. `BUY_LAND` est une dépendance réelle du marché

`BUY_LAND` consomme l'un des 10 emplacements de commande de marché et ne doit pas être fusionné avec une autre commande.

Avant de l'envoyer, vérifiez :

- la réserve de fonds en sécurité ;
- les prérequis ;
- le plan d'exploitation dépendant.

Si `BUY_LAND`, un autre `BUY` ou un `HIRE` est retardé ou supprimé, chaque plan dépendant doit être revalidé.

<a id="10-reevaluate-land-only-when-its-assumptions-matter"></a>
### 10. Réévaluer le terrain uniquement lorsque ses hypothèses sont pertinentes

L'évaluation du terrain n'a pas besoin d'être effectuée de manière aveugle à chaque tick.

Recalculez-la lorsque une modification économique ou une exigence de mise en place modifie les conditions qui justifiaient ou rejetaient l'extension.

<a id="key-invariants"></a>
## Invariants clés

- Aucune `BUY_LAND` implicite en cas d'échec de mise en place.
- Aucun achat sans un plan d'exploitation concret et daté.
- Aucun achat sauf s'il améliore le meilleur plan sans terrain.
- Aucune action de production ne peut cibler une tile verrouillée.
- Le coût du terrain, les semences/animaux, les embauches, le service de maintenance, les itinéraires et les ventes réalisables doivent tous être inclus.
- Un achat en attente ne compte pas comme capacité confirmée.
- Une utilisation confirmée mais désormais non rentable peut être annulée même si le coût du terrain a déjà été engagé.
- `BUY_LAND` consomme une place sur le marché et propage des dépendances comme les autres achats.

<a id="what-v2-changes-relative-to-v1"></a>
## Quelles sont les modifications v2 par rapport à v1

`v2` conserve le plan quotidien de `v1` mais fait de l'extension du terrain une décision économique séparée et planifiée. L'amélioration principale consiste à remplacer une expansion réactive par une expansion simulée, réservée et confirmée par observation.


---

<a id="navigation"></a>
## Navigation

[← Version précédente](heuristic_ideas_v1.fr.md) · [Version suivante →](heuristic_ideas_v3.fr.md)
