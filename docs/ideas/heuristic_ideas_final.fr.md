[English](heuristic_ideas_final.md) | [Français](heuristic_ideas_final.fr.md) | [简体中文](heuristic_ideas_final.zh-CN.md)

[README du projet](../../README.fr.md)

<a id="heuristic-ideas--final-consolidated-strategy"></a>
# Idées heuristiques — Stratégie finale consolidée

[← Dernière variation de conception](heuristic_ideas_v4.fr.md) · Version finale consolidée

> **Convention de série**
>
> `heuristic_ideas_final.md` n'est **pas une autre variation**. C'est l'ensemble complet et autonome du tableau stratégique obtenu après l'application de `v1 -> v2 -> v3 -> v4` et la résolution des contradictions restantes. C'est la référence autonome canonique pour la branche heuristique.

<a id="identity"></a>
## Identité

|Champ|Valeur|
| --- | --- |
|Version| `final` |
|Agent associé|Aucun — conception uniquement|
|Rôle|Tableau stratégique complet autonome|
|Construit à partir de|[`v4`](heuristic_ideas_v4.fr.md), avec l'héritage complet de `v1 -> v4` déjà résolu|
|Statut canonique|**Référence stratégique complète autonome**|
|Statut d'implémentation|Conception uniquement — projet fermé sans agent dédié validé|

<a id="status"></a>
## Statut

Ce document consolide les segments `heuristic_ideas_v1` à `v4`, élimine les idées redondantes, résout les contradictions et sépare les mécanismes vérifiés, les règles stratégiques actives, les règles économiques et les heuristiques historiques uniquement de référence.

C'est la **seule référence stratégique complète** pour la stratégie heuristique résolue. Le projet est fermé sans mise en œuvre validée de cette conception complète ; il est conservé pour traçabilité plutôt que présenté comme comportement mis en œuvre. Les ouvertures fixes, le seuil de travail, le calendrier d'achat de terrain, l'ordre d'achat de terrain, la disposition triangulaire et la restriction centrale de `2 x 2` définies ci-dessous font partie de la base de conception et ne sont pas des hypothèses historiques uniquement de référence.

Les formules historiques et les calendriers micro-établis explicitement classés comme uniquement de référence restent désactivés par défaut.

---

<a id="0-rule-precedence"></a>
## 0. Précédence des règles

Lorsque deux règles sont en conflit, les appliquer dans l'ordre suivant :

1. **Contrainte mécanique du jeu** — ne doit jamais être violée.
2. **Contrainte de faisabilité / de sécurité** — ressources, survie, délais, itinéraires, stockage, places de marché, liquidités exécutables et seuil de liquidités pour l'achat de terrain.
3. **Règle stratégique active** — ouverture fixe, seuil stratégique de travail, achat de terrain planifié, ordre fixe d'expansion, géométrie de placement triangulaire et restriction centrale de `2 x 2`.
4. **Préservation du plan accepté** — protéger les actifs/actions qui restent encore utiles.
5. **Valeur économique marginale** — choisir l'action incrémentale la plus bénéfique, non obligatoire.
6. **Efficiency de routage / d'efficacité spatiale** — réduire l'utilisation des travailleurs et les déplacements.
7. **Heuristique historique uniquement de référence** — désactivée par défaut, sauf activation explicite pour une expérience isolée.

Les règles stratégiques actives sont des engagements intentionnels. Elles ne sont pas dégradées en priorités optionnelles par le modèle général de valeur marginale. Elles restent soumises aux mécanismes et à la faisabilité.

---

<a id="1-verified-mechanical-baseline"></a>
# 1. Base mécanique vérifiée

Le planificateur doit modéliser explicitement les faits suivants.

<a id="11-survival-and-production"></a>
## 1.1 Survie et production

- Une plantation devient une mauvaise herbe après deux jours consécutifs sans eau.
- Une culture nouvellement plantée doit être arrosée le jour de sa plantation.
- Un animal s'échappe après deux jours consécutifs sans blé.
- Un animal nouvellement placé peut survivre à son premier jour sans nourriture, mais la planification normale doit toujours tenir compte de la prochaine date limite de survie.
- Les produits animaux stockés sur la case sont limités par `max_held`.
- Chaque animal survivant peut produire un engrais par jour ; l'engrais non ramassé ne s'accumule pas.
- Le comportement de `CARE` présente une anomalie observée dans les tests de référence actuels, donc un saut agressif de soins basé uniquement sur un modèle théorique de `pending_care_bonus` est unsafe jusqu'à ce que le comportement soit entièrement expliqué.

<a id="12-storage"></a>
## 1.2 Stockage

```text
SHED_CAPACITY = 100 non-seed items
```

Les graines ne consomment pas de capacité libérée.

La condition exacte de surcharge pour une chute planifiée est :

```text
ProjectedShedAfterDrop > 100
```

Un tampon de sécurité de une case peut être utilisé facultativement :

```text
SafetyTarget = 99
```

mais `99` est une cible de politique, pas la capacité réelle.

<a id="13-market-actions"></a>
## 1.3 Actions du marché

- Au plus 10 ordres de marché peuvent être soumis en une étape.
- Les ordres au-delà de la limite peuvent être ignorés silencieusement par l'environnement.
- `BUY`, `SELL`, `HIRE` et `BUY_LAND` partagent donc un calendrier de marché validé.
- L'ordre de soumission des ordres de marché est important.
- Les ordres du joueur interagissent avec les ordres de l'adversaire et la courbe de prix lors de l'exécution.

<a id="14-land"></a>
## 1.4 Terres

Les coûts d'extension sont :

```text
1st expansion = 1000
2nd expansion = 2000
3rd expansion = 4000
```

L'ordre d'extension est fixe dans le jeu et ne doit pas être optimisé ou permute par la stratégie :

```text
1st expansion -> NE
2nd expansion -> SW
3rd expansion -> SE
```

Un quadrant acheté ne fournit pas de cases physiques avant que l'achat ne soit observé comme confirmé.

---

<a id="15-workers"></a>
## 1.5 Ouvriers

Les main-d'œuvre agricoles sont embauchées pour la journée actuelle et le coût d'embauche augmente selon la suite de Fibonacci quotidienne. La suite de coût d'embauche se réinitialise chaque jour.

La limite d'ouvriers du moteur de jeu et la limite d'ouvriers de la stratégie sont des concepts distincts.

La stratégie de base utilise le suivant **cap stratégique rigide actif** :

```text
MAX_WORKERS = 14
```

Le planificateur ne doit jamais accepter un `HIRE` qui ferait dépasser le nombre d'ouvriers contrôlés à 14, même si l'ajout d'un 15e ouvrier aurait une valeur marginale estimée positive. C'est une règle de stratégie, pas une affirmation sur la capacité maximale possible du moteur.

---

<a id="16-shop-demand"></a>
## 1.6 Demande du magasin

La composition du magasin modifie la demande et doit être représentée explicitement. Plusieurs instances se superposent pour leur demande.

Un produit normal demandé contribue environ 6 unités/jour par instance de magasin ; 2 magasins contribuent environ 12 unités/jour pour leur produit doublé.

---

<a id="2-planner-architecture"></a>
# 2. Architecture du planificateur

Utiliser un état de planification cohérent plutôt que des approximations séparées.

```text
OBSERVE REAL STATE
    -> UPDATE SHARED FORECAST
    -> UPDATE MARKET / OPPONENT SCENARIOS
    -> GENERATE ECONOMIC CANDIDATES
    -> GENERATE DEPENDENCY-AWARE TASK GROUPS
    -> ASSIGN ROUTES + LOGISTICS + OPTIONAL HIRES
    -> VALIDATE CASH / STOCK / MARKET CALENDAR
    -> EXECUTE
    -> LOCAL REPAIR WHEN MATERIAL STATE CHANGES
```

Chaque sous-système lit la même prévision et les réservations.

---

<a id="3-shared-forecast"></a>
# 3. Prévision partagée

Maintenir une prévision dérivée physique/économique à partir de la case actuelle **jusqu'à la fin du jeu**.

Suivre au moins :

- l'âge des cultures, l'état de l'eau, l'état de l'engrais, la production suivante et la dégradation ;
- l'alimentation des animaux, les soins, les produits conservés, la production suivante et le risque de saturation ;
- les graines, les produits, les animaux et l'engrais actuels et réservés ;
- la position des ouvriers, leur disponibilité, leur suffixe de route et leur inventaire transporté ;
- réduire les stocks et les débits entrants indexés sur le temps ;
- occupation des tuiles et libération future ;
- argent et dépenses engagées ;
- demande de vente dans les boutiques ;
- commandes de marché prévues pour soi-même ;
- comportement de marché prévu de l'adversaire ;
- inventaire de marché et trajectoire prévue des prix ;
- viabilité de la liquidation en fin de partie.

Après une modification, mettez à jour uniquement les composants de prévision affectés lorsque possible.

