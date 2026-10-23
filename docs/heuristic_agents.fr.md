[English](heuristic_agents.md) | [Français](heuristic_agents.fr.md) | [简体中文](heuristic_agents.zh-CN.md)

[README du projet](../README.fr.md)

<a id="heuristic-agents"></a>
# Agents heuristiques

Ce document complète [chi_agents.md](chi_agents.fr.md).

`chi_agents.md` décrit la lignée historique de CHI allant de l'ouverture initiale fixe à CHI10. Ce document isole la branche **heuristique-planner** construite à partir du modèle de production de CHI3 et documentée par une séquence stricte d'idées heuristiques :

```text
IMPLEMENTED AGENT LINEAGE

CHI3
  |
  v
heuristic_ideas_v1 -> CHI12
  |
  v
heuristic_ideas_v2 -> CHI13
  |
  v
heuristic_ideas_v3 -> CHI14

DESIGN-ONLY CONTINUATION

heuristic_ideas_v3
  |
  v
heuristic_ideas_v4
  |
  v
heuristic_ideas_final
```

Documents de conception : [ideas_v1](ideas/heuristic_ideas_v1.fr.md) → [ideas_v2](ideas/heuristic_ideas_v2.fr.md) → [ideas_v3](ideas/heuristic_ideas_v3.fr.md) → [ideas_v4](ideas/heuristic_ideas_v4.fr.md) → [ideas_final](ideas/heuristic_ideas_final.fr.md)

La chaîne de conception est stricte : `v1` est la base, chacune des versions `v2`, `v3` et `v4` améliore uniquement son prédécesseur immédiat, et `final` est la stratégie complète autonome après résolution de l'ensemble de la lignée. La lignée d'agents mise en œuvre s'arrête à `CHI14`. Le projet est désormais fermé : `v4` et `final` restent à usage de conception, et les tentatives ultérieures d'implémentation, y compris `CHI16` / `chi_final`, n'ont pas produit de successeur validé et ne sont pas conservées comme agents sources.

La lignée ci-dessus est une **lignée de conception**. Le réutilisation du code peut rester plus directe lorsque cela est utile : l'héritage de conception et la structure d'importation en Python n'ont pas besoin d'être identiques.

---

<a id="1-objective"></a>
## 1. Objectif

L'objectif de cette branche est différent de l'histoire progressive de CHI1 à CHI10.

Cette branche commence à partir de CHI3 car CHI3 fournit déjà la description de production réutilisable nécessaire à un planificateur général :

- des descriptions d'état de culture et d'animaux ;
- des calendriers de récolte ;
- des aides de coordination/chemins ;
- des sémantiques de production sur plusieurs jours.

L'objectif est alors de remplacer des comportements fixes ou localement gloutons par une pipeline de planification de plus en plus explicite :

```text
observation
    |
    v
production state / forecast
    |
    v
economic choices
    |
    v
placements and land decisions
    |
    v
task groups with priorities and deadlines
    |
    v
routing + capacity + HIRE
    |
    v
market orders and storage constraints
    |
    v
execution
    |
    v
local replanning from observations
```

Les quatre documents d'idées versionnés rendent ce pipeline de plus en plus concret, et le document final les résout en une stratégie autonome complète. Dans le point de vue fermé du projet, la lignée d'agents mise en œuvre s'arrête à `CHI14` ; `v4` et `final` restent des étapes de conception.

---

<a id="2-source-mapping"></a>
## 2. Cartographie des sources

|Agent|Source de conception|Rôle principal|
| --- | --- | --- |
| `chi3.py` |Branche historique de CHI|Base de production/état|
| `chi12.py` |[ideas_v1](ideas/heuristic_ideas_v1.fr.md)|Modèle correcteur quotidien et exécution|
| `chi13.py` |[ideas_v2](ideas/heuristic_ideas_v2.fr.md)|Expansion de terrain planifiée au-delà de CHI12|
| `chi14.py` |[ideas_v3](ideas/heuristic_ideas_v3.fr.md)|Prévision unifiée, routage, calendrier de marché et planification consciente de la fin de jeu|

Étapes de conception sans agent associé :

|Conception|État|Rôle principal|
| --- | --- | --- |
|[ideas_v4](ideas/heuristic_ideas_v4.fr.md)|Conception uniquement|Couche tactique et économique marginale consciente du marché sur `v3`|
|[ideas_final](ideas/heuristic_ideas_final.fr.md)|Conception uniquement|Stratégie consolidée complète et contrat d'implémentation|

