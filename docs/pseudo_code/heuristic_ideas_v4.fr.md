[English](heuristic_ideas_v4.md) | [Français](heuristic_ideas_v4.fr.md) | [简体中文](heuristic_ideas_v4.zh-CN.md)

[README du projet](../../README.fr.md)

<a id="heuristic-ideas-v4--market-aware-tactical-strategy"></a>
# Idées heuristiques v4 — Stratégie tactique consciente du marché

[← Version précédente](heuristic_ideas_v3.fr.md) · [Version finale consolidée →](heuristic_ideas_final.fr.md)

> **Convention de série**
>
> `v4` est une **différence stricte par rapport à `v3`**. Elle hérite de `v3` intégralement et ajoute, remplace ou corrige uniquement des règles explicitement documentées ici. Le comportement antérieur est hérité transitivement via `v3` ; `v4` ne considère pas `v1` ni `v2` comme des parents parallèles.

<a id="identity"></a>
## Identité

|Champ|Valeur|
| --- | --- |
|Version| `v4` |
|Source|Feuilles de stratégie Kaggriculture + notes tactiques supplémentaires|
|Agent associé|Aucun — conception uniquement|
|Rôle|Différence stricte par rapport à [`v3`](heuristic_ideas_v3.fr.md)|
|Améliore| [`v3`](heuristic_ideas_v3.fr.md) |
|Consolidé par| [`final`](heuristic_ideas_final.fr.md) |
|Principale attention|Temps de marché, modélisation de l'adversaire, économie marginale, politique d'inventaire, utilisation tactique des terres et contraintes opérationnelles rigides|
|Statut d'implémentation|Pas implémenté comme agent CHI dédié|

<a id="inheritance-rule"></a>
## Règle d'héritage

`v4` hérite intégralement de [`v3`](heuristic_ideas_v3.fr.md). Puisque `v3` hérite déjà de `v2` (et donc de `v1`), tout comportement antérieur reste hérité transitivement. Seules les règles énoncées ci-dessous modifient la conception `v3`.

Ce fichier ne répète intentionnellement pas les idées déjà présentes dans `v3`, y compris les comportements hérités transitivement par `v3`. Le plan quotidien de tâches, les priorités de survie, la gestion des itinéraires/logistiques, la planification de `BUY_LAND`, la prévision partagée, la réplanification locale, le calendrier de marché validé et la faisabilité générale de la fin de partie restent donc hérités de `v3`.

Les règles ci-dessous sont les idées tirées des notes ultérieures de Kaggriculture qui ajoutent de nouvelles informations ou rendent un principe antérieur plus précis.

---

<a id="main-idea"></a>
## Idée principale

Ajouter une deuxième couche stratégique au-dessus du planificateur unifié :

`shop demand -> own/opponent supply -> future inventory -> future price -> marginal value -> what to produce / hold / sell`

Le planificateur ne devrait plus se demander uniquement si un plan de production est faisible. Il doit aussi se demander si la **prochaine unité**, **la prochaine case**, **le prochain ouvrier**, **l'achat de la prochaine terre** ou **la vente de la prochaine unité** améliore le bénéfice attendu après l'impact du marché, en tenant compte de la valeur de conservation, du coût de l'emploi du travail et du timing de l'adversaire.

---

<a id="1-hard-labor-ceiling--marginal-hiring"></a>
## 1. Contrainte de travail rigide + embauche marginale

<a id="hard-constraint"></a>
### Contrainte rigide

```text
worker_count <= 14
```

Le planificateur ne doit jamais créer un plan exigeant plus de 14 ouvriers.

<a id="economic-stopping-rule"></a>
### Règle d'arrêt économique

Ne pas embaucher uniquement parce qu'il existe plus de travail. Comparer la valeur ajoutée générée par un autre ouvrier avec le coût de l'embauche suivante.

```text
Va = Profit(A + 1 workers) - Profit(A workers)
```

Arrêter l'embauche lorsque l'ouvrier marginal ne rapporte plus lui-même.

Si un nouvel ouvrier n'est pas rentable par rapport à son coût, réaffecter le travail existant vers les terres ou productions les plus valorisées au lieu d'agrandir l'effectif.

Les notes sources décrivent également le coût d'opportunité du travail comme :

```text
LaborOpportunityCost_i = Va * required_actions_i
```

Ceci est plus précis que la règle v3 selon laquelle un `HIRE` doit simplement rendre le travail faisible.

---

<a id="2-spatial-layout-constraints"></a>
## 2. Contraintes de disposition spatiale

Utiliser des zones de placement explicites en plus de la logique de placement héritée de `v3`.

