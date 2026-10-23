[English](chi_agents.md) | [Français](chi_agents.fr.md) | [简体中文](chi_agents.zh-CN.md)

[README du projet](../README.fr.md)

<a id="chi-agents--chipy-to-chi10py"></a>
# Agents CHI — `chi.py` à `chi10.py`

> Portée : la lignée originale de l'heuristique-planner CHI uniquement. Les expériences dérivées publiquement et post-CHI10 sont documentées séparément dans `public_agent.md`.
Ce document décrit les versions successives du planificateur heuristique Kaggriculture basé sur les agents mis en œuvre.

<a id="1-objective"></a>
## 1. Objectif

Le planificateur suit une approche incrémentale :

1.  définir un ouverture déterministe au jour 1 ;
2.  convertir des plans fixes en chemins réutilisables et piles d'actions ;
3.  maintenir la production de cultures et d'animaux après le jour 1 ;
4.  distribuer dynamiquement les tâches quotidiennes ;
5.  réduire les déplacements et les embauches inutiles ;
6.  gérer les pénuries de blé pour l'alimentation des animaux ;
7.  éviter les actions inutiles de soins animaux ;
8.  adapter les itinéraires aux positions réelles d'apparition des travailleurs ;
9.  coordonner les moments de récolte et de vente ;
10. arrêter l'automatisation de la réplante après l'extension de la ferme ;
11. éliminer les mauvaises herbes sur les terrains débloqués ;
12. généraliser les achats de terrain jusqu'aux quatre quadrants.

L'objectif est de garder l'agent déterministe et inspectable tout en rendant progressivement ses décisions dépendantes de l'état réel de la ferme.

<a id="2-initial-prototype-----chipy"></a>
## 2. Prototype initial --- `chi.py`

La version initiale définit directement l'ouverture du jour 1 comme une séquence d'actions.

<a id="day-1-purchases"></a>
### Achats du jour 1

À l'heure 0 :

-   10 graines de blé ;
-   6 graines de carotte ;
-   2 graines de fraise ;
-   1 geai ;
-   2 vaches ;
-   1 Mouton ;
-   16 Blé ;
-   3 ouvriers agricoles.

À l'heure 1 :

-   1 grain de tomate ;
-   2 grain de melon.

<a id="day-1-layout"></a>
### Disposition du jour 1

La disposition des cultures contient :

  Culture           Cases
  ------------ -------
  Blé                 10 Carotte               6 Tomate               1 Fraise             2 Melon                2

La zone animale occupe la zone 2x2 en bas à droite :

  Position   Animal
  ---------- --------
  `(3, 3)`   Canard `(4, 3)`   Vache `(3, 4)`   Mouton `(4, 4)`   Vache

L'agriculteur construit et initialise la zone animale tandis que trois ouvriers agricoles plantent et arrosent la zone des cultures.

Ce prototype ne s'exécute que le jour 1. À partir du jour 2, chaque ouvrier passe.

<a id="3-chi-1-----final-fixed-day-1-opening"></a>
## 3. CHI 1 --- Ouverture fixe du jour 1

CHI 1 conserve la même disposition de ferme mais modifie l'ouverture pour utiliser quatre ouvriers agricoles embauchés.

<a id="main-changes"></a>
### Modifications principales

-   quatre ouvriers agricoles au lieu de trois ;
-   Les graines de blé sont achetées à l'heure 1 ;
-   la zone des cultures est divisée en quatre itinéraires fixes ;
-   l'agriculteur reste dédié à la mise en place de la zone animale.

<a id="fixed-worker-roles"></a>
### Rôles fixes des ouvriers

  Ouvrier   Rôle
  -------- ------------------------------------------------------
  Agriculteur   Construire la zone animale, placer les animaux, les nourrir et les soigner Ouvrier 1   Itinéraire de droite dans la zone des cultures Ouvrier 2   Itinéraire de gauche dans la zone des cultures Ouvrier 3   Itinéraire central dans la zone des cultures Ouvrier 4   Itinéraire court vers la case restante des cultures