---

<a id="3-base--chi3-production-model"></a>
## 3. Base — modèle de production de CHI3

CHI3 est le point de départ commun de la branche heuristique.

CHI12 importe explicitement de CHI3 :

```python
ANIMAL_STATE
CROP_PRODUCTION
CROP_STATE
coordinates_to_path
distance
```

La validation de CHI12 vérifie également que CHI3 reste en lecture seule pendant la réécriture.

L'arbre maintient donc le vocabulaire de production de CHI3 tout en remplaçant la planification et l'exécution autour de ce vocabulaire.

<a id="retained-concepts"></a>
### Concepts conservés

La base conservée inclut :

- les cinq familles de cultures utilisées par le planificateur ;
- la production de canard, de vache et de mouton ;
- le moment de récolte des cultures ;
- le moment de production des animaux ;
- la construction réutilisable de parcours de Manhattan ;
- l'état observable des cultures et des animaux.

<a id="what-the-branch-changes"></a>
### Ce que modifie la branche

La nouvelle branche ne suit pas simplement la voie de CHI3.

Elle introduit progressivement :

- des priorités explicites des tâches ;
- des délais d'action ;
- une compilation de parcours prise en compte par les ressources ;
- des rendez-vous planifiés PICKUP et DROP ;
- la disponibilité du marché à T+1 ;
- la protection du stock ;
- l'affectation globale des ouvriers ;
- l'évaluation de l'expansion de la surface ;
- des lots de production datés ;
- une projection dynamique des prix de marché ;
- un déploiement économique complet et exécutable.

---

<a id="4-chi12--ideas_v1"></a>
# 4. CHI12 — [ideas_v1](ideas/heuristic_ideas_v1.fr.md)

`src/agents/chi12.py` est associé au planificateur de base décrit par [ideas_v1](ideas/heuristic_ideas_v1.fr.md).

Le fichier source énonce directement la relation :

```text
CHI12: CHI3 production with the daily planner described by `heuristic_ideas_v1`.
```

CHI3 est traité comme une référence de production en lecture seule.

<a id="41-planner-structure"></a>
## 4.1 Structure du planificateur

[ideas_v1](ideas/heuristic_ideas_v1.fr.md) organise chaque jour autour de la séquence suivante :

```text
read current state
    -> economic strategy
    -> generate daily tasks
    -> choose placements
    -> prioritize tasks
    -> build task groups
    -> add logistics
    -> build candidate routes
    -> calculate capacity / HIRE
    -> finalize routes
    -> execute and replan
```

Ceci devient le premier planificateur quotidien explicite de cette branche.

<a id="42-task-generation"></a>
## 4.2 Génération des tâches

CHI12 convertit la ferme observée en des ensembles de tâches localisés par tuile.

Ces exemples incluent :

```text
crop:
    FERTILIZE
    WATER
    HARVEST
    DIG
    PLANT
    WATER

animal:
    HARVEST
    COLLECT_FERTILIZER
    FEED
    CARE
```

Chaque tâche porte :

- une priorité ;
- un délai ;
- une position de tuile ;
- une valeur estimée ;
- les actions ordonnées à exécuter sur cette tuile.

Les classes de priorité implémentées sont :

```text
CRITIQUE
PRODUCTION
RENDEMENT
PREPARATION
SECONDAIRE
```

Cela maintient les travaux essentiels et les tâches sensibles aux délais devant les travaux optionnels de rendement ou de nettoyage.

<a id="43-placement"></a>
## 4.3 Placement

`choose_placements` conserve les productions existantes et reconstruit le portefeuille de CHI3 sur les tuiles disponibles.

Le coût de placement tient compte de :

- le nombre attendu de visites ;
- la distance à l'accès le plus proche de la grange ;
- la proximité avec des productions similaires ;
- la compatibilité structurelle.

À ce stade, le planificateur ne fait pas de spéculation sur l'expansion : le portefeuille de CHI3 s'inscrit dans le quadrant initial NW.

<a id="44-explicit-logistics"></a>
## 4.4 Logistique explicite

La conception de `v1` fait de la gestion des stocks une composante du plan plutôt qu'une après-pensée.

CHI12 calcule :