<a id="animal-zone"></a>
### Zone animale

Les animaux doivent être concentrés dans une zone triangulaire de taille approximative `5 x 5` proche de l'aire centrale de la ferme / zone d'accès au bâtiment.

Objectif :

- réduire les déplacements répétés de `FEED`, `CARE`, `HARVEST` et de collecte de fertilisant ;
- conserver une production fréquente au centre ;
- éviter de disperser les soins aux animaux sur une surface agrandie.

<a id="central-2-x-2-reserve"></a>
### Réservé central `2 x 2`

Éviter d'utiliser la zone centrale `2 x 2` pour des cultures à long terme.

La note originale précise que cette restriction cesse d'appliquer après le seuil de remboursement pertinent. Cela constitue donc une **restriction de placement dépendante du temps**, et non une interdiction permanente.

<a id="effective-land-usage"></a>
### Utilisation efficace des terres

Pour une comparaison économique, les notes utilisent :

```text
plant effective land = 1 tile
poultry effective land = 5 / 3 tiles
```

Cette occupation effective peut être utilisée lors de la comparaison de la valeur marginale par unité de temps-terre.

---

<a id="3-three-strategic-game-phases"></a>
## 3. Trois phases stratégiques du jeu

Les notes divisent le jeu en trois phases générales :

```text
Phase 1: T0  -> T3
Phase 2: T4  -> T20
Phase 3: T20 -> T30
```

Les décisions exactes restent dépendantes de l'état, mais les rôles prévus sont :

- **T0–T3 :** établir une base de production initiale et une capacité de survie/alimentation ;
- **T4–T20 :** s'agrandir, réagir aux demandes révélées des boutiques et maximiser l'utilisation des terres productives ;
- **T20–T30 :** réduire les engagements à long terme, gérer l'inventaire de manière agressive et se préparer à la liquidation.

Ce modèle de phase constitue un biais tactique supplémentaire ; la faisabilité de la fin de jeu héritée de `v3` reste supérieure à tout calendrier fixe qui n'est plus rentable.

---

<a id="4-historical-opening-templates"></a>
## 4. Modèles d'ouverture historiques

Les notes contiennent plusieurs idées d'ouverture. Elles doivent être conservées comme **des ouvertures alternatives pour référence/test**, et ne doivent pas être fusionnées en une seule ouverture obligatoire car elles ont été rédigées à des étapes différentes.

<a id="opening-candidate-a--fixed-initial-farm-package"></a>
### Ouverture candidate A — paquet initial fixe de ferme

|Article|Quantité|Coût enregistré|
| --- | ---: | ---: |
|Culture de blé (`W`)| 10 | 100 |
|Carotte (`C`)| 6 | 120 |
|Tomate (`T`)| 1 | 50 |
|Fraise (`S`)| 2 | 200 |
|Melon (`M`)| 2 | 160 |
|Gosse| 1 | 300 |
|Vache| 2 | 800 |
|Mouton| 1 | 500 |
|Stock de blé| 16 | 450 |
|Embauches| 4 | 7 |

Total enregistré dans la note :

```text
total cost = 2687
remaining cash = 313
```

Intention d'ouverture importante :

- planter et arroser les cultures initiales immédiatement ;
- maintenir suffisamment de blé pour alimenter les animaux ;
- après les premiers récoltes précoce, réaffecter les terres libérées selon les boutiques apparues ;
- utiliser les récoltes précoce de blé pour nourrir les animaux lorsqu'il est utile ;
- calculer combien de temps le stock actuel de blé dure et quand une nouvelle production de blé devient nécessaire.

<a id="opening-candidate-b--product-by-product-day-1-quantities"></a>
### Ouverture candidate B — quantités du jour 1, produit par produit

Un autre tableau de stratégie indique les quantités initiales suivantes :

|Produit|Quantité prévue au jour 1|
| --- | ---: |
|Melon| 2 |
|Carotte| 6 |
|Production d'œufs| 1 |
|Production de laine| 1 |
|Production de lait| 2 |
|Fraise| 2 |
|Blé| 2 |
|Tomate| 2 |

Ces valeurs sont conservées comme priorités historiques et doivent être reconsidérées en fonction de la demande actuelle de magasins, de la surface disponible, du personnel et des prévisions de marché, plutôt que d'être insérées de manière rigide.

---

<a id="5-tactical-land-expansion-schedules"></a>
## 5. Programmes de déploiement territorial tactique

Les vérifications de rentabilité et de faisabilité héritées de `v3` restent obligatoires. `v4` ajoute **des branches de timing et de disposition préférées** qui peuvent être testées lorsque ces vérifications sont satisfaites.