Ceci devient l'ouverture fixe du jour 1 réutilisée par les versions ultérieures.

<a id="4-chi-2-----paths-and-action-stacks"></a>
## 4. CHI 2 --- Itinéraires et piles d'actions

CHI 2 remplace les grandes séquences d'actions prédéfinies par une représentation basée sur des chemins.

Les parcours jour 1 deviennent :

``` text
Farmer: W -> N -> E

Hand 1: W -> N -> N -> N -> N -> W -> W -> W -> S

Hand 2: N -> W -> W -> W -> W -> N -> N -> N -> N

Hand 3: W -> N -> W -> N -> N -> N -> W -> S -> W -> S

Hand 4: N -> W -> W
```

Au lieu d'inscrire explicitement chaque `PLANT`, `WATER`, `PLACE`, `FEED` et `CARE` dans le parcours, le planificateur déduit les actions à partir de la case atteinte par l'ouvrier.

Pour les cultures :

``` text
reach crop tile
    -> PLANT
    -> WATER
```

Pour les animaux :

``` text
reach animal tile
    -> BUILD if required
    -> PLACE
    -> FEED
    -> CARE
```

Les actions sont insérées dans une pile et consommées un tick à la fois.

Cette version établit le modèle d'exécution utilisé par les planificateurs suivants.

<a id="5-chi-3-----dynamic-multi-day-planner"></a>
## 5. CHI 3 --- Planificateur dynamique sur plusieurs jours

CHI 3 étend l'agent au-delà du jour 1.

<a id="persistent-farm-state"></a>
### État persistant de la ferme

Le planificateur introduit un état explicite pour chaque case de culture et d'animal.

L'état des cultures suit :

-   type de culture ;
-   si la culture est plantée ;
-   si elle est prête à être récoltée.

L'état des animaux suit :

-   type d'animal ;
-   si l'animal est placé ;
-   production disponible ;
-   fertilisant disponible.

Cet état est actualisé à chaque tick à partir de l'observation.

<a id="crop-production"></a>
### Production des cultures

Le planificateur distingue les cultures à effet unique et les cultures en cours.

  Culture         Type       Âge de récolte
  ------------ ---------- ----------------
  Blé            À effet unique   4 Carottes       À effet unique   3 Tomate         En cours    8, 9, 10, 11 Fraise         En cours    10, 12, 14, 16 Citron         À effet unique   10

Les tâches possibles pour les cultures incluent maintenant :

``` text
WATER
HARVEST
REPLANT
```

Les semences nécessaires à la réplante d'une culture à effet unique sont achetées automatiquement.

<a id="animal-production"></a>
### Production des animaux

Les tâches liées aux animaux peuvent inclure :

``` text
BUILD
PLACE
FEED
CARE
COLLECT_FERTILIZER
HARVEST
```

<a id="dynamic-daily-routing"></a>
### Routing quotidien dynamique

Après le jour 1, le planificateur :

1.  crée des tâches pour les cultures et les animaux ;
2.  estime le coût des actions associées ;
3.  les attribue aux ouvriers disponibles ;
4.  réunit les tâches voisines ;
5.  transforme les coordonnées des tâches en parcours de mouvement ;
6.  recherche le nombre minimal d'embauches permettant de terminer le travail dans la capacité des ouvriers.

C'est la première version où les parcours quotidiens et les embauches sont calculés dynamiquement.

<a id="6-chi-4-----dedicated-livestock-block"></a>
## 6. CHI 4 --- Bloc dédié aux animaux

CHI 4 modifie l'affectation des tâches de sorte que toutes les tâches liées aux animaux soient regroupées sur un seul ouvrier.

Auparavant, les tâches liées aux animaux pouvaient être réparties entre différents ouvriers par l'allocateur générique.

Le nouveau planificateur :