---

<a id="4-separate-farm-production-from-market-inventory"></a>
# 4. Séparer la production des fermes de l'inventaire de marché

C'est une correction critique conservée par le modèle économique consolidé.

Un cultive devenant récoltable ne ajoute pas directement des unités à l'inventaire global du marché. La production devient d'abord inventaire de ferme/ouvrier/abri. L'inventaire global du marché change uniquement lorsque des unités entrent ou quittent le marché ou sont consommées.

Utiliser deux prévisions séparées.

<a id="41-farm-side-supply-forecast"></a>
## 4.1 Prévision de l'offre côté ferme

```text
FarmOutput(t) = expected harvest / animal production available to us at t
```

Cela détermine ce que nous pourrions ensuite garder, consommer ou vendre.

<a id="42-market-inventory-forecast"></a>
## 4.2 Prévision de l'inventaire de marché

```text
MarketInventory(t + 1) =
    MarketInventory(t)
    + ExpectedOurSales(t)
    + ExpectedOpponentSales(t)
    - ExpectedOurPurchases(t)
    - ExpectedOpponentPurchases(t)
    - ShopConsumption(t)
```

Inclure uniquement une autre source de consommation si elle est explicitement représentée par l'environnement/les règles actuels.

Ensuite :

```text
ExpectedPrice(t) = PriceFunction(ExpectedMarketInventory(t))
```

Cela empêche le planificateur de valoriser les produits non vendus comme s'ils avaient déjà inondé le marché.

---

<a id="5-opponent-model-scenarios-not-false-precision"></a>
# 5. Modèle de l'adversaire : scénarios, pas de précision fausse

Suivre la capacité visible de l'adversaire :

- type de culture plantée / nombre / âge ;
- type d'animal / nombre ;
- dates prévues de maturité et de production ;
- événements de récolte visibles ;
- changements d'inventaire de marché observés cohérents avec l'achat/vente de l'adversaire.

Maintenir trois scénarios bornés sans inventer de poids de probabilité :

```text
LOW opponent supply
BASE opponent supply
HIGH opponent supply
```

Convention de base :

- utiliser `BASE` comme scénario central pour le classement par valeur attendue ;
- utiliser `LOW` et `HIGH` pour exposer la sensibilité et le risque de crise de marché ;
- ne pas calculer une moyenne pondérée arbitraire sauf si des poids de scénario sont ultérieurement configurés et validés ;
- ne pas inventer un coefficient numérique `RiskPenalty`.

Lorsque deux choix ont une valeur égale de `BASE`, privilégier celui qui reste viable et moins fragile dans les scénarios `LOW/HIGH` avant d'appliquer les règles de rupture globale.

Les observations confirmées reçoivent une confiance pleine. Le comportement futur des boutiques ou de l'adversaire non révélé doit rester basé sur des scénarios plutôt que d'être converti en précision fausse.

---

<a id="6-economic-acceptance-rule"></a>
# 6. Règle d'acceptation économique

Un candidat économique non obligatoire est accepté uniquement s'il possède une **chaîne complète d'extinction en espèces** faisable et valorisante. Les engagements stratégiques actifs définis par ce document sont gérés par leurs propres portes.

Pour un candidat `i` :

```text
IncrementalValue_i =
    IncrementalExpectedSalesRevenue
    - IncrementalDirectCashCost
    - IncrementalFeedOpportunityCost
    - IncrementalHireCost
    - IncrementalHolding / StorageCost
    - IncrementalRoutingOpportunityCost
```

Des termes stratégiques optionnels peuvent être ajoutés uniquement s'ils représentent une véritable option future :

```text
+ LayoutOptionValue
+ DemandHedgeValue
+ ResourceSecurityValue
```

Porte d'acceptation :

```text
IncrementalValue_i > 0
AND all feasibility constraints pass
AND cash-out can occur before the game ends
```

Ne pas accepter un candidat simplement parce qu'il a un ratio élevé si sa valeur absolue est négative.

---

<a id="7-land-scarcity-and-land-time-value"></a>
# 7. Scarcité des terres et valeur du temps sur les terres

L'efficacité du temps sur les terres est utile uniquement lorsque les terres sont réellement rares.

Pour classer les candidats positifs ayant une valeur élevée sous pression terrestre :

```text
LandEfficiency_i =
    IncrementalValue_i
    / EffectiveOccupiedLandTime_i
```

Ne pas utiliser ce ratio comme objectif universel. Lorsque la terre n'est pas un facteur limitant, la valeur incrémentale absolue est plus importante.

Distinction :

```text
PhysicalOccupancy = real map tiles reserved over time
EconomicEffectiveLand = optional comparison metric
```

Par exemple, la valeur historique `5/3` équivalente au terrain pour les oiseaux peut rester un poids économique expérimental, mais elle ne doit jamais remplacer les réservations réelles de parcelles.

---

<a id="8-labor-economics"></a>
# 8. Économie du travail

<a id="81-feasibility-first"></a>
## 8.1 Priorité de faisabilité

Les travailleurs existants sont attribués en premier. Un nouveau salarié est testé uniquement lorsqu'une tâche utile ne peut pas être réalisée autrement de manière économique.

<a id="82-correct-marginal-hire-test"></a>
## 8.2 Test marginal de recrutement

Soit :

```text
ProfitWithoutHire = best feasible plan with A workers
ProfitWithHire    = best feasible plan with A + 1 workers
MarginalWorkerValue = ProfitWithHire - ProfitWithoutHire
```

Embaucher uniquement si :

```text
MarginalWorkerValue > NextHireCost
```

et que le nouveau travailleur rend effectivement la tâche en question faisable.

<a id="83-labor-shadow-cost"></a>
## 8.3 Coût sombre du travail

Ne pas utiliser :

```text
Va * required_actions
```

lorsque `Va` est déjà la valeur totale d'un autre travailleur entier ; cela mélange des unités et peut entraîner une double comptabilisation massive du travail.

Au lieu de cela, estimer un coût d'opportunité par tick / par action provenant de la capacité limitée de travailleurs :

```text
LaborShadowCostPerTick ~=
    value of the best displaced task per scarce worker tick
```

ou utiliser la différence exacte entre le meilleur calendrier avec et sans le candidat.

La différence exacte du calendrier est préférée lorsque le coût est raisonnable.

<a id="84-active-worker-cap"></a>
## 8.4 Limite sur le nombre d'employés actifs

```text
MAX_WORKERS = 14
```

Cette limite est **activée par défaut** et fait partie de la stratégie de base.

L'embauche requiert toujours une valeur marginale positive et une faisabilité réelle du calendrier, mais même une embauche rentable est rejetée si elle créerait 15 employés ou plus.

---

<a id="9-asset-preservation-is-conditional-not-absolute"></a>
# 9. La préservation des actifs est conditionnelle, pas absolue

Les priorités de survie s'appliquent uniquement aux actifs que le plan accepté prévoit de conserver.

Définir :

```text
KeepAsset(asset) = remaining expected value of preserving asset > abandonment alternative
```

Ensuite :

- la survie `WATER` est `CRITICAL` uniquement pour une installation à conserver ;
- la survie `FEED` est `CRITICAL` uniquement pour un animal à conserver ;
- les fertilisants, soins ou nourriture tardifs sans effet futur commercialisable doivent être supprimés ;
- un actif déjà perdu peut être abandonné s'il ne présente pas de valeur d'exploitation restante négative.

Cela résout la contradiction entre les priorités de survie en début de jeu et la liquidation à la fin du jeu.

---

<a id="10-taskgroup-model"></a>
# 10. Modèle de groupe de tâches

Générer directement des objets stables `TaskGroup` sensibles aux dépendances.

```text
TaskGroup:
    id
    position
    ordered_actions[]
    priority
    deadline
    required_resources
    expected_incremental_value
    dependencies
    assigned_worker_or_none
```

Les identifiants stables doivent empêcher la planification dupliquée lorsqu'une génération se déroule deux fois sans changement de l'état matériel.

Les prérequis héritent de l'urgence de la tâche dépendante.

---

<a id="11-action-priority"></a>
# 11. Priorité des actions

Utiliser une hiérarchie de priorités conditionnelle.

<a id="critical"></a>
## CRITIQUE

Seulement lorsque l'actif/la tâche sous-jacente reste partie intégrante du plan accepté :

- arrosage de survie ;
- alimentation de survie ;
- récolte avant dégradation / saturation / perte irréversible ;
- arrosage obligatoire le jour de plantation ;
- libération du stock nécessaire avant une chute entrante obligatoire ;
- dépendance au marché requise avant une date limite rigide.

<a id="production"></a>
## PRODUCTION

- récolte planifiée rentable ;
- plantation / construction / placement obligatoires ;
- alimentation productive obligatoire ;
- récolte / achat de ressources obligatoires.

<a id="yield"></a>
## YIELD