<a id="branch-a--first-two-shops-do-not-create-meaningful-animal-demand"></a>
### Branche A — les deux premiers magasins ne créent pas de demande animale significative

```text
T4: prefer buying NE as first expansion
T9: prefer buying SW as second expansion
```

Après l'acquisition du NE :

- si une demande animale apparaît, privilégiez les animaux ainsi que le soutien au blé ;
- si la demande animale reste absente, conservez environ une geai et utilisez le reste pour les cultures demandées par les magasins ;
- remplissez progressivement la nouvelle surface plutôt que de forcer une utilisation immédiate complète.

Pour l'extension au sud-ouest, les modèles de remplissage candidats incluent :

- `4 x 4` triangle ;
- `4 x 4` carré ;
- remplissage partiel conditionnel en fonction de la demande et du personnel disponible.

<a id="branch-b--first-two-shops-contain-animal-demand"></a>
### Branche B — les deux premiers magasins contiennent une demande animale

Utilisez une expansion antérieure :

```text
T4 : NE first expansion
T7 : SW second expansion
T12: SE third expansion
```

Les notes ajoutent également qu'il faut considérer la quatrième parcelle lorsque les deux premiers magasins présentent une demande animale.

Les modèles d'occupation du sud-est incluent :

- `4 x 4` triangle ;
- `4 x 4` sous-ensemble proche du centre ;
- remplissage conditionnel en fonction de la demande et du personnel disponible.

<a id="historical-timing-ceiling"></a>
### Limite temporelle historique

Une note antérieure indique également :

```text
first land  < T7
second land < T12
third land  < T12
```

Conservez cela comme une hypothèse expérimentale, sans le remplacer par la validation économique héritée de `v3`.

<a id="land-cash-floor"></a>
### Niveau minimal de liquidité sur la surface

En plus de la logique de réserves de liquidité héritée de `v3`, imposez une borne inférieure explicite :

```text
cash
- land_cost
- days_until_next_income * average_labor_price
> 300
```

Une seconde formulation des notes est :

```text
current_cash >=
    land_cost
    + immediate_deployment_cost_after_expansion
    + operating_reserve_until_first_harvest
```

Les deux formulations expriment la même intention stratégique : ne pas acheter de terrain si l'achat rend le domaine incapable d'opérer jusqu'à la prochaine récolte réalisable.

---

<a id="6-explicit-market-demand-and-opponent-forecast"></a>
## 6. Prévision explicite de la demande de marché et de l'adversaire

<a id="market-gap"></a>
### Gap de marché

Pour chaque produit, estimez le déficit futur comme suit :

```text
MarketGap =
    shop_demand
    + town_center_demand
    - own_expected_supply
    - opponent_expected_supply
```

Ne **pas** supposer que le remplacement complet de ce gap est toujours optimisé pour la rentabilité. La quantité économiquement optimale peut être plus petite car une offre excessive peut affaiblir le prix.

<a id="opponent-supply-model"></a>
### Modèle d'offre de l'adversaire

Suivez la production visible de l'adversaire :

- type de culture plantée et quantité ;
- type d'animal et quantité ;
- durée prévue de maturité de la production ;
- montant prévu de la production ;
- heure prévue de libération sur le marché.

Approximer l'offre de l'adversaire incertaine comme suit :

```text
OpponentExpectedSupply = VisibleCapacity * ExpectedExecutionRate
```

Les notes d'origine suggèrent explicitement des niveaux de probabilité faible / moyen / élevé lorsqu'exécution de l'adversaire est incertaine.

Lorsque les stocks de marché changent, utilisez-les comme preuve pour mettre à jour l'état estimé de l'offre de l'adversaire.

<a id="demand-certainty"></a>
### Certitude de la demande

```text
ConfirmedDemandWeight = 1
FutureExpectedDemandWeight < 1
```

La demande confirmée des magasins devrait donc influencer la production de manière plus forte que la demande future incertaine.

---

<a id="7-future-inventory---future-price"></a>
## 7. Inventaire futur -> prix futur

Utiliser la courbe du prix de marché au lieu de considérer le prix actuel comme permanent.

<a id="short-term-inventory-forecast"></a>
### Prévision de stockage à court terme

```text
FutureInventory =
    CurrentMarketInventory
    + FutureOwnSupply
    + FutureOpponentSupply
    - FutureShopConsumption
    - FutureTownConsumption
```

Ensuite :

```text
ExpectedFuturePrice = PriceFunction(FutureInventory)
```