1.  construit le parcours complet des animaux ;
2.  teste quel ouvrier peut l'exécuter ;
3.  attribue le bloc des animaux au plus économique ouvrier valide ;
4.  répartit les tâches de culture sur la capacité restante disponible.

Le parcours des animaux reste continu avant qu'ajoutées des tâches de culture supplémentaires à cet ouvrier.

<a id="purpose"></a>
### Objectif

Cela réduit la fragmentation autour de la zone compacte 2x2 des animaux et rend la gestion des animaux plus prévisible.

<a id="7-chi-5-----wheat-shortage-and-animal-sequencing"></a>
## 7. CHI 5 --- Manque de blé et séquencement des animaux

CHI 5 traite le cas où le bâtiment ne contient pas assez de blé pour nourrir tous les animaux.

Le planificateur dispose maintenant de deux modes.

<a id="normal-mode"></a>
### Mode normal

Utilisé lorsque :

``` text
shed Wheat >= number of animals
```

La route dédiée aux animaux est utilisée.

<a id="wheat-shortage-mode"></a>
### Mode de pénurie de blé

Lorsque le blé est insuffisant, le flux d'activité des animaux est divisé en types de tâches séparés :

``` text
ANIMAL_PRE
WHEAT_SUPPLY
SHED_DROP
WAIT_WHEAT
ANIMAL_FEED
REPLANT_WHEAT
```

Un ouvrier fournisseur :

1.  se rend dans le champ mûr de blé ;
2.  arrose et récolte le blé requis ;
3.  rejoint le centre ;
4.  dépose le blé dans le grenier.

Un ouvrier alimentateur :

1.  rejoint le centre ;
2.  attend que suffisamment de blé soit disponible ;
3.  prend le blé ;
4.  suit la route d'alimentation des animaux.

Les tâches liées à l'animal qui ne nécessitent pas de blé peuvent être effectuées séparément via `ANIMAL_PRE`.

L'ordre d'action des animaux est également modifié afin que les productions et les engrais disponibles soient collectés avant le nouveau cycle d'alimentation et de soins :

``` text
HARVEST if available
COLLECT_FERTILIZER if available
FEED
CARE
```

Cette version résout la dépendance entre la production des cultures et l'alimentation des animaux, au lieu de considérer chaque tâche animale comme immédiatement exécutable.

<a id="8-chi-6-----hiring-and-shortage-route-optimization"></a>
## 8. CHI 6 --- Optimisation de l'embauche et de la route de pénurie

CHI 6 améliore le planificateur de pénurie introduit dans CHI 5.

L'objectif principal est d'éviter de recruter de nouveaux ouvriers simplement parce qu'un ouvrier attend le blé.

<a id="tick-aware-planning"></a>
### Planification consciente des ticks

Le planificateur introduit :

``` text
DAY_TICKS = 24
```

et tient explicitement compte du retard d'un tick lors du début de l'emploi d'ouvriers agricoles.

Le couple fournisseur/alimentateur est sélectionné en fonction du moment estimé à laquelle :

-   le fournisseur peut déposer du blé ;
-   l'alimentateur peut atteindre le grenier ;
-   la route complète d'alimentation peut être terminée.

<a id="use-waiting-time-productively"></a>
### Utiliser le temps d'attente de manière productive

L'alimentateur n'est plus contraint d'attendre inutilement l'arrivée du blé.

Avant `WAIT_WHEAT`, le planificateur tentait d'insérer des tâches pouvant être effectuées pendant qu'il arrivait encore au grenier avant que le fournisseur ne soit arrivé.

La priorité est accordée aux tâches `ANIMAL_PRE`.

Le fournisseur peut également exécuter :

-   la réplante de blé après récolte ;
-   des tâches voisines supplémentaires si la capacité le permet.

<a id="result"></a>
### Résultat

La capacité des ouvriers est utilisée plus efficacement, permettant au planificateur de rechercher des effectifs allant de zéro à un nombre minimal valide.