- fertilisant rentable;
- soin rentable;
- eau augmentant la récolte.

<a id="preparation"></a>
## PREPARATION

- excavation pour une production acceptée;
- installation pour une production future acceptée.

<a id="secondary"></a>
## SECONDARY

- collecte de fertilisant non urgente;
- suppression optionnelle des mauvaises herbes;
- travail local optionnel.

---

<a id="12-action-ordering-use-dependencies-not-one-universal-sequence"></a>
# 12. Ordre des actions : utiliser les dépendances, pas une séquence universelle

Éviter une séquence universelle animale telle que :

```text
FEED -> HARVEST -> CARE -> COLLECT
```

pour chaque visite.

Au contraire, imposer uniquement les dépendances qui comptent dans l'état actuel.

Exemples :

- `FEED -> CARE` lorsque le soin exige que l'animal soit nourri ce jour-là;
- `HARVEST` avant l'événement de production suivant lorsque la saturation `max_held` entraînerait une perte de rendement;
- `HARVEST` avant les délais de retour/vente de la fin de jeu;
- `COLLECT_FERTILIZER` uniquement lorsque sa valeur dépasse le coût d'opportunité de l'action/du trajet;
- pour les cultures, `FERTILIZE -> WATER` lorsque le fertilisant doit déjà être actif pour que l'arrosage améliore le rendement;
- `WATER -> HARVEST` uniquement lorsque le changement d'arrosage du jour même modifie le rendement récoltable.

Cela évite d'employer des actions simplement pour respecter une séquence fixe historique.

---

<a id="13-animal-care-policy"></a>
# 13. Politique de SOIN de l'animal

Étant donné que les tests de référence actuels rapportent une anomalie non résolue concernant le soin, utiliser une logique de soin conservatrice.

Le soin est autorisé lorsque :

```text
expected additional saleable yield
    * expected marginal sale value
>
CARE action/travel opportunity cost
```

mais ne saute pas de manière agressive le soin simplement parce qu'un calcul simplifié `pending_care_bonus` prédit aucun bénéfice.

Les calendriers de soin candidats tels que `skip T5` ou `skip T5-T7` restent exclusifs aux benchmarks jusqu'à ce que l'anomalie de production soit expliquée et reproduite de manière fiable.

---

<a id="14-animal-harvest-policy"></a>
# 14. Politique de RÉCOLTE de l'animal

Récolter la production de l'animal lorsque l'une des conditions suivantes est remplie :

```text
1. saturation risk before the next opportunity to harvest
2. planned near-term sale requires the output
3. an existing route passes close enough that marginal labor/travel cost is low
4. endgame requires collection now to allow return + DROP + SELL in time
```

Sinon, reporter la récolte afin de préserver le travail.

Règle finale :

- si la dernière production utile de l'animal doit être vendue le dernier jour jouable, planifier la récolte assez tôt — potentiellement la veille — pour garantir le retour, la chute et la vente.

---

<a id="15-placement-policy"></a>
# 15. Politique de placement

Le placement suit d'abord les contraintes géométriques, puis utilise des critères économiques ou de routage. Ne pas inventer des coefficients de placement pondérés.

<a id="151-mandatory-center-facing-5-x-5-triangular-animal-layout"></a>
## 15.1 Disposition obligatoire centrée vers le nord `5 x 5` de triangle animal

Les lignes suivantes sont écrites du nord au sud et les colonnes de l'ouest à l'est.

`1` = cellule autorisée pour le placement de l'animal selon la disposition triangulaire.   `*` = pas une cellule de placement de l'animal.

Pour le quadrant Nord-Ouest, utiliser exactement :

```text
NW
* * * * 1
* * * 1 1
* * 1 1 1
* 1 1 1 1
1 1 1 1 1
```

Appliquer une symétrie exacte pour les autres quadrants :

```text
NE
1 * * * *
1 1 * * *
1 1 1 * *
1 1 1 1 *
1 1 1 1 1
```

```text
SW
1 1 1 1 1
* 1 1 1 1
* * 1 1 1
* * * 1 1
* * * * 1
```

```text
SE
1 1 1 1 1
1 1 1 1 *
1 1 1 * *
1 1 * * *
1 * * * *
```

Les animaux doivent être placés dans les cellules `1` du triangle centré correspondant. Lorsque plusieurs cellules sont éligibles, remplir ou choisir au sein du triangle selon l'ordre de rupture global plutôt qu'un score pondéré arbitraire.

<a id="152-central-2-x-2-long-term-crop-exclusion"></a>
## 15.2 Exclusion centrale `2 x 2` des cultures à long terme

L'aire centrale `2 x 2` à forte connectivité a une **interdiction absolue** sur les cultures à long terme :

```text
if tile in CENTRAL_2X2 and crop is LONG_TERM_CROP:
    placement is forbidden
```

Ceci est une contrainte stratégique active, et non une préférence sur le coût d'opportunité. La production à court terme et les utilisations non agricoles restent soumises à leurs propres règles de faisabilité. L'implémentation doit utiliser la classification explicite à long terme des cultures du projet, si elle existe ; elle ne doit pas inventer un seuil de durée de manière silencieuse.

<a id="153-placement-tie-break-without-arbitrary-weights"></a>
## 15.3 Comparaison des emplacements sans poids arbitraires

Après que la géométrie rigide et la faisabilité aient été satisfaites, comparez les emplacements dans l'ordre suivant :

```text
1. higher expected economic value
2. smaller deadline slack
3. fewer worker/labor ticks required
4. less travel
```

Si le lien persiste, utilisez un ordre coordonnée stable et déterministe afin que plusieurs planifications produisent le même résultat.

---

<a id="16-land-purchase"></a>
# 16. Achat de terres

L'achat de terres comporte deux modes : **expansion stratégique planifiée** et **expansion économique non planifiée**.

<a id="161-scheduled-strategic-expansion"></a>
## 16.1 Expansion stratégique planifiée

Le calendrier de base est actif et suit l'ordre défini par le jeu `NE -> SW -> SE`. Ici, `Tn` désigne **la journée n** ; soumettez l'achat au premier tick de marché légal de cette journée.

```text
T4:
    BUY NE

AT T7, once the first two shops are known:

    IF the first two shops contain animal demand:
        T7  -> BUY SW
        T12 -> BUY SE

    ELSE:
        T9 -> BUY SW
        no mandatory T12 SE purchase
```

Le premier achat `NE` est donc indépendant de la branche des deux premières boutiques. Cette branche modifie le moment de `SW` et détermine si `SE` est obligatoire à `T12`.

Chaque achat planifié est exécuté lorsque toutes les conditions suivantes sont remplies :

```text
purchase is legal and executable
AND required market slot is available
AND cash-floor / operating-reserve constraint passes
```

Utilisez le seuil explicite de liquidité :

```text
cash
- land_cost
- days_until_next_income * average_labor_price
> 300
```

Lorsqu'une estimation plus précise de la réserve opérationnelle est disponible, elle peut également la vérifier :

```text
CashAfterPurchase >=
    ImmediateDeploymentCost
    + RequiredOperatingSpendUntilNextReliableIncome
```

Un achat planifié constitue une engagement stratégique actif ; il n'est **pas annulé simplement parce que la comparaison du seuil marginal de valeur sans terre préfère ne pas s'agrandir**. Les mécanismes et les ressources financières ou la faisabilité le surmontent toujours.

Si un achat planifié ne peut être exécuté à son heure cible en raison d'un échec du seuil de liquidité ou d'une dépendance mécanique rigide, conservez-le en attente et réévaluez-le au premier tick légal ; ne supprimez pas silencieusement cet engagement.

<a id="162-unscheduled--additional-expansion"></a>
## 16.2 Expansion non planifiée / expansion supplémentaire

Tout achat de terres non requis par le calendrier ci-dessus utilise la porte de terre économique :

1. calculez le plan optimal sans achat ;
2. simulez la prochaine expansion légale sur un état copié ;
3. réservez l'utilisation future exacte des nouvelles cases ;
4. incluez la déploiement, l'entretien, la capacité de travailleurs, le routage, les stocks et les ventes ;
5. validez le calendrier de marché et la réserve de liquidité ;
6. exigez un gain réel positif d'argent final incrémental.

Après que tout achat soit confirmé, son coût est irréversible. La production future sur cette terre est réévaluée à partir des coûts restants et de la valeur uniquement.

---

<a id="17-shop-dependent-expansion-branch"></a>
# 17. Branche d'expansion dépendante des boutiques

Les deux premières boutiques sont utilisées uniquement lorsque la branche devient observable à `T7`. Elles **ne** modifient pas de manière rétroactive l'achat obligatoire `T4 -> NE`.

Définissez `animal demand` exactement comme suit : au moins une des deux premières boutiques consomme `EGG`, `MILK` ou `WOOL`.

Résumé de la décision :