<a id="long-term-approximation"></a>
### Approximation à long terme

Les notes proposent également :

```text
FutureInventory(h) =
    CurrentMarketInventory
    + h * (
        OwnAverageDailySupply
        + OpponentAverageDailySupply
        - ShopAverageDailyConsumption
      )
```

Ceci est utile lorsque la projection événement par événement n'est pas justifiée par le coût.

<a id="supply-timing"></a>
### Temps de livraison des produits

Distinction :

- approvisionnement synchronisé ;
- approvisionnement différé ;
- approvisionnement lissé.

Deux plans ayant la même production totale peuvent avoir une valeur différente si l'un évite de vendre au même creux de prix que l'autre.

---

<a id="8-marginal-production-economics"></a>
## 8. Économie de production marginale

Le choix de production doit comparer l'unité de capacité supplémentaire suivante, et non seulement le bénéfice total du projet.

<a id="expected-revenue"></a>
### Revenu attendu

Pour une culture unique :

```text
ER_i = ExpectedFuturePrice_at_harvest * ExpectedYield
```

Pour une production répétée, sommer chaque rendement futur au prix attendu de sa date de production :

```text
ER_i = sum_t(ExpectedPrice_t * ExpectedYield_t)
```

<a id="plant-direct-cost"></a>
### Coût direct de plantation

```text
PlantCost = SeedCost * Quantity + LaborCost
```

<a id="animal-direct-cost"></a>
### Coût direct animal

Les notes modélisent le coût animal comme :

```text
AnimalCost =
    PurchaseCost
    + FeedOpportunityCost
    + LaborCost
```

incluant le coût d'opportunité de nourriture, comprenant la valeur du blé qui aurait pu être vendu autrement.

<a id="marginal-value"></a>
### Valeur marginale

```text
MV_i = DeltaER_i - DeltaC_i - DeltaFeed_i - DeltaLabor_i
```

Un score stratégique plus complet permet également :

```text
MV_i += DeltaStrategic_i - DeltaRisk_i
```

<a id="value-per-land-time"></a>
### Valeur par unité de terre-temps

Comparer les produits selon la valeur marginale qu'ils produisent par unité de terre effective occupée et par durée de blocage :

```text
MarginalScore_i =
    MV_i
    / (AddedEffectiveLand_i * LandLockTime_i)
```

Les notes expriment également cette idée comme :

```text
Expected lifecycle profit per tile =
    (future sales revenue
     - seed/direct cost
     - labor cost
     - inventory/holding cost)
    / occupied land-days
```

<a id="additional-strategic-terms"></a>
### Termes stratégiques supplémentaires

L'ordre des candidats peut également inclure :

- coefficient de risque de marché ;
- coefficient de chute de prix ;
- valeur stratégique ;
- valeur d'option provenant de la préservation ou de l'amélioration de la disposition future ;
- optimisation de l'application de fertilisants ;
- le blé doit-il être produit localement ou acheté en externe.

---

<a id="9-historical-product-score-formulas"></a>
## 9. Formules de score historique de produit

Une feuille de stratégie précoce utilisait des approximations de score spécifiques aux produits. Leur notation est conservée ici car elles servent d'hypothèses expérimentales utiles, bien que la parenthésation exacte n'ait pas été entièrement définie dans la source.

|Produit|Idée de score enregistrée|
| --- | --- |
|Melon| `sum(q * dynamic_price) - 80 - fertilizer - labor / land_occupation` |
|Carotte| `sum(q * dynamic_price) - 20 - labor / land_occupation` |
|Œuf| `sum(q * dynamic_price) - 300 - labor * 1.6 / land_occupation` |
|Laine| `sum(q * dynamic_price) - 500 - labor * 1.6 / land_occupation` |
|Lait| `sum(q * dynamic_price) - 400 - labor * 1.6 / land_occupation` |
|Fraise| `sum(q * dynamic_price) - 100 - labor / land_occupation` |
|Blé| `sum(q * dynamic_price) - 10 - labor / land_occupation` |
|Tomate| `sum(q * dynamic_price) - 50 - labor / land_occupation` |

Ces formules datent de avant le modèle marginal de valeur plus général ci-dessus. Elles doivent donc être considérées comme des règles de calibration candidates plutôt qu'un deuxième moteur économique indépendant.

---

<a id="10-historical-demand-formulas"></a>
## 10. Formules historiques de demande

Les notes contiennent également des estimations spécifiques aux produits de demande. Leurs abréviations (`Dm`, `Npc`, `Nfm`, `Nb`, `Nbs`, `Ny`, `Np`, `Ni`, `Ns`, `Nic`, `q`) n'ont pas été entièrement définies dans la source, donc les formules sont conservées plutôt que reconsidérées.