<a id="9-chi-7-----care-optimization"></a>
## 9. CHI 7 --- Optimisation de CARE

CHI 7 ajoute une conscience de la capacité de production des animaux.

Le planificateur suit maintenant :

``` text
pending_care_bonus
```

pour chaque animal.

La production maximale conservée est représentée par :

  Animal     Production maximale conservée
  -------- -------------------------
  Canard                            4 Vache                              6 Mouton                            6

CARE n'est plus automatiquement ajouté à chaque visite d'animal.

La condition mise en œuvre est :

``` text
pending_care_bonus + 1 < animal maximum held production
```

Si cette condition est fausse, l'action CARE est omise.

Cette condition est utilisée dans :

-   les actions normales des animaux ;
-   les tâches de pénurie `ANIMAL_PRE`.

L'estimateur de coût de trajet inclut CARE uniquement lorsque l'action est effectivement nécessaire, afin que l'embauche et le choix de la route bénéficient d'une charge de travail réduite.

<a id="10-chi-8-----sale-expansion-and-land-management"></a>
## 10. CHI 8 --- Vente, expansion et gestion des terres

CHI 8 étend le planificateur de la maintenance de production à l'expansion de l'exploitation et à la transition vers une stratégie dynamique d'attribution de cases.

<a id="real-worker-positions"></a>
### Postes réels des ouvriers

Le plan quotidien est d'abord basé sur les positions d'ouvriers déduites du modèle d'entrée connu des abris d'accès.

À l'heure 1, une fois que les ouvriers embauchés sont visibles dans l'observation, leurs positions réelles sont enregistrées et les itinéraires sont reconstruits à partir de ces coordonnées.

Cela évite les erreurs de coût de trajet causées par l'hypothèse que tous les ouvriers partent de la même case d'accès à l'abri.

<a id="sale-day-planning"></a>
### Planification du jour de vente

Un jour de vente spécifique est défini avec :

``` text
SALE_DAY = 5
SALE_DROP_HOUR = 22
SALE_HOUR = 23
```

Le jour de vente, la capacité des ouvriers et le coût des trajets tiennent compte du retour à l'abri avant la vente.

Les ouvriers retournent à la zone d'accès à l'abri et déposent leur inventaire avant la vente au marché.

Les carottes atteignant l'âge 2 le jour de vente sont récoltées précocement :

``` text
WATER
HARVEST
```

Elles ne sont pas replantées.

<a id="expansion-mode"></a>
### Mode d'expansion

Le mode d'expansion devient actif dès qu'un quadrant au-delà du premier `NW` est débloqué :

``` text
EXPANSION_ACTIVE = len(unlocked_quadrants) > 1
```

Avant l'expansion, la stratégie initiale de replantation est conservée.

Après l'expansion :

-   les cultures existantes continuent d'être arrosées ;
-   les cultures prêtes continuent d'être récoltées ;
-   les cultures à une seule fois ne sont plus replantées après récolte ;
-   les semences de remplacement ne sont plus achetées ;
-   les cases récoltées vides sont ignorées par le planificateur des cultures.

Cela laisse les cases vides disponibles pour la stratégie dynamique d'attribution de cases prévue pour CHI 9.

<a id="weed-tasks"></a>
### Tâches de débroussaillement

Le planificateur scanne l'ensemble du réseau de l'exploitation pour détecter les mauvaises herbes.

Chaque mauvaise herbe peut générer une tâche explicite :

``` text
WEED
    -> DIG
```

Les mauvaises herbes sont donc incluses dans l'affectation des itinéraires même si elles ne se trouvent pas sur l'une des positions initiales des cultures.

Après l'expansion, la suppression d'une mauvaise herbe ne déclenche pas automatiquement la replantation.

<a id="generalized-land-purchases"></a>
### Achats généralisés de terres

Les prix des terres sont représentés explicitement :