```text
T4 -> NE always

At T7:
    first two shops contain animal demand
        -> SW at T7
        -> SE at T12

    first two shops contain no animal demand
        -> SW at T9
        -> no mandatory SE at T12
```

La direction de l'expansion elle-même n'est pas un choix : l'ordre du moteur est `NE -> SW -> SE`. La stratégie choisit uniquement si et quand l'achat planifié est déclenché selon la règle ci-dessus.

---

<a id="18-event-driven-phases-instead-of-hard-phase-boundaries"></a>
# 18. Phases déclenchées par des événements au lieu de frontières rigides

Les phases historiques :

```text
T0-T3
T4-T20
T20-T30
```

sont utiles comme prémisses descriptives mais ne doivent pas être des changements stratégiques rigides.

Préférez les changements de régime déclenchés par des événements :

```text
OPENING:
    little shop information, establish resilient production

EXPANSION / ADAPTATION:
    new shop information materially changes marginal values

CAPACITY-LIMITED MIDGAME:
    land/labor/storage become binding constraints

LIQUIDATION HORIZON:
    new investments fail full cash-out feasibility
```

L'instant exact de la transition émerge de la prévision plutôt qu'une date fixe.

---

<a id="19-inventory-reservations"></a>
# 19. Réservations de stock

Pour chaque produit, maintenez :

```text
AvailableStock
ReservedForOperations
ReservedForConfirmedDemand
ReservedForPlannedProduction
UncommittedStock
```

Ne pas utiliser des quantités de réserve fixes spécifiques au produit lorsque la prévision datée peut calculer directement le besoin.

Les réserves historiques restent des priorités de secours :

- Blé : réserve pour alimentation + réserve d'urgence ;
- Œuf : petite réserve avec la demande de la boulangerie/du petit-déjeuner ;
- Carotte : petite réserve avec la demande du PetCafe/du marché des fermiers ;
- Fraise/Lait : réserve plus importante lorsque la pénurie à court terme est confirmée ;
- Laine : réserve lorsque la demande de tricots est active ou très probable ;
- Melon/Fertilisant : éviter généralement de garder des stocks longs sous faible demande.

---

<a id="20-shed-overflow"></a>
# 20. Dépassement de la grange

Utilisez une projection indexée sur le temps.

Pour chaque événement de chute futur `d` :

```text
ProjectedShed(d) =
    current shed
    + all prior planned drops
    - all prior planned sells / uses / purchases from shed
```

Liquidation d'urgence requise :

```text
RequiredNeedSell = max(0, ProjectedShed(d) - 100)
```

Version de sécurité facultative à une seule case :

```text
SafetyNeedSell = max(0, ProjectedShed(d) - 99)
```

Ne pas ajouter de manière aveugle l'ensemble des stocks portés par les ouvriers : comptez uniquement les stocks attendus d'arriver à la grange avant l'événement de capacité pertinent.

---

<a id="21-selling-exact-marginal-simulation"></a>
# 21. Vente : simulation marginale exacte

L'équation historique de vente utilisant `P1/P3/P4/P5` est conservée uniquement comme intuition. Le moteur de vente de base énumère chaque quantité réalisable.

Pour chaque produit avec `stock` unités actuellement vendables :

```text
for q in 0 .. stock:
    simulate selling exactly q units
    compute the exact marginal revenue sequence
    propagate market inventory / price effects
    propagate enabled cash-dependent BUY / HIRE actions
    evaluate retained stock value

choose q with the highest resulting expected final value
```

`stock` ici signifie **le stock vendable non engagé après réserves opérationnelles, de production et de demande confirmée**, et non le stock brut de la grange.

Lorsque le comportement de l'adversaire est pertinent, passez les mêmes quantités de vente par les scénarios d'adversaire `LOW / BASE / HIGH`. Le classement de base utilise `BASE` ; les vérifications de robustesse `LOW/HIGH` ne comportent pas de poids de probabilité inventés.

Le revenu doit être calculé à partir du parcours marginal réel du prix, et non `q * initial_price`. Tous les ventes candidats restent soumis aux exigences du calendrier de 10 commandes par tick et à la liquidité.

---

<a id="22-sell-versus-hold"></a>
# 22. Vendre versus garder

Pour chaque unité suivante :

```text
MarginalSellValue(unit) = simulated cash received if this unit is sold now
```

Comparer contre :

```text
RetentionValue(unit) = max(
    FutureExpectedResaleValue,
    ProductionUseValue,
    SafetyStockValue
)
```

Vendre pendant que :

```text
MarginalSellValue > RetentionValue
```

Cependant, lorsque la vente actuelle débloque une action contrainte plus rentable, inclure explicitement cette valeur de liquidité.

---

<a id="23-liquidity-value-instead-of-arbitrary-financial-discounting"></a>
# 23. Valeur de liquidité au lieu d'un discount financier arbitraire

Ne pas se fier à la formule expérimentale :

```text
FuturePrice / (1 + r)^h
```

avec une `r` inférée sauf si elle est validée empiriquement.

Kaggriculture a une horizon fini court. Le principal coût d'un retard de paiement est la **meilleure action qui ne peut être financée pendant l'attente**.

Préférez :

```text
LiquidityOpportunityCost =
    Profit(best feasible plan with cash now)
    - Profit(best feasible plan without that cash until t+h)
```

Ensuite :

```text
FutureResaleValueAdjusted =
    ExpectedFutureSaleRevenue
    - LiquidityOpportunityCost
    - HoldingRisk
```

Une approximation bornée plus simple peut être utilisée si la comparaison exacte est trop coûteuse.

---

<a id="24-cash-urgency"></a>
# 24. Urgence en liquidité

Évitez les coefficients d'urgence non bornés ou négatifs.

```text
NearTermShortfall = max(
    0,
    RequiredCommittedSpendBeforeNextReliableIncome
    - LiquidCashAvailable
)

CashUrgency =
    NearTermShortfall
    / max(1, RequiredCommittedSpendBeforeNextReliableIncome)
```

Par conséquent :

```text
0 <= CashUrgency <= 1
```

Utilisez cela comme un bonus de liquidité dans l'évaluation de la vente, et non comme une raison indépendante pour vendre une grande quantité à un prix médiocre.

---

<a id="25-price-impact-and-opponent-timing"></a>
# 25. Impact de prix et timing de l'adversaire

Ne pas remplir automatiquement l'ensemble de la pénurie estimée du marché.

Évaluez l'unité de vente suivante selon son prix marginal.

Lorsque la disponibilité de l'adversaire est attendue prochainement :

- considérer la vente de unités rentables avant la maturité/la sortie de l'adversaire ;
- retenir des unités uniquement lorsque la récupération/la demande attendue justifie le délai ;
- éviter le dumping synchronisé de produits sensibles à une surproduction ;
- utiliser les actions observées de l'adversaire pour mettre à jour immédiatement la situation.

Le simulateur de marché exact doit remplacer des règles fixes comme « clarifier toujours avant la maturité de l'adversaire » dès lors que suffisamment d'information est disponible.

---

<a id="26-production-quantity"></a>
# 26. Quantité de production

Pour chaque produit candidat, augmenter la production **une unité incrémentale à la fois**.

```text
k = current_quantity + 1

while k is physically and operationally feasible:
    MV = marginal value of adding unit/tile/animal k

    if MV <= 0:
        stop

    accept k
    k += 1
```

Arrêter immédiatement lorsque l'un des deux cas suivants se produit :

- `MV <= 0`; ou
- une contrainte fixe empêche l'unité suivante : terre/temps de case, capacité du travailleur, argent, nourriture, stockage, délai, place sur le marché, ou la faisabilité de la sortie d'argent à la fin du jeu.

Ne sautez pas directement à une quantité de demande-inflation et n'inventez pas une capacité de production fixe sauf si une règle active l'explicitement définit.

---

<a id="27-wheat-as-an-operating-resource"></a>
# 27. Le blé comme ressource opérationnelle

Le blé a une valeur de vente et une valeur alimentaire.

Calculez une nécessité alimentaire datée :

```text
RequiredWheat(t0..t1) =
    feed actions required by accepted animal plan
    + safety reserve for survival risk
```

Soustrayez le blé déjà détenu et le blé qui mûrira avant chaque délai de livraison alimentaire.

Seulement le surplus de blé est librement vendable.

Comparez la production autonome à l'achat sur le marché en utilisant le même cadre de valeur marginale :

```text
cost of Wheat land + labor + delayed cash-out
vs
expected market purchase cost at feed date
```

Cela remplace une réserve fixe `5 * animal_q - next5day_maturity` lorsque la prévision datée est plus précise.

---

<a id="28-fertilizer"></a>
# 28. Fertilisant

Comme les engrais animaux ne s'accumulent pas, leur collecte n'est pas automatiquement valorisée.

Collecter uniquement lorsque l'un au moins des cas suivants est vrai :