|Produit|Formule enregistrée `Dtotal`|
| --- | --- |
|Melon| `Dtotal = 1/day` |
|Carotte| `Dtotal = Dm + 12 * Npc * q + 6 * Nfm * q` |
|Œuf| `Dtotal = Dm + 6 * Nb * q + 6 * Nbs * q` |
|Laine| `Dtotal = Dm + 12 * Ny * q` |
|Lait| `Dtotal = Dm + 6 * Np * q + 6 * Ni * q + 6 * Ns * q` |
|Fraise| `Dtotal = Dm + 6 * Nb * q + 6 * Nic * q + 6 * Ns * q + 6 * Nfm * q + 6 * Ns * q` |
|Blé| `Dtotal = Dm + 6 * Ni * q + 6 * Nb * q + 6 * Ns * q + 6 * Nfm * q + 6 * Nb * q` |
|Tomate| `Dtotal = Dm + 6 * Np * q + 6 * Nfm * q` |

Les termes répétés sont laissés exactement tels qu'ils ont été enregistrés, sans correction silencieuse.

---

<a id="11-production-quantity-should-react-to-opponent-supply"></a>
## 11. La quantité de production doit réagir à l'offre de l'adversaire

Pour un produit que l'adversaire ne produit pas, comparez la note de produit une fois que suffisamment de terres deviennent disponibles.

Si l'adversaire produit déjà :

```text
AdjustedGap = MarketGap - OpponentSupply
```

et réévaluez la valeur supplémentaire de la production encore disponible.

Suivez la date et la quantité de la prochaine récolte de l'adversaire avant de choisir notre propre calendrier de production et de vente.

Les notes définissent également une notion de marge concurrentielle :

```text
MarginMax = OurProfit - OpponentProfit
```

Cela peut être utilisé comme signal stratégique secondaire, mais ne doit pas remplacer la rentabilité absolue.

---

<a id="12-sell-decision--current-marginal-value-vs-retention-value"></a>
## 12. La décision de vente = valeur marginale actuelle vs valeur de retenue

Ne vendez pas simplement parce que l'inventaire existe.

Pour chaque unité supplémentaire considérée :

```text
CurrentMarginalSalePrice =
    P(CurrentMarketInventory + considered_unit_index - 1)
```

Comparez-la à la valeur de conserver l'unité :

```text
RetentionValue = max(
    FutureResaleValue,
    ProductionUseValue,
    SafetyStockValue
)
```

Vendez lorsque :

```text
CurrentMarginalSaleValue > RetentionValue
```

et arrêtez lorsque la valeur marginale de la vente baisse en dessous de la valeur marginale de retenir la prochaine unité.

---

<a id="13-time-discounted-future-resale-value"></a>
## 13. Valeur de revente future discrétionnée dans le temps

Une vente future doit être discrétionnée car les fonds reçus plus tard sont moins utiles que les fonds disponibles actuellement.

Les notes proposent :

```text
FutureResaleValue(h) = E[P(t + h)] / (1 + r)^h
```

avec une estimation expérimentale de taux d'opportunité :

```text
r = ((CapitalPrepared + ExtraNetBenefit) / CapitalPrepared)^(1 / h) - 1
```

La source mentionne l'évaluation de plus d'un horizon `h`, y compris la prochaine et la dernière opportunité de vente pertinente ; la convention exacte d'averagage n'est pas entièrement spécifiée.

---

<a id="14-cash-urgency-changes-the-sell-threshold"></a>
## 14. L'urgence du cash modifie le seuil de vente

Définissez la pression de cash à court terme liée à des dépenses nécessaires :

```text
CashUrgency =
    (NearTermRequiredSpend - CurrentCash)
    / NearTermRequiredSpend
```

Puis réduisez alors le seuil normal de retenue/vente lorsque l'urgence du cash augmente :

```text
AdjustedSellThreshold =
    BaseSellThreshold - CashUrgencyAdjustment
```

Les anciennes notes font également référence à un coefficient `lambda` comme facteur de besoin en cash.

Cela permet au planificateur de vendre plus tôt lorsque le cash est stratégiquement plus précieux que de patienter pour le prix théorique optimal du marché.

---

<a id="15-control-price-impact-and-sale-quantity"></a>
## 15. Contrôler l'impact de prix et la quantité de vente

Estimez la détérioration du prix causée par une vente :

```text
PriceImpactRate =
    (PriceBeforeSale - PriceAfterSale)
    / PriceBeforeSale
```