- la quantité de blé nécessaire pour FEED ;
- la quantité de fertilisant nécessaire pour FERTILIZE ;
- les animaux à PICKUP avant PLACE ;
- les graines nécessaires aux actions PLANT planifiées ;
- la disponibilité des achats à T+1 ;
- les itinéraires de retour à la grange ;
- les actions de DROP finale.

`compile_route` rejette une route lorsque l'action ou le retour final manque de respecter la deadline de jeu.

<a id="45-storage-protection"></a>
## 4.5 Protection de la mémoire

`protect_storage` simule chronologiquement :

```text
PICKUP
DROP
SELL
BUY_PRODUCT
BUY_ANIMAL
```

avant d'accepter le trajet.

Un retour peut être reporté si le dépôt ne peut pas accepter son chargement, mais le planificateur ne reporte pas une récolte simplement pour maintenir la production en dehors du dépôt.

<a id="46-hire-and-routing"></a>
## 4.6 LOCATION ET ROUTING

La première implémentation utilise l'insertion de trajets glouton.

Pour chaque ouvrier, le planificateur :

1. sélectionne une tâche candidate ;
2. recompile la route complète ;
3. vérifie les délais ;
4. vérifie la logistique ;
5. vérifie le stockage ;
6. accepte l'insertion uniquement lorsque la route complète reste exécutable.

Si le personnel existant ne peut pas couvrir les tâches requises, le planificateur évalue des travailleurs supplémentaires avec le coût Fibonacci HIRE et la règle d'indisponibilité des travailleurs T+1.

<a id="47-observation-checked-execution"></a>
## 4.7 Exécution vérifiée par observation

L'exécution est persistante au cours de la journée.

Un réplan local peut être déclenché par :

- une position inattendue d'un travailleur ;
- un achat refusé ;
- un travailleur embauché manquant ;
- une mauvaise herbe inattendue ;
- un changement de tuile de production ;
- un désaccord de rendement ;
- l'ouverture d'un nouveau magasin ;
- un changement de prix suffisamment important.

Les itinéraires valides sont conservés autant que possible au lieu de reconstruire l'ensemble du plan.

---

<a id="5-chi12-validation"></a>
## 5. Validation CHI12

Un rapport de validation dédié au Codex est disponible pour CHI12.

<a id="engine-behavior-verified"></a>
### Le comportement de l'engine a été vérifié

La validation confirme plusieurs contraintes de l'engine utilisées par le planificateur :

- les actions du worker s'exécutent avant les ordres de marché ;
- les achats et les HIRE effectués à T deviennent utilisables à T+1 ;
- un DROP de même tick peut être vendu ;
- une vente de même tick ne libère pas l'espace du dépôt avant ce DROP ;
- dans la version par défaut de 720 étapes de jeu, l'étape actionnable finale est 718 ;
- la dernière retour explicite et liquidation doit donc être effectuée avant la fin.

<a id="tests"></a>
### Tests

L'ensemble spécifique à CHI12 contient **28 tests**.

L'ensemble complet de tests à l'heure de la validation contient **68 tests passés**.

Les cas couvrent, parmi d'autres choses :

- PLANT suivie de WATER obligatoire ;
- les exigences de ressources FEED pour les animaux ;
- plusieurs actions FERTILIZE ;
- la mise en place de toutes les trois espèces d'animaux ;
- l'ordre de FERTILIZE/WATER/HARVEST ;
- le remplacement des tomates et des fraises ;
- le coût des retours et des DROP ;
- les mauvaises herbes ;
- la disponibilité des HIRE et des ACHATS à T+1 ;
- la limite des ordres de marché ;
- les cas de dépôts complets et de retours simultanés ;
- la liquidation finale ;
- la préservation des itinéraires lors de la replanification ;
- les achats et HIRE rejetés ;
- des changements de production inattendus.

<a id="chi3-comparison"></a>
### Comparaison avec CHI3

L'indicateur de référence conservé utilise les semences de 0 à 19 dans les deux sièges, pour 40 parties par agent.

|Agent|Parties|Minimum|Maximum|Moyenne|Médiane|Invalide|
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
|CHI3| 40 | 0 | 0 | 0 | 0 | 0 |
|CHI12| 40 | 55,033 | 62,953 | 59,597.25 | 60,306 | 0 |

Cette comparaison présente une limitation importante : CHI3 ne génère pas d'ordres VENTE dans le code testé. Le résultat valide donc l'ensemble du cycle jouable/économique de CHI12, mais il ne permet pas d'isoler la valeur de l'algorithme de routage nouveau seul.