``` text
1 -> 1000
2 -> 2000
3 -> 4000
```

où la clé est le nombre de quadrants déjà débloqués.

Le coût de la prochaine terre est donc :

    Quadrants already unlocked        Next land cost
  ---------------------------- ---------------------
                             1                  1000
                             2                  2000
                             3                  4000

Le planificateur utilise des fonctions dédiées pour déterminer le prix suivant et si le solde disponible est suffisant.

Cela élimine la logique précédente spécifiquement liée au deuxième quadrant `NE` et permet au même mécanisme d'achat de gérer les deuxième, troisième et quatrième quadrants.


<a id="11-chi-9-----dynamic-production-labor-and-endgame-optimization"></a>
## 11. CHI 9 --- Production dynamique, optimisation du travail et stratégie finale

CHI 9 étend le planificateur heuristique avec une stratégie économique et finale plus dynamique.

<a id="dynamic-worker-count-calculation"></a>
### Calcul dynamique du nombre d'ouvriers

Le nombre d'ouvriers embauchés n'est plus uniquement basé sur la capacité de la tâche quotidienne.

Le planificateur recherche d'abord le minimum de main-d'œuvre valide, puis vérifie si l'engagement d'un autre travailleur génère une valeur de production supplémentaire suffisante pour justifier le coût de l'embauche suivante.

L'engagement supplémentaire s'arrête lorsque :

``` text
additional expected profit < next hire cost
```

Cela permet au planificateur d'éviter à la fois une sous-occupation et des travailleurs inutiles lorsque la capacité supplémentaire ne se justifie pas économiquement.

<a id="conditional-crop-watering"></a>
### Réglage conditionnel de l'arrosage des cultures

Les cultures ne sont plus arrosées automatiquement chaque jour.

Le planificateur suit :

``` text
watered_today
consecutive_unwatered
needs_water
```

et crée uniquement une action ARROSAGE lorsque l'arrosage est nécessaire à la survie des cultures ou lorsque une culture prête à la récolte a encore besoin d'être arrosée avant l'action de récolte.

Cela élimine des actions ARROSAGE inutiles et réduit le coût quotidien du parcours.

<a id="endgame-planting-constraints"></a>
### Contraintes de plantation en phase finale

Les décisions de plantation et de réplantation utilisent désormais le calendrier de production des cultures en conjonction avec la journée actuelle.

Une culture est plantée uniquement si sa première récolte peut encore avoir lieu avant la dernière journée utile de récolte :

``` text
planting day + first harvest age <= last harvest day
```

Le même principe s'applique aux nouveaux animaux en fonction de leur première âge de production.

Les productions qui ne peuvent pas générer une récolte à temps pour la vente finale sont donc exclues de :

-   la plantation nouvelle ;
-   la réplantation ;
-   la mise en place des animaux ;
-   l'évaluation de la production ;
-   les commandes de marché.

<a id="dynamic-production-purchasing"></a>
### Achat dynamique de productions

La stratégie précédente fixe de production après l'ouverture du marché est remplacée par un système de sélection de production conscient de son budget.

Pour les cases disponibles ou bientôt vides, le planificateur évalue les cultures et les animaux possibles en utilisant :

-   revenu marginal attendu sur le marché ;
-   coût d'achat de production ;
-   coût attendu de nourriture pour animaux ;
-   coût supplémentaire de main-d'œuvre ;
-   durée d'occupation de la case ;
-   utilisation effective de l'espace.

Les candidats sont évalués selon le bénéfice marginal par unité d'espace et de temps effectivement occupé.

Seules les options de production positives et accessibles sont conservées.

Le plan résultant est ensuite converti en commandes de marché nécessaires pour les semences, les animaux et le blé.

<a id="land-purchase-profitability"></a>
### Profitabilité de l'achat de terres

L'extension de la terre est également évaluée en fonction de la production projetée.

Avant d'acheter un nouveau quadrant, le planificateur estime :