Ne vendez pas plus que ce que le marché peut absorber à court terme :

```text
SaleQuantity <= ShortTermAbsorbableDemand
```

Choisissez la plus grande quantité de vente pour laquelle la valeur marginale de vente reste supérieure à la valeur marginale de retenue **sans provoquer inutilement une chute du prix**.

Cela répond explicitement à la remarque selon laquelle combler tout le gap de marché n'est pas toujours une action optimisante en termes de profit.

---

<a id="16-sell-before-expected-opponent-supply-when-profitable"></a>
## 16. Vente avant l'offre prévue de l'adversaire lorsque rentable

Les dates de maturité de l'adversaire créent des fenêtres de vente.

Stratégie générale :

- estimez la date de prochaine récolte / production de l'adversaire ;
- considérez la vente partielle de notre inventaire avant l'arrivée de cette offre ;
- évitez de attendre dans une chute de prix prévisible causée par l'adversaire ;
- si les deux côtés produisent en même temps, envisagez de réagir rapidement à la sortie de l'adversaire plutôt que d'attendre aveuglément.

Règle historique du tableau de produit :

```text
if combined supply < shop consumption:
    sell n units before opponent's next maturity,
    subject to value constraints

if combined supply > shop consumption:
    prefer selling around maturity rather than accumulating excess stock
```

Le melon avait une règle historique particulièrement agressive : vider l'inventaire avant la maturité de l'adversaire, et si les deux plantent en même temps, réagir immédiatement lors de la vente de l'adversaire.

---

<a id="17-explicit-split-sale-comparison"></a>
## 17. Comparaison explicite de ventes fractionnées

Les notes ultérieures définissent un test concret pour décider de vendre maintenant ou de diviser la vente.

Définitions :

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

Privilégier le chemin de vente divisée lorsque :

```text
(n + m) * P1 - x * P5
<
n * P1 + m * P4 - x * P3
```

Interprétation : comparer la valeur stratégique de vendre immédiatement `n + m` maintenant avec la vente de `n` maintenant et de `m` plus tard, en tenant compte de l'interaction de prix de l'adversaire.

---

<a id="18-inventory-overflow-formula"></a>
## 18. Formule de surstockage de l'inventaire

Avant que le stockage ne devienne complet, estimer explicitement la liquidation nécessaire :

```text
NeedSell = Shed + Carry + Incoming - 99
```

Si `NeedSell > 0`, au moins cette quantité doit être vendue ou autrement retirée avant que le stock entrant ne parvienne au local de stockage.

Cela affine la logique de faisabilité du stockage héritée de `v3` avec une quantité de liquidation directe.

---

<a id="19-product-specific-inventory-policy"></a>
## 19. Politique d'inventaire spécifique au produit

<a id="fertilizer"></a>
### Fertilisant

- préférer la vente immédiate lorsque le fertilisant n'est pas nécessaire pour une fertilisation rentable à court terme ;
- éviter le stockage à long terme car il est continuellement produit et la demande externe est faible.

<a id="melon"></a>
### Melon

- éviter le stockage à long terme ;
- vente immédiate ou planification de la vente face à l'adversaire ;
- les notes historiques limitent la production combinée de melon autour de `120` ;
- la fertilisation est autorisée / encouragée dans la stratégie historique du melon.

<a id="wheat"></a>
### Blé

Réservé principalement pour l'alimentation des animaux et les opérations d'urgence :

```text
WheatReserve =
    5 * animal_q
    - WheatExpectedToMatureInNext5Days
```

Vendre les excès de blé au lieu de les occuper de manière permanente dans le local de stockage.

Comparer également la production auto-du blé avec l'achat sur le marché.

<a id="egg"></a>
### Œuf

- si aucune boutique pertinente n'existe, ne pas maintenir un inventaire inutile d'œufs ;
- avec la demande de boulangerie / de petit-déjeuner, maintenir environ une journée de demande ;
- la politique animale historique utilisait quotidiennement `CARE`.

<a id="carrot"></a>
### Carotte

- pas de demande de PetCafe -> vendre plutôt que de le garder ;
- avec la demande de PetCafe / du marché des agriculteurs -> maintenir environ deux jours de demande ;
- éviter de maintenir de grands stocks à long terme ;
- traiter comme un produit à rotation courte ;
- règle historique : aucune fertilisation.

<a id="tomato"></a>
### Tomate

- si les plants matures garantissent déjà le renouvellement, l'inventaire peut être vendu plus agressivement ;
- idée historique de calendrier : fertiliser autour de `T8`, récolter autour de `T9` et `T11`.