- une tâche de fertilisation rentable en nécessite ;
- la valeur attendue de vente dépasse le coût d'organisation et de déplacement ;
- la collecte s'insère presque gratuitement dans une route existante ;
- ne pas collecter maintenant entraîne la perte d'une valeur significative qui ne peut pas être récupérée ultérieurement.

Fertiliser uniquement lorsque le bénéfice futur marginal en termes de rendement cashable ou d'avantage temporel dépasse les coûts de fertilisant, de main-d'œuvre, de déplacement et d'utilisation alternative.

---

<a id="29-product-specific-behavior-is-a-fallback-not-the-economy-engine"></a>
# 29. Le comportement spécifique à un produit est une option de secours, pas le moteur économique

Conserver les caractéristiques générales des produits comme hypothèses préalables :

- Blé : priorité à l'exploitation et au stock de nourriture ;
- Carotte : tour de rotation rapide et sensible à la rareté ;
- Tomate : production continue, sensible à la rareté ;
- Fraise : prix élevé mais très sensible à l'abondance ;
- Melon : valeur unitaire élevée mais très sensible à l'abondance ;
- Œuf : production fréquente d'animaux et relativement résistant à l'abondance ;
- Lait : valeur élevée, sensible à l'abondance ;
- Laine : valeur élevée, très sensible à l'abondance ;
- Fertilisant : utiliser ou vendre lorsque la collecte est rentable.

Les horaires fixes historiques et les formules de notation spécifiques aux produits ne doivent pas surcharger le modèle marginal partagé.

---

<a id="30-routing-logistics-and-hires"></a>
# 30. Itinéraires, logistique et embauches

Pour chaque `TaskGroup` non attribué, tester son insertion dans les itinéraires existants.

Le coût d'insertion inclut :

```text
travel
+ actions
+ pickup / resource acquisition
+ waiting
+ return / DROP
+ deadline risk
+ inventory effect
+ market dependency effect
```

Choisir l'insertion la plus économique possible.

Si des travaux importants et acceptés restent non attribués, testez un nouveau travailleur en utilisant la logique marginale exacte de recrutement.

Après avoir obtenu des itinéraires faisables, utilisez uniquement des mouvements locaux simples/échanges. N'introduisez pas un solveur global VRP complexe sauf si des preuves de benchmark le justifient.

---

<a id="31-resource-reservations"></a>
# 31. Réservations de ressources

Chaque tâche acceptée réserve les ressources nécessaires à l'heure concernée.

Exemples :

- semences ;
- alimentation en blé ;
- fertilisant ;
- animaux achetés ;
- capacité de grange ;
- place dans le marché ;
- temps de travail ;
- temps de tuile physique.

Une commande retardée ou échouée, un recrutement, une acquisition de terrain ou une vente invalide les réservations dépendantes et déclenche une réparation locale.

---

<a id="32-deployment-capacity-use-time-indexed-tile-reservations"></a>
# 32. Capacité de déploiement : utilisez des réservations de tuiles indexées par temps

Ne pas utiliser la contrainte historique statique :

```text
sum(seed_units) + animals <= currently_free_tiles
```

comme règle finale.

Au lieu de cela, valider l'occupation physique au fil du temps :

```text
for each placement interval [start, release):
    reserve exact tile
    reject overlapping incompatible reservations
```

Cela permet à la production d'utiliser des tuiles qui seront libérées avant le déploiement et empêche le métrique économique `effective land` d'être confondu avec l'occupation physique.

---

<a id="33-local-replanning"></a>
# 33. Réplanification locale

Réplantez uniquement lorsque le changement affecte la faisabilité, le signe de la valeur attendue ou l'action économique choisie.

Les changements pertinents incluent :

- nouvelle boutique ;
- mouvement significatif du prix ou de l'inventaire sur le marché ;
- plante, récolte, achat ou vente de l'adversaire ;
- herbe sauvage inattendue / animal échappé ;
- production différente de la prévision ;
- action de marché échouée ou retardée ;
- retard dans le trajet ;
- conflict entre stocks/cash ;
- confirmation de terrain ;
- dépassement de l'horizon de fin de jeu.

Conservez :

- faits confirmés ;
- actions complétées ;
- travailleurs payés ;
- préfixes de trajets toujours valides ;
- réservations toujours valides.

Libérez uniquement les réservations futures et les suffixes de trajets affectés.

---

<a id="34-endgame"></a>
# 34. Fin de jeu

La fin de jeu est évaluée à chaque nouvelle décision, et non seulement lors d'une passe de nettoyage.

Une nouvelle culture, acquisition d'animaux, achat de terrain, utilisation de fertilisant ou recrutement est rejetée si la chaîne complète :

```text
install
-> maintain
-> produce
-> harvest
-> return
-> DROP
-> SELL
```

ne peut pas créer un cash réalisable positif avant la dernière vente exécutable.

Planifiez en sens inverse à partir de la dernière vente :

```text
last SELL
<- required DROP
<- required return travel
<- required HARVEST
<- required maintenance / production
```

Si l'environnement configuré utilise le calendrier connu `episodeSteps = 720`, conservez un test de régression explicite selon lequel la liquidation finale est terminée à l'heure de la dernière exécution réelle (convention du projet actuelle : jour 29, heure 22).

Ne faites jamais confiance à un dépôt automatique après la fin du jeu.

---

<a id="35-fixed-opening-strategy"></a>
# 35. Stratégie d'ouverture fixe

La base utilise le paquet d'ouverture fixe ci-dessous. Il est **ACTIVÉ par défaut** et n'est pas simplement une semence de référence.

Quantités cibles d'ouverture :

|Article|Quantité|
| --- | ---: |
|Culture de blé| 10 |
|Carotte| 6 |
|Tomate| 1 |
|Fraise| 2 |
|Melon| 2 |
|Gosse| 1 |
|Vache| 2 |
|Mouton| 1 |
|Stock de blé| 16 |
|Embauches initiales de travailleurs agricoles| 4 |

Règles d'ouverture :

- créer/placer/planter le paquet cible au plus tôt selon les mécaniques et la capacité d'action ;
- l'arrosage obligatoire du jour même pour les cultures récemment plantées reste incontournable ;
- les animaux obéissent au masque de placement triangulaire obligatoire centré ;
- les cultures à long terme ne peuvent pas occuper le centre `2 x 2` ;
- acquérir et réserver suffisamment de blé pour soutenir le paquet animal fixe ;
- ne pas remplacer les quantités fixes par des quantités marginales lors de la construction initiale ;
- une fois que le paquet d'ouverture est établi, les plans partagés normaux et les plans marginaux prennent le relais pour la production supplémentaire.

Utiliser les prix/coûts observés réellement et l'état du jeu lors de l'exécution. Les coûts historiques enregistrés ne sont pas considérés comme des constantes mécaniques.

---

<a id="36-objective"></a>
# 36. Objectif

L'objectif du jeu est le montant final du compte bancaire.

Par conséquent, l'objectif principal du planificateur doit rester :

```text
maximize expected final realizable cash
```

L'analyse de l'adversaire est utile car l'adversaire modifie les prix et la victoire dépend du résultat final relatif, mais ne pas remplacer la valeur absolue par une heuristique historique :

```text
MarginMax = OurProfit - OpponentProfit
```

sauf si une politique concurrentielle distincte est explicitement benchmarkée.

Les décisions de production et d'exploitation principales ne doivent pas détruire notre propre espérance de liquidités simplement pour réduire une estimation de profit de l'adversaire.

---

<a id="37-historical-ideas-retained-only-for-benchmark"></a>
# 37. Idées historiques conservées uniquement pour benchmark

Les éléments suivants restent **désactivés par défaut** et ne doivent pas influencer l'agent de base sauf si un benchmark isolé les active explicitement :

- journées de saut fixées comme `T5` ou `T5-T7` ;
- dates fixes de fertilisation / de récolte comme `T8`, `T10`, `T12`, `T14`, `T16` ;
- formules historiques de score produit avec parenthèses ambiguës ;
- formules historiques `Dtotal` avec abréviations non définies ou répétées ;
- `Va * required_actions` comme coût du travail ;
- le taux de discount financier inféré `r` ;
- la production brute de l'exploitation ajoutée directement à l'inventaire du marché global ;
- l'inégalité de vente par tranches `P1/P3/P4/P5` comme moteur de vente finale ;
- `NeedSell = Shed + Carry + Incoming - 99` comme équation exacte de stockage ;
- capacité de déploiement statique `seeds + animals <= free tiles` ;
- changement de stratégie rigide `T0-T3 / T4-T20 / T20-T30`.

Les éléments suivants sont **plus que simplement réservés pour benchmark** et sont des règles de base actives :

- limite de travailleurs `14` ;
- paquet d'ouverture fixe ;
- achats de terres planifiés `T4/T7/T9/T12` avec la branche de magasin définie dans §16-17 ;
- ordre d'expansion fixe `NE -> SW -> SE` ;
- disposition triangulaire obligatoire symétrique `5 x 5` des animaux ;
- interdiction absolue du centre `2 x 2` pour les cultures à long terme.