-   la production qui peut encore être installée sur la nouvelle terre ;
-   le bénéfice marginal attendu ;
-   les besoins en travailleurs résultants ;
-   les coûts de semences, d'animaux et de nourriture ;
-   le coût supplémentaire d'embauche.

L'achat est conservé uniquement lorsque la production projetée reste accessible et suffisamment rentable par rapport au prix de la terre.

L'extension finale coûtant 4000 est également désactivée après le jour 19.

<a id="continuous-sales"></a>
### Ventes continues

À partir du jour 6, les produits non blé récoltés peuvent être vendus directement depuis le local au lieu d'attendre une liquidation ultérieure.

L'ensemble des ventes quotidiennes inclut :

``` text
CARROT
TOMATO
STRAWBERRY
MELON
EGG
MILK
WOOL
```

Le fertilisant reste vendable indépendamment.

<a id="final-liquidation"></a>
### Liquidation finale

Le jour 29, les ouvriers commencent à revenir vers le centre d'accès au grenier avant la liquidation finale du marché.

À partir de l'heure 22, tout produit vendable restant dans le grenier est soumis au marché :

``` text
SELL all remaining market products
```

Cela assure que les produits encore tenus à la fin de la partie soient convertis en argent avant la fin du jeu.



<a id="additional-retained-improvements"></a>
### Améliorations supplémentaires

Les principales ajouts sont intentionnellement limités à :

- évaluation de la production consciente des événements et du marché ;
- estimations de la production animale avec prise en compte de la CARE ;
- protection contre le dépassement du grenier ;
- ventes mesurées pour des produits sensibles au prix ;
- logistique basée sur le grenier le plus proche en utilisant les quatre cases d'accès valides au grenier ;
- coûts de recrutement étendus selon la suite de Fibonacci sans limite artificielle de 10 mains ;
- synchronisation plus sûre de l'état de production lorsque le type de production d'une case change.

Ces modifications conservent l'algorithme de routage glouton tout en améliorant le modèle économique et la robustesse de l'exécution.


<a id="12-chi-10-----observation-checked-execution-and-cash-flow-planning"></a>
## 12. CHI 10 --- Exécution vérifiée et planification du flux de trésorerie

CHI 10 conserve la structure du planificateur CHI 9 et se concentre sur le rapprochement entre l'exécution et les estimations économiques et l'état réel du jeu.

Les principales ajouts sont :

- projections de la disponibilité des fournitures propres et adverses basées sur les événements ;
- simulation du prix de marché unitaire pour les ventes projetées ;
- decisions de production et de recrutement sensibles au flux de trésorerie ;
- validation des actions en file d'attente des ouvriers contre l'observation actuelle avant exécution ;
- gestion adaptative des ventes et de la capacité du grenier, incluant les produits déposés pendant le tour actuel ;
- gestion plus serrée des itinéraires à la fin du jeu et de la liquidation.

CHI 10 conserve l'architecture de routage glouton tout en améliorant la validation de l'exécution et la planification économique.

<a id="chi-10-temporal--experimental-rolling-horizon-scheduler"></a>
### CHI 10 Temporel — planificateur expérimental à horizon glissant

`src/agents/chi10_temporal.py` est une variante autonome avec le début de CHI 10 et le modèle économique. Après le début, il reconstruit un calendrier temporel à partir des positions observées des ouvriers, des cases et des stocks à chaque tick.

Le planificateur conserve jusqu'à quatre affectations alternatives (deux pendant les estimations quotidiennes de recrutement). Il peut ignorer une tâche optionnelle afin de laisser du temps à une chaîne plus valorisante. Les tâches sont traitées dans un ordre de priorité compatible avec les préférences fixes ; ce n'est qu'une heuristique bornée, pas un solveur globalment optimal.

Le calendrier tient compte de :