---

<a id="6-chi13--ideas_v2"></a>
# 6. CHI13 — [ideas_v2](ideas/heuristic_ideas_v2.fr.md)

`src/agents/chi13.py` est l'évolution ciblée de CHI12 associée à la stricte différence `v2` dans [ideas_v2](ideas/heuristic_ideas_v2.fr.md).

Son code résume l'objectif comme suit :

```text
CHI13: targeted CHI12 evolution with global routing and planned land use.
```

L'implémentation réutilise les primitives vis-à-vis de l'engine testées dans CHI12.

<a id="61-main-design-change"></a>
## 6.1 Changement principal de conception

[ideas_v2](ideas/heuristic_ideas_v2.fr.md) ajoute une décision économique supérieure manquante avant le pipeline normal des tâches quotidiennes :

```text
DECIDER_ACHAT_TERRAIN()
```

La terre n'est plus achetée simplement parce que l'exploitation est pleine.

L'expansion doit correspondre à un besoin réel de production supplémentaire qui ne peut pas être placé sur des terres déjà débloquées dans le temps.

<a id="62-land-order-model"></a>
## 6.2 Modèle d'ordre de terre

L'implémentation suit l'ordre légal d'expansion :

```text
NW -> NE -> SW -> SE
```

avec des coûts :

```text
1000
2000
4000
```

Le planificateur ne crée pas un choix entre des quadrants arbitraires. Il décide s'il faut acheter le quadrant suivant légal et comment l'exploiter.

<a id="63-concrete-expansion-plan"></a>
## 6.3 Plan concret d'expansion

Avant qu'un ordre ACHETER_TERRAIN soit accepté, CHI13 estime :

- la production restante rentable ;
- les positions des tuiles dans le nouveau quadrant ;
- le coût de la semence ;
- le coût supplémentaire de RECRUTER ;
- le coût du marché déjà engagé ;
- la capacité de la route ;
- si l'installation reste encore compatible avant la fin.

Un plan d'expansion doit donc être à la fois :

```text
affordable
and
routable
and
profitable
```

La disposition pour le nouveau quadrant est réservée uniquement après confirmation de l'achat de terre.

<a id="64-global-worker-assignment"></a>
## 6.4 Affectation globale des ouvriers

CHI12 construit des itinéraires principalement ouvrier par ouvrier.

CHI13 modifie l'assignateur de sorte qu'une tâche soit d'abord testée sur tous les ouvriers existants. L'insertion sélectionnée minimise le coût supplémentaire de la route parmi les ouvriers faisables.

L'ordre prévu devient :

```text
existing workers first
    -> fit as many required groups as possible
    -> only then consider HIRE
```

Cela implémente directement l'objectif [ideas_v2](ideas/heuristic_ideas_v2.fr.md) de éviter un recrutement lorsque l'un des ouvriers existants peut absorber le travail.

<a id="65-centralized-market-scheduling"></a>
## 6.5 Planification centralisée du marché

CHI13 ajoute une étape finale de consolidation des ordres de marché.

Les ordres sont :

- fusionnés ;
- dédoublés ;
- limités au nombre configuré d'ordres de marché par tick ;
- portés à des ticks ultérieurs lorsqu'ils sont nécessaires.

Cela donne un propriétaire à la contrainte de marché-slot au lieu de laisser des blocs de planificateurs indépendants se partager les mêmes slots.

<a id="66-execution-relationship"></a>
## 6.6 Relation d'exécution

CHI13 conserve le modèle d'exécution de CHI12 :

- des itinéraires persistants ;
- une confirmation à partir des observations ;
- la détection d'échec d'ACHETER/RECRUTER ;
- invalidation sélective de voie;
- replanification locale;
- protection du stock.

La principale modification n'est donc pas un nouveau gestionnaire d'action, mais un planificateur renforcé placé au-dessus des primitives CHI12 testées.

---

<a id="7-chi14--ideas_v3"></a>
# 7. CHI14 — [ideas_v3](ideas/heuristic_ideas_v3.fr.md)

`src/agents/chi14.py` est associé à la différence stricte `v3` dans [ideas_v3](ideas/heuristic_ideas_v3.fr.md).

Sa source décrit la version comme suit :

```text
CHI14: CHI13 routing with dated marginal crop economics.
```