<a id="371-historical-alternative-opening"></a>
### 37.1 Alternative d'ouverture historique

Les quantités suivantes pour le jour 1 ont été enregistrées comme autre ouverture candidate et ne restent disponibles que pour une comparaison isolée de benchmark :

|Produit|Quantité candidate jour 1 historique|
| --- | ---: |
|Melon| 2 |
|Carotte| 6 |
|Production d'œufs| 1 |
|Production de laine| 1 |
|Production laitière| 2 |
|Fraise| 2 |
|Blé| 2 |
|Tomate| 2 |

Ils ne surchargent pas l'ouverture active fixe prévue à §35.

<a id="372-historical-phase-boundaries"></a>
### 37.2 Limites historiques des phases

Les phases descriptives fixes sont conservées comme prémisses historiques :

```text
T0-T3   -> opening
T4-T20  -> expansion / adaptation
T20-T30 -> liquidation-oriented play
```

Le planificateur actif utilise les régimes déclenchés par des événements à §18 au lieu de considérer ces limites comme des commutateurs rigides.

<a id="373-historical-expansion-timing-and-fill-patterns"></a>
### 37.3 Horlogerie historique des expansions et des schémas de remplissage

Des notes anciennes ont enregistré une limite temporelle :

```text
first land  < T7
second land < T12
third land  < T12
```

Ils ont également proposé des schémas de remplissage de nouvelles terres :

- SW : triangle `4 x 4`, carré `4 x 4`, ou remplissage partiel conditionnel ;
- SE : triangle `4 x 4`, sous-ensemble proche du centre `4 x 4`, ou remplissage partiel conditionnel.

Ces éléments restent uniquement de référence. Le calendrier actif d'expansion et la géométrie sont définis à §15-17.

<a id="374-historical-effective-land-weight"></a>
### 37.4 Poids historique des terres efficaces

L'ancienne comparaison économique utilisait :

```text
plant effective land   = 1 tile
poultry effective land = 5 / 3 tiles
```

Cela peut être utilisé comme un poids de comparaison économique, mais il ne doit jamais remplacer les réservations physiques exactes des tuiles au temps prévues à §32.

<a id="375-historical-opponent-and-demand-approximations"></a>
### 37.5 Approximations historiques de l'adversaire et de la demande

Le modèle d'adversaire ancien proposait :

```text
OpponentExpectedSupply = VisibleCapacity * ExpectedExecutionRate
```

et confiance en la demande :

```text
ConfirmedDemandWeight = 1
FutureExpectedDemandWeight < 1
```

La base finale conserve les scénarios d'adversaire `LOW / BASE / HIGH` sans inventer de poids de probabilité. Ces formules sont conservées uniquement comme des approximations expérimentales possibles.

<a id="376-historical-long-horizon-market-approximation"></a>
### 37.6 Approximation historique du marché à long terme

Lorsque la projection événement par événement était jugée trop coûteuse, les notes proposaient :

```text
FutureInventory(h) =
    CurrentMarketInventory
    + h * (
        OwnAverageDailySupply
        + OpponentAverageDailySupply
        - ShopAverageDailyConsumption
      )
```

Cette approximation est uniquement de référence. Le modèle actif maintient la production au niveau du fermier séparée de l'inventaire global du marché et préfère le chemin d'inventaire daté à §4.

<a id="377-historical-product-score-formulas"></a>
### 37.7 Formules historiques des scores produits

Les idées de score suivantes sont conservées exactement comme des notes stratégiques. Leur parenthésage initial n'était pas entièrement spécifié, donc elles ne doivent pas devenir silencieusement des formules de base.

|Produit|Idée de score historique|
| --- | --- |
|Melon| `sum(q * dynamic_price) - 80 - fertilizer - labor / land_occupation` |
|Carotte| `sum(q * dynamic_price) - 20 - labor / land_occupation` |
|Œuf| `sum(q * dynamic_price) - 300 - labor * 1.6 / land_occupation` |
|Laine| `sum(q * dynamic_price) - 500 - labor * 1.6 / land_occupation` |
|Lait| `sum(q * dynamic_price) - 400 - labor * 1.6 / land_occupation` |
|Fraise| `sum(q * dynamic_price) - 100 - labor / land_occupation` |
|Blé| `sum(q * dynamic_price) - 10 - labor / land_occupation` |
|Tomate| `sum(q * dynamic_price) - 50 - labor / land_occupation` |

<a id="378-historical-demand-formulas"></a>
### 37.8 Formules historiques de la demande

Les abréviations initiales n'étaient pas entièrement définies. Les termes répétés sont intentionnellement conservés plutôt que corrigés silencieusement.

|Produit|Formule historique `Dtotal`|
| --- | --- |
|Melon| `Dtotal = 1/day` |
|Carotte| `Dtotal = Dm + 12 * Npc * q + 6 * Nfm * q` |
|Œuf| `Dtotal = Dm + 6 * Nb * q + 6 * Nbs * q` |
|Laine| `Dtotal = Dm + 12 * Ny * q` |
|Lait| `Dtotal = Dm + 6 * Np * q + 6 * Ni * q + 6 * Ns * q` |
|Fraise| `Dtotal = Dm + 6 * Nb * q + 6 * Nic * q + 6 * Ns * q + 6 * Nfm * q + 6 * Ns * q` |
|Blé| `Dtotal = Dm + 6 * Ni * q + 6 * Nb * q + 6 * Ns * q + 6 * Nfm * q + 6 * Nb * q` |
|Tomate| `Dtotal = Dm + 6 * Np * q + 6 * Nfm * q` |

<a id="379-historical-competitive-margin-signal"></a>
### 37.9 Signal historique de marge concurrentielle

Les notes proposaient :

```text
MarginMax = OurProfit - OpponentProfit
```

Il peut être utilisé comme un signal secondaire, mais §36 conserve le montant final attendu réalisable en espèces comme objectif de base.

<a id="3710-historical-financial-discounting"></a>
### 37.10 Discounting financier historique

Le modèle ancien de vente/tenue proposait :

```text
FutureResaleValue(h) = E[P(t + h)] / (1 + r)^h

r =
    ((CapitalPrepared + ExtraNetBenefit) / CapitalPrepared)^(1 / h)
    - 1
```

La spécification exacte de l'agrégation de l'horizon n'était pas entièrement définie. La base finale utilise donc le modèle de coût de liquidité-opportunité du §23, sauf si une expérience de taux de discount est explicitement activée.

<a id="3711-historical-split-sale-comparison"></a>
### 37.11 Comparaison historique de ventes fractionnées

Les notes tactiques plus anciennes comparaient la vente immédiate de `n + m` avec la division de la vente :

```text
P  = average price
n  = quantity sold now
P1 = current price
D  = shop consumption
m  = later quantity we may sell before opponent maturity
x  = opponent quantity sold one day before our later sale
P3 = opponent sale price before our later sale
P4 = our resulting price after that opponent sale
P5 = opponent's later price after our n + m sales and before our next maturity
```

Condition historique de vente fractionnée :

```text
(n + m) * P1 - x * P5
<
n * P1 + m * P4 - x * P3
```

Cela reste matière d'intuition ou de benchmark. L'engine de vente actif du §21 énumère directement les quantités réalisables.

<a id="3712-historical-overflow-and-deployment-shortcuts"></a>
### 37.12 Raccourcis historiques de surcharge et de déploiement

Les notes anciennes utilisaient :

```text
NeedSell = Shed + Carry + Incoming - 99
```

et :

```text
sum(seed_units_to_deploy) + number_of_animals_to_place
<= available_free_tiles
```

Ils sont conservés uniquement comme raccourcis pour des expériences. Le planificateur actif utilise la capacité réelle de décharge `100`, l'inventaire entrant indexé dans le temps et les réservations exactes par case-temporelle.

<a id="3713-historical-animal-action-ordering"></a>
### 37.13 Ordre historique des actions animales

La séquence ancienne des visites productives était :

```text
FEED
-> HARVEST
-> CARE
-> COLLECT_FERTILIZER
```

La base finale ne l'implique pas universellement. Le §12 conserve uniquement les dépendances pertinentes pour l'état actuel.

<a id="3714-historical-product-level-inventory-and-timing-heuristics"></a>
### 37.14 Heuristiques historiques d'inventaire et de timing au niveau du produit

Les règles suivantes restent disponibles comme prérequis de benchmark, et non comme surcharges de base :