<a id="strawberry"></a>
### Fraise

- avec des boutiques pertinentes, réserver environ deux jours de **demande nette** ;
- préférer des lots de ventes plus petits pour éviter des dommages inutiles sur le prix ;
- idée historique de calendrier : fertiliser autour de `T10`, récolter à `T12`, fertiliser à `T14`, récolter à `T16`.

<a id="milk"></a>
### Lait

- avec une demande pertinente, maintenir environ deux jours de demande nette ;
- sans boutique pertinente, si une vache est proche de produire plus de lait, augmenter la priorité de vente actuelle de lait ;
- préférer des lots petits ;
- règle historique : vendre au prix élevé ;
- règle historique de soins omis autour de `CARE` à `T5–T7`.

<a id="wool"></a>
### Laine

- garder la laine en attente de la demande de laine ;
- sans demande de laine, envisager la vente ;
- programme de soins historique utilisé quotidiennement, sauf autour de `T5`.

---

<a id="20-inventory-priority-classes"></a>
## 20. Classes de priorité de l'inventaire

Les notes regroupent également les stocks en cinq grandes catégories.

<a id="class-1--operating-inventory-only"></a>
### Catégorie 1 — inventaire opérationnel uniquement

`Wheat`

Conserver les aliments + la réserve d'urgence, mais ne laisser pas les excès de blé occuper la grange pendant de longues périodes.

<a id="class-2--fast-turnover"></a>
### Catégorie 2 — rotation rapide

`Carrot`

Utiliser par défaut des périodes de stockage courtes ; augmenter le stock à court terme uniquement lorsque la demande au magasin est forte.

<a id="class-3--balanced"></a>
### Catégorie 3 — équilibrée

`Tomato`, `Egg`

Peut être stockée, mais n'obtient généralement pas la priorité la plus élevée dans la grange. La conservation dépend principalement de la fenêtre de demande suivante.

<a id="class-4--high-value-timing-inventory"></a>
### Catégorie 4 — inventaire à haute valeur et timing

`Strawberry`, `Milk`, `Wool`

Lorsque la demande est confirmée et qu'une pénurie future est prévisible, accorder une priorité accrue au stockage de ces produits et éviter la liquidation massive à bas prix.

<a id="class-5--avoid-long-holding"></a>
### Catégorie 5 — éviter de garder longtemps

`Melon`, `Fertilizer`

Privilégier la rotation car le melon manque d'un point de consommation stable au magasin et le fertilisant est régénéré continuellement.

---

<a id="21-seed--animal-deployment-capacity-constraint"></a>
## 21. Contrainte de capacité de déploiement des semences / des animaux

Ne pas acheter plus de production immédiatement déployable que la capacité de placement disponible ne peut absorber.

Contrainte historique :

```text
sum(seed_units_to_deploy) + number_of_animals_to_place
<= available_free_tiles
```

La conversion exacte des unités de semences / structures en cases occupées dépend encore de la nature de la production et du modèle de placement hérité de `v3`.

---

<a id="22-animal-action-ordering"></a>
## 22. Ordre d'action des animaux

Lorsque l'animal est censé effectuer une visite productive, les notes préfèrent :

```text
FEED
-> HARVEST
-> CARE
-> COLLECT_FERTILIZER
```

Ceci est plus précis que le regroupement des tâches d'animaux sensibles aux dépendances hérité de `v3`.

L'entretien en fin de partie doit s'arrêter lorsque l'animal n'a plus de production rentable. Critère historique spécifique est :

```text
if next useful production is beyond the remaining horizon
and fertilizer value < maintenance cost:
    stop FEED / CARE
```

La règle générale v3 décide encore de la faisabilité finale.

---

<a id="23-abandonment--liquidation-trigger-from-expected-price"></a>
## 23. Déclencheur d'abandon / de liquidation à partir du prix attendu

Ne pas maintenir une production simplement parce qu'elle existe déjà.

Si :

```text
ExpectedMarketValue
< MaintenanceCost + HarvestCost + CleanupCost
```

Commencer à liquidationner ou à abandonner la production au lieu de continuer à consacrer du travail.

Les notes historiques proposent également de commencer une liquidation générale à la journée précédant la dernière. La faisabilité exacte de la sortie de liquidation en v3 reste la contrainte dure la plus forte.

---

<a id="24-recompute-on-new-shops"></a>
## 24. Recalculer en cas d'apparition de nouveaux magasins

Lorsqu'un nouveau magasin apparaît, recalculer immédiatement la demande et les économies de tous les produits concernés.

Cela inclut :