CHI14 préserve ainsi la couche de routage/execution de CHI13 et se concentre sur la valeur économique de la production et de l'expansion.

<a id="71-single-forecast-oriented-architecture"></a>
## 7.1 Architecture orientée prévision unique

[ideas_v3](ideas/heuristic_ideas_v3.fr.md) simplifie l'ancien planificateur long en six blocs étroitement connectés :

```text
forecast
    -> economy / placement / expansion
    -> task groups and dependencies
    -> routing / capacity / HIRE
    -> stock and market calendar
    -> execution / local replanning / endgame
```

L'objectif est d'utiliser un même état daté dans le planificateur au lieu de laisser les modules de routage, d'économie et de marché maintenir des approximations indépendantes.

<a id="72-exact-market-price-projection"></a>
## 7.2 Projection exacte des prix de marché

CHI14 utilise la fonction de tarification de l'engine Kaggriculture pour les transactions projetées.

`project_market` simule :

- le tarif de vente unitaire ;
- le tarif d'achat de produit ;
- l'inventaire de marché actuel ;
- la consommation déjà ouverte dans les magasins ;
- la consommation au centre-ville ;
- l'ordre des transactions par tick.

Le planificateur vérifie d'abord que la fonction de tarification locale reproduit la quote observée avant de faire confiance à la projection.

<a id="73-dated-production-lots"></a>
## 7.3 Lots de production datés

Au lieu de valoriser une récolte comme une quantité statique, CHI14 crée des lots de vente datés.

Pour chaque production, il suit suffisamment d'informations pour estimer :

```text
harvest day
    -> earliest feasible return
    -> DROP
    -> SELL tick
```

Les plantations existantes et les plantations planifiées sont traitées séparément afin qu'une production ne soit pas comptée deux fois.

Les productions qui ne peuvent être vendues avant la fin n'apportent pas de revenu projeté.

<a id="74-marginal-contribution"></a>
## 7.4 Contribution marginale

La décision centrale devient une comparaison entre deux portefeuilles complets :

```text
reference layout
versus
reference layout + one candidate production
```

Pour le candidat, CHI14 recalcul :

- le revenu projeté ;
- le coût des semences ;
- le coût d'embauche ;
- la faisabilité de la route ;
- le coût de terrain lorsque cela s'applique.

La quantité résultante est une contribution marginale plutôt qu'une note fixe de culture.

<a id="75-prudent-scenario"></a>
## 7.5 Scénario prudent

CHI14 évalue les deux suivants :

- une projection centrale ;
- une projection plus conservatrice incluant la production visible de l'adversaire.

Le planificateur peut donc utiliser :

```text
contribution_prudent
```

lorsqu'il décide si un candidat reste rentable.

Cela utilise encore uniquement la production visible de l'adversaire ; il ne crée pas une inventaire caché de l'adversaire.

<a id="76-marginal-land-expansion"></a>
## 7.6 Expansion marginale de terrain

L'évaluation du terrain passe à développer progressivement le nouveau plan proposé.

Pour chaque case candidate :

1. tester chaque culture ;
2. calculer la contribution marginale ;
3. reconstruire le plan de route CHI13 ;
4. vérifier que la case est effectivement attribuée ;
5. recalculer la contribution avec le nouveau plan de route ;
6. conserver l'ajout uniquement si la contribution prudente reste positive.

Le coût total de la terre est ensuite facturé une seule fois au prédicat d'extension du candidat.


---

<a id="8-design-v4--ideas_v4"></a>
# 8. Conception v4 — [ideas_v4](ideas/heuristic_ideas_v4.fr.md)

`v4` n'a **aucun agent associé**. C'est la différence de conception stricte qui suit la conception mise en œuvre par CHI14 / `v3`.

`v4` ne réinvente pas le planificateur de zéro. Il hérite de la conception complète de `v3` et ajoute une couche tactique consciente du marché sur la prédiction unifiée, la gestion des itinéraires, le calendrier du marché, les réparations locales et le modèle de fin de partie.

<a id="81-main-design-change"></a>
## 8.1 Changement principal de conception

La chaîne centrale nouvelle est :

```text
shop demand
    -> own + opponent supply
    -> future market inventory
    -> future price
    -> marginal value
    -> production / hold / sell decisions
```

La conception évalue donc non seulement la faisabilité d'une tâche, mais aussi si l'unité suivante, le carreau, l'ouvrier, l'achat ou la vente de terrain améliore encore la valeur attendue.