- une action ou un déplacement par ouvrier par tick ;
- l'arrosage avant la récolte, et la plantation suivie de l'arrosage obligatoire ;
- des réservations partagées de semences, des retours d'animaux et de la disponibilité du blé ;
- des dépendances entre la récolte, le dépôt et le retrait du blé entre les ouvriers ;
- la disponibilité des ouvriers embauchés et des ressources achetées à l'heure suivante ;
- le retour en transit et les dépôts avant la fin de l'horizon.

Les estimations quotidiennes de commande supposent que les fournitures nécessaires peuvent être achetées. L'exécution en temps réel utilise uniquement les stocks observés, vérifie les actions dans l'ordre des ouvriers, limite les dépôts à la capacité de salle disponible et inclut les transferts de même tour dans les ventes. Les achats échoués ou les changements d'état inattendus sont gérés par une réplanification. La congestion de la grange et les prix futurs des ventes restent approximatifs dans la recherche.

Avec la partie par défaut de 720 étapes, l'observation actionnable finale est le jour 29, heure -22. Le calendrier final réserve du temps pour déposer avant que cette action ne se termine ; les dépôts automatiques à la fin de la journée ne peuvent pas être comptés pour la vente finale.

Les routings gloutons inutilisés, l'exécution en file d'attente, les paramètres anciens de vente et les aides de calcul de production obsolètes ont été supprimés de cette version. L'agent utilise uniquement la bibliothèque standard de Python et prend en charge les paramètres par défaut du jeu.

Exécuter les tests ciblés depuis le répertoire racine :

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_chi10_temporal.py -q -p no:cacheprovider
```

Les vérifications de partie complète sont facultatives. Elles utilisent deux grappins dans les deux positions joueuses contre CHI 10, valident la complétude et vérifient les actions des ouvriers avec le moteur réel. Le résultat JUnit enregistre les récompenses et le temps maximum mesuré d'action :

```powershell
$env:RUN_KAGGRICULTURE = "1"
.\.venv\Scripts\python.exe -m pytest tests/test_chi10_temporal.py -q -p no:cacheprovider -o junit_family=xunit1 --junitxml=experiments/chi10_temporal_validation.xml
Remove-Item Env:RUN_KAGGRICULTURE
```

Ces vérifications couvrent l'exécution dans les scénarios testés ; elles ne démontrent pas une amélioration compétitive par rapport à CHI 10.

<a id="13-version-summary"></a>
## 13. Résumé de la version

|Version|Amélioration principale|
| --- | --- |
| `chi.py` |Prototype initial fixe du jour 1 avec trois ouvriers agricoles|
| `chi1.py` |Ouverture finale fixe du jour 1 avec quatre ouvriers agricoles|
| `chi2.py` |Les parcours fixes ont été convertis en piles d'actions générées|
| `chi3.py` |Suivi de l'état, logique de récolte/repontage et routage dynamique sur plusieurs jours|
| `chi4.py` |Bloc complet de bétail attribué à un seul ouvrier|
| `chi5.py` |Workflow de pénurie de blé et tâches séparées de pré-alimentation des animaux|
| `chi6.py` |Planification de pénurie sensible aux ticks et réduction de l'embauche|
| `chi7.py` |Les actions CARE ont été adaptées à la prime en attente et à la capacité de production des animaux|
| `chi8.py` |Routage le jour de vente, démarrage réel des ouvriers, mode sans expansion de replantation, nettoyage des mauvaises herbes et achats généralisés de terres|
| `chi9.py` |Achats dynamiques de production, évaluation sensible aux événements/marchés, embauche basée sur le bénéfice, protection de la grange, ventes mesurées, logistique plus sûre et coupures de production en fin de partie|
| `chi10.py` |Exécution vérifiée par observation, évaluation du flux de trésorerie basée sur les événements et gestion adaptative des ventes|
| `chi10_temporal.py` |Un planificateur expérimental à horizon glissant construit à partir du modèle d'ouverture/économique de CHI10|