- Fertilisant : préférer la vente immédiate lorsque ce n'est pas nécessaire pour une fertilisation rentable à court terme.
- Melon : éviter de le garder longtemps ; une note ancienne a limité la production combinée autour de `120`.
- Blé : estimation ancienne de réserve `5 * animal_q - WheatExpectedToMatureInNext5Days`.
- Œuf : avec la demande de Boulangerie/Repas du matin, garder environ une journée de demande ; la politique ancienne utilisait un jour de `CARE`.
- Carotte : avec la demande de PetCafe/Marché des fermiers, garder environ deux jours de demande ; la règle ancienne ne prévoyait pas de fertilisation.
- Tomate : idée historique de fertilisation/harvest autour de `T8`, `T9` et `T11`.
- Fraise : idée historique de fertilisation/harvest autour de `T10`, `T12`, `T14` et `T16`.
- Lait : avec une demande pertinente, garder environ deux jours de demande nette ; le calendrier ancien CARE a été sauté autour de `T5-T7`.
- Laine : garder en attente de la demande de laine ; le calendrier ancien CARE a été sauté autour de `T5`.

Les classes d'inventaire historiques associées étaient :

```text
Class 1 — operating inventory only: Wheat
Class 2 — fast turnover: Carrot
Class 3 — balanced: Tomato, Egg
Class 4 — high-value timing inventory: Strawberry, Milk, Wool
Class 5 — avoid long holding: Melon, Fertilizer
```

Le planificateur actif dérive au contraire les réservations à partir de la prévision datée et utilise uniquement les caractéristiques générales des produits du §29 comme prérequis de secours.

<a id="3715-historical-market-aware-sale-biases"></a>
### 37.15 Biais historiques de ventes sensibles au marché

Lorsque le simulateur marginal complet est désactivé pour un benchmark isolé, les notes anciennes suggéraient :

- Carotte / Œuf / Blé / Tomate : vendre plus tôt sous pression de liquidité ;
- Laine : attendre la demande de laine si plausible ;
- Lait / Fraise : préférer les fenêtres à prix élevé ;
- Melon : vendre immédiatement ou avant la fourniture attendue de l'adversaire ;
- sous pression de décharge : vendre dans l'ordre de priorité de profit plutôt que FIFO.

Ces règles ne doivent pas surcharger les logiques de vente/tenue et de quantité de base du §21-25.


---

<a id="38-final-hard--near-hard-invariants"></a>
# 38. Invariants rigides / presque rigides finaux

1. Ne jamais violer une limite réelle du mécanisme de jeu.
2. Ne jamais dépasser la limite de capacité du travailleur stratégique actif de `14`.
3. Ne jamais laisser une culture nouvellement plantée sans eau requise pour la même journée.
4. N'oubliez jamais les maintenances de survie pour un bien dont le plan accepté vise à le conserver.
5. N'effectuez jamais de maintenance sur un bien dont le meilleur plan restant est l'abandon.
6. N'organisez jamais un travail sans les ressources et dépendances nécessaires.
7. N'autorisez jamais une chute requise à dépasser la capacité réelle de la grange `100`.
8. Ne soumettez jamais plus de 10 ordres de marché en une seule étape.
9. N'assumez jamais que des terres en attente soient déjà débloquées.
10. N'incluez jamais la production agricole non vendue dans l'inventaire du marché global.
11. N'placez jamais des animaux en dehors de la masque triangulaire centré de la zone active `1`.
12. N'installez jamais un cultiveur à long terme au centre `2 x 2`.
13. Conservez les compteurs d'ouverture fixes pendant la construction d'ouverture, sauf si les mécanismes rendent une action demandée temporairement impossible.
14. Conservez la promesse de terrain : `T4 NE` ; puis à `T7`, branche de demande animale -> `T7 SW` + `T12 SE`, sinon `T9 SW` et aucune obligation de `T12 SE`.
15. Un achat de terrain planifié peut être reporté en raison d'échecs mécaniques ou de seuil de liquidités, mais ne doit pas être silencieusement abandonné.
16. N'acceptez jamais un embauche non obligatoire simplement parce qu'un travail existe ; exigez une valeur marginale positive et un nombre de travailleurs `< 14` avant l'embauche.
17. N'acceptez jamais un achat de terrain non planifié simplement parce que le champ est plein ; exigez une augmentation de liquidités positive par rapport au plan sans terrain.
18. N'acceptez jamais un nouvel investissement non obligatoire qui ne peut pas terminer sa chaîne de liquidités totale avant la fin du jeu.
19. N'arrêtez jamais de manière silencieuse une dépendance en raison de pression sur les places de marché.
20. N'ajoutez jamais de groupes de tâches ou de réservations après un plan sans changement.
21. Conservez les travaux et réparations valides et engagés, uniquement pour les suffixes futurs affectés.

---

<a id="39-verification-suite-for-the-final-design"></a>
# 39. Ensemble de vérification pour la conception finale

Toute implémentation affirmant suivre la stratégie finale ne doit pas être considérée comme fidèle avant que ces cas ne soient passés.

<a id="mechanics"></a>
## Mécanismes

- culture nouvellement plantée sans eau de même jour -> planificateur rejette le trajet ;
- animal conservé à la date limite de survie -> FEED est planifié ;
- animal abandonné ou peu rentable en retard -> le FEED de survie peut être intentionnellement omis ;
- grange à 95 avec une chute entrante de 10 -> au moins 5 unités de capacité doivent être libérées avant la chute ;
- mode de sécurité pour ce cas -> libérer 6 unités pour atteindre 99 ;
- les semences ne comptent pas dans la capacité de la grange ;
- le calendrier du marché ne génère jamais plus de 10 ordres en une seule étape.

<a id="market-model"></a>
## Modèle du marché

- récolte de ferme sans vente -> inventaire du marché global inchangé ;
- notre vente -> inventaire global augmente et le prix marginal de la prochaine vente est recalculé ;
- notre achat -> inventaire global diminue ;
- consommation au magasin -> inventaire global diminue ;
- scénario de vente simultanée entre deux joueurs -> le revenu utilise les prix marginaux séquentiels / intercalés de l'environnement, et non `quantity * initial_price` ;
- les scénarios d'adversaires LOW/BASE/HIGH peuvent modifier la quantité de vente sans compromettre la faisabilité.

<a id="labor"></a>
## Main-d'œuvre

- nouveau travailleur qui exécute uniquement des travaux à valeur négative -> aucune EMPLOI ;
- un nouveau travailleur qui sauve une tâche critique de délais rentable et couvre le coût de recrutement -> HIRE ;
- un 15e travailleur est rejeté par la capacité stratégique active même s'il présente une valeur marginale positive isolée.

<a id="land"></a>
## Terres

- tout champ actuel mais aucune production supplémentaire de valeur positive -> pas de BUY_LAND ;
- production rentable avec un entretien impossible -> pas de BUY_LAND ;
- expansion rentable qui contrevient à la réserve de liquidités opérationnelles -> pas de BUY_LAND ;
- terre confirmée avec un cultive réservé devenu mauvais -> annuler le cultive malgré le coût déjà engagé ;
- `T4 -> NE` est programmé indépendamment de la demande des ateliers ;
- à `T7`, la demande animale dans les deux premiers ateliers programme `SW` immédiatement et `SE` à `T12` ;
- à `T7`, aucune demande animale ne programme `SW` à `T9` et ne force pas `SE` à `T12` ;
- un achat programmé qui échoue à la limite de liquidités est reporté/pendant plutôt que supprimé sans alerte ;
- la direction d'expansion n'est jamais permutée en dehors de `NE -> SW -> SE`.

<a id="opening-and-placement"></a>
## Ouverture et placement

- les cibles fixes d'ouverture sont exactement conformes à §35 ;
- le planificateur d'ouverture ne remplace pas les quantités préférées marginales avant la construction du paquet fixe ;
- les masques triangulaires NW/NE/SW/SE sont des symétries exactes du modèle spécifié `5 x 5` ;
- le placement d'animal en dehors d'une cellule `1` est rejeté ;
- le placement à long terme d'une culture à l'intérieur de `CENTRAL_2X2` est rejeté.

<a id="inventory"></a>
## Inventaire

- seulement les stocks programmés pour atteindre le bâtiment avant une chute ciblée contribuent à cet événement de capacité ;
- le blé requis avant les délais futurs de nourriture ne peut être vendu comme stock non engagé ;
- les réserves de demande future des ateliers influencent la valeur de vente/tenue ;
- la pression de stock peut forcer une vente même si l'attente a un prix unitaire supérieur en dehors de contexte.

<a id="endgame"></a>
## Fin de partie

- investissement dont la première vente réalisable se produit après la fin du jeu -> rejeté ;
- récolte animale qui doit être vendue le jour final -> récoltée assez tôt pour garantir le retour/la chute/la vente ;
- aucun travailleur final ne porte un inventaire valorisable non vendu ;
- aucune décision de planificateur ne suppose une liquidation automatique post-jeu.

<a id="replanning"></a>
## Réplanification

- génération répétée avec état inchangé -> identiques IDs de tâche, pas de doublons ;
- l'annulation d'un HIRE invalide uniquement la capacité future dépendante ;
- l'échec d'un BUY invalide les tâches de collecte/planification dépendantes ;
- un nouveau magasin recalculer les demandes, les prix, les réserves et les quantités de production affectées ;
- un mouvement de prix sans lien n'actualise pas les itinéraires non affectés.