- la quantité cible de production ;
- la pénurie prévue ;
- la réserve d'inventaire ;
- le moment de vente ;
- l'occupation du terrain ;
- l'allocation entre animaux et cultures.

`v3` recalculait déjà sur les modifications économiquement pertinentes des magasins ; `v4` ajoute la nécessité que les **modèles de demande de marché et de valeur marginale** soient recalculés eux-mêmes.

---

<a id="25-market-aware-product-specific-sell-behavior"></a>
## 25. Comportement spécifique de vente des produits, sensible au marché

Les notes stratégiques historiques incluent les préférences suivantes au niveau des produits :

- Carotte / Œuf / Blé / Tomate : vendre plus tôt lorsque de l'argent est nécessaire ;
- Laine : attendre le fil lorsque cela est plausible ;
- Lait / Fraise : privilégier les fenêtres à prix élevé ;
- Melon : vendre immédiatement ou avant l'approvisionnement de l'adversaire ;
- tous les produits : lorsque la capacité de vente est serrée, vendre selon l'ordre de priorité sur le profit plutôt que selon l'ordre FIFO / ordre arbitraire.

Ces sont des heuristiques de secours dans les cas où le modèle marginal de vente complet est trop coûteux ou incertain.

---

<a id="26-core-strategic-chain"></a>
## 26. Chaîne stratégique centrale

La couche économique v4 peut être résumée comme suit :

```text
shops define demand
-> own + opponent production define future supply
-> future supply and demand define future market inventory
-> market inventory defines expected price
-> expected price defines marginal revenue
-> marginal revenue minus direct/feed/labor/land/risk costs defines marginal value
-> marginal value decides what to produce, how much to produce, what to hold, and what to sell
```

Cette chaîne est l'idée centrale de v4.

---

<a id="key-invariants-added-by-v4"></a>
## Invariants clés ajoutés par v4

- Ne jamais dépasser `14` travailleurs.
- Ne pas embaucher un travailleur dont la valeur économique marginale est inférieure au coût marginal d'embauche.
- Conserver les animaux à maintenance élevée dans la zone préférée proche du centre lorsque cela est possible.
- Préserver le central `2 x 2` pendant que la règle de réservation est active, en ce qui concerne les cultures à longue durée.
- Ne pas laisser une date de prise de terrain préférée contourner la rentabilité, le cash, la faisabilité de la route ou la faisabilité à la fin du jeu héritée de `v3`.
- Ne pas acheter de terrain si le seuil de liquidité opérationnelle explicite serait violé.
- Prévoir la production adverse et le timing du marché lors de la prise de décision sur la production et la vente.
- Ne pas supposer que la satisfaction complète de la pénurie de marché maximise le profit.
- Comparer la valeur marginale de la vente d'une unité avec la valeur marginale de sa conservation.
- Limiter la taille de la vente lorsque l'ajout de nouvelles unités entraînerait un impact excessif sur le prix.
- Conserver des stocks de sécurité spécifiques à un produit uniquement s'ils ont une valeur en matière de nourriture, de demande ou stratégique.
- Utiliser `NeedSell = Shed + Carry + Incoming - 99` pour quantifier une liquidation d'urgence.
- Arrêter de maintenir une production dont la valeur de marché attendue restante ne peut pas couvrir ses coûts opérationnels restants.

---

<a id="what-v4-changes-relative-to-v3"></a>
## Quelles sont les modifications de v4 par rapport à v3

`v3` a rendu le planneur interne cohérent. `v4` ajoute une politique économique plus explicite sur ce planneur cohérent :

1. des contraintes rigides sur les travailleurs et la disposition spatiale ;
2. des préférences initiales tactiques et d'extension du terrain ;
3. une prévision explicite de la production adverse ;
4. une prédiction du prix basée sur l'inventaire futur ;
5. la valeur marginale de la production par unité de temps de terrain ;
6. la valeur marginale du travail pour l'embauche ;
7. la valeur de conservation et la vente discrétisée dans le temps ;
8. des ventes partielles sensibles à l'impact sur le prix ;
9. des réserves d'inventaire spécifiques à un produit et des classes de rotation ;
10. des règles concrètes de seuil de liquidité, de surcharge et de liquidation.

Les horaires et quantités fixes enregistrés dans les feuilles historiques sont **des heuristiques de référence candidats**, tandis que les règles de faisabilité et de rentabilité héritées de `v3` restent la porte finale.


---

<a id="navigation"></a>
## Navigation

[← Version précédente](heuristic_ideas_v3.fr.md) · [Version finale consolidée →](heuristic_ideas_final.fr.md)