<a id="82-labor-and-spatial-constraints"></a>
## 8.2 Contraintes liées au travail et à l'espace

La conception `v4` ajoute :

- un plafond stratégique pour les ouvriers `MAX_WORKERS = 14`;
- un test de valeur marginale avant une nouvelle EMPLOI;
- un placement des animaux proche du centre;
- une réservation centrale `2 x 2` contre les cultures à long terme;
- une comparaison économique consciente du temps et de la terre.

Ces règles se situent au-dessus du mécanisme de routage et de faisabilité hérité de `v3`.

<a id="83-market-and-opponent-aware-economics"></a>
## 8.3 Économie consciente du marché et de l'adversaire

`v4` ajoute une réflexion explicite sur :

- la production et le timing de l'adversaire visible;
- l'inventaire et les prix du marché futur;
- la valeur marginale de production;
- la valeur de vente versus de retenue;
- l'impact du prix de vente;
- l'urgence en liquidités;
- le comportement de l'inventaire au niveau du produit.

Les formules historiques et les calendriers fixes dans `v4` restent expérimentaux sauf si la conception finale consolidée les promeut explicitement.

<a id="84-tactical-land-policy"></a>
## 8.4 Politique tactique sur les terrains

`v4` ajoute des branches préférées pour le timing des terrains et un seuil explicite de liquidités opérationnelles tout en conservant les portes de faisabilité et de rentabilité héritées.

L'interprétation exacte de ces règles tactiques est résolue dans [ideas_final](ideas/heuristic_ideas_final.fr.md).

---

<a id="9-final-consolidated-design--ideas_final"></a>
# 9. Conception finale consolidée — [ideas_final](ideas/heuristic_ideas_final.fr.md)

`final` n'a **aucun agent associé**. C'est une snapshot de documentation/conception, pas une version mise en œuvre de CHI. Le projet s'est fermé sans successeur validé `CHI16` / `chi_final`.

Contrairement à `v2`, `v3` et `v4`, le document final n'est **pas une différence**. C'est un snapshot autonome obtenu après l'application complète de la chaîne de conception et la résolution des contradictions.

<a id="91-canonical-final-design"></a>
## 9.1 Conception finale canonique

La stratégie finale définit, dans un seul lieu :

- des contraintes mécaniques vérifiées;
- une seule prédiction physique/économique partagée;
- la séparation de l'approvisionnement côté ferme de l'inventaire global du marché;
- des scénarios d'adversaires `LOW / BASE / HIGH`;
- la préservation ou l'abandon conditionnel des actifs;
- un planification consciente des dépendances `TaskGroup`;
- des réservations précises des ressources, des carreaux, des liquidités, des stocks, des temps d'ouvriers et des places de marché;
- `MAX_WORKERS = 14`;
- la géométrie active de placement et les règles d'ouverture fixes;
- expansion terrestre planifiée active et expansion économique non planifiée ;
- production marginale et recherche précise de la quantité de vente ;
- réparation locale au lieu d'une réplanification générale ;
- planification de sortie en cascade inversée ;
- un contrat de vérification et de mise en œuvre.

<a id="92-historical-ideas-remain-traceable"></a>
## 9.2 Les idées historiques restent traçables

Les idées considérées mais non actives sont conservées dans le document final comme une histoire de référence. Les fichiers versionnés restent utiles pour comprendre comment chaque modification a intégré la lignée de conception, tandis que `final` est le snapshot complet résolu pour toute mise en œuvre future.

---

<a id="10-evolution-of-the-heuristic-branch"></a>
# 10. Évolution de la branche heuristique

L'évolution constitue une chaîne de conception stricte : chaque version répond à une question supplémentaire du planificateur sans utiliser les versions antérieures comme parents parallèles.

<a id="chi12--v1--can-the-work-actually-be-executed"></a>
## CHI12 / v1 — Peut-on exécuter ce travail ?

[ideas_v1](ideas/heuristic_ideas_v1.fr.md) établit la base quotidienne complète :

```text
What must be done?
When must it be done?
What resources must be carried?
Can a worker complete the route and return?
Can the shed accept the result?
```

<a id="chi13--v2--should-the-farm-expand"></a>
## CHI13 / v2 — Doit-on étendre l'exploitation ?