---

<a id="40-benchmark-protocol-for-uncertain-heuristics"></a>
# 40. Protocole de référence pour des heuristiques incertains

Pour chaque heuristique optionnelle, comparer avec la même base finale utilisant des semences paires et la même politique adverse.

Enregistrer au moins :

```text
mean final money
median final money
minimum final money
win rate / money difference if relevant to the evaluation setup
mean hires per day
land purchase timing
idle worker ticks
missed critical tasks
shed overflow incidents
market-order truncation incidents
unrealized final inventory
runtime
```

Promouvoir une heuristique expérimentale uniquement lorsque :

```text
1. it improves the chosen primary metric,
2. it does not introduce a clear tail-risk regression,
3. the gain survives more than a tiny seed sample,
4. the implementation does not duplicate an existing planner mechanism.
```

---

<a id="41-final-strategy-summary"></a>
# 41. Résumé de la stratégie finale

Le planificateur final doit se comporter comme suit :

```text
1. Execute the fixed opening package.
2. Observe the real game state and maintain one forecast through game end.
3. Keep farm inventory and global market inventory separate.
4. Model opponent supply with LOW / BASE / HIGH scenarios without arbitrary weights.
5. Enforce MAX_WORKERS = 14.
6. Enforce the center-facing 5x5 triangular animal masks and central 2x2 long-crop ban.
7. Follow the active land schedule:
       T4 -> NE
       at T7: animal-demand branch -> SW T7 + SE T12
              no-animal-demand branch -> SW T9, no mandatory SE T12
8. Generate non-mandatory production one unit at a time until MV <= 0 or a constraint binds.
9. Reserve exact tile-time, stock, cash, market slots and worker-time.
10. Protect valuable assets; abandon negative-value sunk assets.
11. Route existing workers first; hire only on positive marginal schedule delta and below cap 14.
12. Enumerate sale quantities q = 0..sellable_stock with the exact market simulator.
13. Use the deterministic tie-break: value -> smallest slack -> less labor -> less travel.
14. Replan locally when observations materially change feasibility or value.
15. Plan final harvest/drop/sale backward so value becomes cash before game end.
```

Le principe fondamental est :

> **Les mécaniques définissent ce qui est possible ; la stratégie active définit la base engagée ; la faisabilité définit ce qui peut être exécuté ; l'optimisation du cash final marginal améliore tout ce qui reste facultatif.**


---

<a id="42-version-to-final-traceability"></a>
# 42. Tracabilité version à résultat final

Les documents historiques sur l'idée sont maintenant une lignée stricte, tandis que ce fichier est le résultat complet et autonome :

|Version de conception|Agent associé|Contribution principale intégrée dans cette conception finale|
| --- | --- | --- |
| [`v1`](heuristic_ideas_v1.fr.md) | `chi12.py` |Planification quotidienne, priorités, logistique, routage, protection du stock, réplanification locale, liquidation|
| [`v2`](heuristic_ideas_v2.fr.md) | `chi13.py` |Expansion explicite du territoire, base sans territoire, confirmation et gestion des dépendances|
| [`v3`](heuristic_ideas_v3.fr.md) | `chi14.py` |Prévision partagée, stabilité de `TaskGroup`, routage intégré/HIRE, un calendrier de marché, réparation locale, intégration de la fin de jeu|
| [`v4`](heuristic_ideas_v4.fr.md) |—|Économie consciente du marché/du concurrent, production/vente marginale, contraintes en main-d'œuvre et espace, priorités tactiques|
| `final` |—|Stratégie complètement résolue, hiérarchisation active vs benchmark, modèle de marché corrigé et contrat d'implémentation|

La stratégie finale est spécifiée de telle manière qu'une implémentation pourrait être dérivée uniquement à partir de ce fichier ; les documents versionnés restent utiles pour l'histoire de conception et l'attribution des modifications. Aucun tel successeur validé n'est conservé dans le projet fermé.


<a id="43-implementation-contract"></a>
# 43. Contrat d'implémentation

Cette section élimine la liberté d'implémentation qui pourrait autrement conduire à deux agents à revendiquer la même stratégie tout en se comportant différemment.

<a id="431-active-vs-benchmark-only-rules"></a>
## 43.1 Règles active vs uniquement benchmark

Toutes les règles explicitement marquées comme active dans ce document sont activées par défaut.

Les règles historiques ou uniquement benchmark sont désactivées par défaut et ne doivent pas influencer la base sauf si une expérience les active explicitement.

Les règles actives incluent, au minimum :

```text
MAX_WORKERS = 14
fixed opening package from §35
fixed expansion order = NE -> SW -> SE
active land schedule from §16-17
mandatory 5x5 triangular animal masks
absolute central 2x2 long-term-crop exclusion
```

<a id="432-storage"></a>
## 43.2 Stockage

```text
SHED_CAPACITY = 100
```

Utiliser `100` pour les vérifications de faisabilité et les dépassements.

`99` est uniquement une cible de sécurité optionnelle et ne doit pas être traitée comme la capacité du moteur. La base peut exposer un indicateur de configuration pour cette marge ; aucune règle ne doit l'exiger pour prouver la faisabilité de base.

<a id="433-forecast-horizon"></a>
## 43.3 Horizon de prévision

La prévision physique/économique s'étend du tick actuel à la fin du jeu. Des approximations courtes conservées peuvent être utilisées internes uniquement si elles garantissent la préservation des mêmes décisions pour la portée concernée.

<a id="434-marginal-production-search"></a>
## 43.4 Recherche de production marginale

Pour la production non obligatoire, tester exactement une unité, un carreau ou un animal de plus à la fois et arrêter lorsque :

```text
MV <= 0
OR a binding constraint prevents the next unit
```

Ne pas sauter directement à une quantité ciblée supposée.

<a id="435-sale-quantity-search"></a>
## 43.5 Recherche de quantité de vente

Pour chaque produit, après réservations :

```text
sellable_stock = uncommitted stock
for q in 0 .. sellable_stock:
    simulate q exactly
choose q maximizing expected final value
```

Ne pas utiliser une taille de lot fixe comme règle de décision de base.

<a id="436-deterministic-tie-break"></a>
## 43.6 Résolution déterministe des égalités

Quand deux choix faisables sont égaux selon l'objectif principal, appliquer :

```text
1. higher value
2. smaller deadline slack
3. fewer labor / worker ticks
4. less travel
5. stable deterministic ID / coordinate order
```

`smaller slack` signifie que la tâche plus urgente parmi les faisables gagne.

<a id="437-no-arbitrary-economic-coefficients"></a>
## 43.7 Aucun coefficient économique arbitraire

Ne pas inventer des constantes non expliquées pour :

- `RiskPenalty`;
- les probabilités LOW/BASE/HIGH ;
- les poids de placement ;
- les taux de discount de liquidité ;
- multiplicateurs de valeur stratégique.

Conventions de base :

- classer les résultats attendus selon la situation de l'adversaire `BASE`;
- utiliser le `LOW/HIGH` uniquement comme vérifications de robustesse/sensibilité, sauf si des probabilités sont ultérieurement configurées;
- utiliser la géométrie de placement rigide ainsi que le critère de rupture déterministe au lieu de la notation de placement pondérée;
- utiliser les écarts directs de calendrier/du cash au lieu d'un coefficient de désavantage financier inventé.

Si un coefficient numérique reste inévitables, le rendre une valeur de configuration nommée et le marquer comme **non spécifié par la stratégie**. Il ne doit pas devenir silencieusement une partie de la base.

<a id="438-mechanical-execution-contract"></a>
## 43.8 Contrat d'exécution mécanique

Le code stratégique doit lire les sémantiques d'exécution exactes des règles du jeu / de l'environnement plutôt que de les inventer. En particulier, vérifier dans les tests :

- la disponibilité exacte des travailleurs après `HIRE`;
- la position exacte de spawn des travailleurs;
- la quantité exacte de `PICKUP` après soustraction de ce qui est déjà transporté;
- le traitement exact des ordres de marché / l'interlèvement;
- le moment exact de consommation des boutiques;
- le moment exact de production/actualisation quotidienne;
- le dernier tick effectivement exécutable.

Ces éléments sont des mécanismes, pas des paramètres de stratégie.

<a id="439-traceability-requirement"></a>
## 43.9 Exigence de traçabilité

Chaque branche stratégique dans toute implémentation revendiquant ce design final doit être traçable à une section de ce document. Si un comportement ne peut être justifié par ce fichier ou par un mécanisme de jeu vérifié, le Codex ne doit pas l'ajouter silencieusement.


---

<a id="navigation"></a>
## Navigation

[← Design précédent](heuristic_ideas_v4.fr.md) · Design consolidé final