[ideas_v2](ideas/heuristic_ideas_v2.fr.md) modifie uniquement la décision sur les terres héritée de `v1` :

```text
Is additional profitable production blocked by land?
What is the best no-purchase plan?
Can the new quadrant be exploited in time?
Does the complete expansion plan repay its cost?
```

<a id="chi14--v3--can-every-subsystem-reason-from-the-same-plan"></a>
## CHI14 / v3 — Peut chaque sous-système raisonner à partir du même plan ?

[ideas_v3](ideas/heuristic_ideas_v3.fr.md) réorganise le planificateur hérité autour de :

```text
one forecast
-> stable TaskGroups
-> integrated routing / logistics / HIRE
-> one market calendar
-> local repair
-> endgame-aware feasibility
```

<a id="v4--how-should-feasible-work-react-to-the-market-and-opponent"></a>
## v4 — Comment les travaux faisables doivent-ils réagir au marché et à l'adversaire ?

[ideas_v4](ideas/heuristic_ideas_v4.fr.md) ajoute :

```text
shop demand
-> own/opponent supply
-> future market inventory
-> expected price
-> marginal production / labor / sell value
```

<a id="final--what-is-the-complete-resolved-strategy"></a>
## final — Quelle est la stratégie complète résolue ?

[ideas_final](ideas/heuristic_ideas_final.fr.md) applique toute la chaîne, résout les heuristiques historiques contradictoires, sépare les règles actives des idées de référence, et reste la référence de conception archivée. Aucune mise en œuvre validée de cette étape n'a été conservée avant la fermeture du projet.

---

<a id="11-architecture-summary"></a>
# 11. Résumé de l'architecture

|Version|Planification|Itinérance / main-d'œuvre|Économie|Expansion|
| --- | --- | --- | --- | --- |
|CHI3|Maintenance dynamique de la production|Itinérance quotidienne dynamique|Minimal|Aucune|
|CHI12 / v1|Priorités + délais + ensembles de ressources|Itinéraires exécutables + HIRE|Decisions économiques de base|Aucune expansion implicite spéculative|
|CHI13 / v2|v1 + décision explicite sur les terres|Planificateur hérité, validé par rapport à l'expansion|Comparaison entre absence de terres et plan de terres|Expansion réservée, observée, validée économiquement|
|CHI14 / v3|Prévision partagée + stabilité de `TaskGroup`|Affectation intégrée, logistique et HIRE|Un calendrier de marché validé|L'expansion consomme le plan partagé|
|v4 (seulement conception)|v3 + couche tactique de marché|Cap sur les ouvriers + valeur marginale de la main-d'œuvre|Logique de réaction à l'adversaire / au prix / à la vente marginale|Préférences de timing tactique + seuil de liquidité|
|final (seulement conception)|Stratégie complète résolue|Réservations exactes + réparation locale|Objectif final en liquidités + recherche marginale exacte|Calendrier actif + porte non planifié économiquement|

---

<a id="12-relationship-with-chi_agentsmd"></a>
# 12. Relation avec `chi_agents.md`

Les deux documents décrivent intentionnellement des historiques différents.

`chi_agents.md` reste le registre de la progression initiale de CHI :

```text
chi.py -> CHI1 -> ... -> CHI10
```

Ce document enregistre la lignée séparée de conception du planheur :

```text
CHI3
  -> heuristic_ideas_v1    -> CHI12
  -> heuristic_ideas_v2    -> CHI13
  -> heuristic_ideas_v3    -> CHI14
  -> heuristic_ideas_v4    -> design only
  -> heuristic_ideas_final -> design only
```

Chaîne de conception canonique :

[ideas_v1](ideas/heuristic_ideas_v1.fr.md) → [ideas_v2](ideas/heuristic_ideas_v2.fr.md) → [ideas_v3](ideas/heuristic_ideas_v3.fr.md) → [ideas_v4](ideas/heuristic_ideas_v4.fr.md) → [ideas_final](ideas/heuristic_ideas_final.fr.md)

CHI3 apparaît donc dans les deux documents pour des raisons différentes :

- dans `chi_agents.md`, c'est la troisième itération historique de CHI ;
- dans `heuristic_agents.md`, c'est la fondation réutilisable de production/état à partir de laquelle le planheur heuristique a été réétabli.


Cette séparation permet de garder l'historique du dépôt lisible sans présenter CHI12 et plus comme des successeurs chronologiques directs de CHI10.
