[English](game_rules.md) | [Français](game_rules.fr.md) | [简体中文](game_rules.zh-CN.md)

[README du projet](../README.fr.md)

<a id="kaggriculture-game-rules"></a>
# Règles du jeu Kaggriculture

Ce document contient les mécaniques et les règles utilisées comme référence pendant le développement de l'agent Kaggriculture.

Ces règles sont basées sur la documentation officielle de la compétition Kaggriculture.

> Ce document est maintenu pour référence de développement. La documentation officielle de la compétition reste la source autorisée.

<a id="kaggriculture"></a>
# Kaggriculture

Un simulateur de ferme où deux joueurs s'affrontent pour maximiser leurs revenus en vendant leurs produits à un marché dynamique.

<a id="overview"></a>
## Aperçu

Chaque joueur commence avec une ferme vide et un petit montant d'argent (une somme initiale, si vous voulez). À chaque tour, il peut effectuer des actions telles que se déplacer sur le plateau, acheter des semences ou des animaux, planter des semences, arroser les plantes, récolter des produits ou des produits animaux, puis les vendre au marché. Le jeu dure une durée fixe représentant une saison, et le gagnant est déterminé par celui qui a le plus d'argent au compte bancaire à la fin.

<a id="object-types"></a>
## Types d'objets

|Type|Type de rendement|Coût de semence|Prix de marché de base|Durée jusqu'au premier rendement|Durée jusqu'au rendement maximal|Rendements successifs|Rendement maximal|Coût d'action|Rendement / case / jour|
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
|**Blé**|Unique| 10 | 25 |2 jours|4 jours|aucun|6 (4 sans engrais)| 1 | 0.80 |
|**Carotte**|Unique| 20 | 35 |2 jours|3 jours|aucun|4 (3 sans engrais)| 1 | 0.75 |
|**Tomate**|Continu| 50 | 60 |8 jours|11 jours|chaque jour ×4| 4 | 1 | 0.33 |
|**Fraise**|Continu| 100 | 120 |10 jours|16 jours|chaque deux jours ×4| 4 | 1 | 0.24 |
|**Melon**|Unique| 80 | 250 |10 jours|10 jours|aucun| 6 | 1 | 0.55 |
|**Gosse/Oeuf**|Continu| 300 | 50 |4 jours|NA|chaque jour, indéfiniment|4 conservés|1 \+ 1 (construire un abri)| 1.00 |
|**Vache/Lait**|Continu| 400 | 160 |8 jours|NA|chaque deux jours, indéfiniment|6 conservés|1 \+ 1 (construire un parc)| 0.50 |
|**Mouton/Élégance**|Continu| 500 | 200 |6 jours|NA|chaque trois jours, indéfiniment|6 conservés|1 \+ 1 (construire un parc)| 0.33 |
|**Engrais**|NA| 100 |X|  |X|X|  | 1 |  |

Pour les cultures, « Rendement / parcelle / jour » correspond à la quantité totale récoltée divisée par le nombre de jours pendant lesquels la parcelle est occupée, avec une irrigation quotidienne et une récolte à la période de rendement maximal. Pour les animaux, c'est le taux de production stable (`1 / interval`) atteint dès la première récolte ; les animaux continuent de produire tant qu'ils sont nourris, donc il n'y a pas d'occupation fixe à diviser. Le « Rendement maximal » pour les animaux est `max_held`, la limite du produit non récolté restant sur la parcelle, et non une somme totale de vieillissement.

Pour les cultures, le « temps jusqu’au rendement maximal » est l’âge auquel le rendement cesse d’augmenter avec un arrosage quotidien. Il ne correspond pas toujours à la fin de la période de bonus :

- Pour le **Melon**, la période de bonus va de 6 à 12 jours, mais la base de 1 unité, augmentée d’une unité par jour arrosé, atteint le plafond de 6 à 10 jours. Les jours 11 et 12 n’ajoutent donc rien. Avec fertilisation, ce plafond est atteint à 8 jours.
- Le **blé** et la **carotte** atteignent leurs rendements maximaux indiqués de 6 et 4 uniquement avec fertilisation ; avec le seul arrosage, les plafonds sont respectivement de 4 et 3.
- La **tomate** et la **fraise** produisent en continu, mais *pas* indéfiniment : la production est limitée à 4 récoltes programmées, aux âges 8–11 pour la tomate et 10, 12, 14 et 16 pour la fraise. La plante se dégrade ensuite en mauvaise herbe.

Toutes les plantes doivent être arrosées chaque jour ; deux jours consécutifs sans arrosage les transforment en mauvaises herbes. Tous les animaux doivent être nourris chaque jour avec du blé ; après deux jours consécutifs sans nourriture, ils s’échappent et ne peuvent plus être récupérés. Le blé est aussi disponible à l’achat au prix courant du marché.

<a id="actions"></a>
## Actions

Le joueur peut effectuer une action par tour. Une journée compte 24 tours et la saison dure 30 jours, soit 720 tours au total.

<a id="farmer--farm-hand-action"></a>
### Action du fermier / de l’ouvrier agricole

Chaque fermier ou ouvrier agricole peut recevoir une action à chaque tour. Ils **peuvent** occuper la même case.

<a id="movement"></a>
#### Déplacement

- NORD, SUD, EST, OUEST — Déplacez une case dans cette direction. Les déplacements en dehors des limites du plateau sont ignorés. Les cases verrouillées sont passables : une unité peut se déplacer sur et traverser des quadrants non achetés, mais les actions de case (`PLANT`, `WATER`, `BUILD_*`, etc.) sont ignorées sur une case verrouillée et ne consomment rien. L'exception est le groupe d'actions de grange `PICKUP`, `DROP` et `PLACE`-into-shed, qui fonctionnent à partir de toute case d'accès à la grange, même si cette case est verrouillée — elles utilisent la case uniquement comme position d'attente et ne la modifient jamais.

<a id="shed"></a>
#### Grange

Récupère un objet de la grange (doit être orthogonalement adjacent) dans l'inventaire

- PICKUP `<item>` `[n]` — déplace jusqu'à `n` de `<item>` (par défaut 1) de la grange dans l'inventaire actif du fermier/du main. Tout objet présent dans la grange est valide (animaux, engrais, produits récoltés, etc.). Les graines sont disponibles dans un emplacement séparé et ne sont jamais récupérées — `PLANT` les consomme directement.
- DROP — orthogonalement adjacent à la grange, vide l'ensemble de l'inventaire actif du fermier/main dans la grange. Les éléments en excès au-delà de `shedCapacity` sont ignorés. Aucune action si pas adjacent à la grange.

<a id="plants"></a>
#### Plantes

- PLANT — Plante une graine achetée au marché
  - Les graines sont automatiquement disponibles pour tous les Fermiers / Ouvriers agricoles
  - Si vous tentez de planter trop de graines en un tour spécifique, aucune ne sera plantée
    - par exemple, si vous avez 1 graine de melon, mais deux unités effectuent la commande PLANT MELON
- EAU — Arroser une plante. Cela ne doit être effectué qu'une fois par jour, et les arrosages successifs sur la même journée sont sans effet.
- RECOLTE — Récupérer les produits d'une plante. Si la plante n'a pas de rendements successifs, elle est supprimée de la carte. Chaque action de récolte donne au moins une unité du produit, avec un potentiel de rendement supplémentaire selon l'arrosage et l'apport de fertilisant (la formule varie selon le type de culture — voir les rendements de récolte ci-dessous). Les produits récoltés sont ajoutés à l'inventaire.
- FERTILISER — Apporter du fertilisant à une plante afin d'augmenter son potentiel de rendement (voir les rendements de récolte ci-dessous).
  - Double le bonus quotidien de rendement pour les 3 jours suivants. Ce bonus ne s'applique que les jours où la plante est également arrosée (besoins de base d'abord).

<a id="animals"></a>
#### ANIMAUX

- PLACER `<item>` `[n]` — Déposer des objets de l'inventaire actif du fermier ou de la main dans une case ou dans le grenier :
  - **Placement d'animal** : se tenir sur une structure libre correspondante (`GOOSE` sur un poulailler, `SHEEP`/`COW` sur une prairie) place un animal de l'inventaire sur la case. L'argument `n` est ignoré.
  - **Dépôt dans le grenier** : se tenir orthogonalement adjacent au grenier permet de déposer jusqu'à `n` (valeur par défaut 1) de `<item>` de l'inventaire dans le grenier. Ce dépôt est limité par `shedCapacity` ; les excédents restent dans l'inventaire.
- ALIMENTER — Alimenter un animal avec du blé (ne doit être effectué qu'une fois par jour)
- RECOLTE — Récupérer les œufs / lait / laine produits par l'animal.
- RECOLTER\_FERTILISANT — Récupérer 1 unité de fertilisant de l'animal. Chaque animal survivant fournit 1 unité à la fin de chaque jour, qu'il ait été nourri ou non. Le fertilisant non récupéré ne s'accumule pas, donc un animal laissé seul pendant cinq jours fournit toujours 1 unité.
- SOINS — Prendre soin d'un animal (une fois par jour, sans effet si déjà pris en charge). Voir les soins aux animaux ci-dessous.

<a id="animal-care"></a>
#### Soins aux animaux

Les soins permettent de bank un bonus qui est versé lors de la prochaine production prévue de l'animal :

* À la fin de la journée, si l'animal a été à la fois nourri et pris en charge ce jour-là, `pending_care_bonus` augmente de 1. Les jours où l'animal n'a pas été nourri ne permettent pas de bank un bonus (besoins de base d'abord).
* Le jour de production prévu, si l'animal est nourri, le bonus banké est ajouté au rendement de cette production (en plus du rendement de base de 1) et le bank est réinitialisé à 0.
* Si l'animal n'est pas nourri le jour de production, le rendement de base de 1 unité est toujours produit, mais le bonus banké n'est pas appliqué et le bank est réinitialisé à 0.
* `pending_care_bonus` est indirectement limité par la limite par animal `max_held` sur `yield_units`.

<a id="terrain"></a>
#### TERRAIN

- CONSTRUIRE\_POULAILLER — Ajoute un poulailler à une case non occupée
- CONSTRUIRE\_PRAIRIE — Ajoute une prairie à une case non occupée
- DIGER — Retirer une plante d'une case pour libérer de l'espace OU retirer une mauvaise herbe d'une case (ne produit aucun produit) OU retirer un **poulailler vide** / une **prairie vide**. Un poulailler ou une prairie avec un animal dedans ne peut pas être détruit ; l'action DIG est sans effet.

<a id="other"></a>
#### AUTRES

- PASS — Action par défaut si rien à faire (optionnel)

<a id="market-action"></a>
### ACTION DU MARCHÉ

Chaque tour, vous pouvez soumettre jusqu'à `maxMarketOrdersPerTurn` (par défaut 10) actions de marché ; tout ordre au-delà de ce seuil est silencieusement ignoré. C'est une liste ordonnée et les ordres de marché seront traités en ordre simultané (un ordre par joueur) tant que les deux joueurs ont des ordres.

- ACHETER\_SEED — Acheter N unités d'un seul article sur le marché.
  - ACHETER\_SEED WHEAT 1
- ACHETER\_ANIMAL \-
  - ACHETER\_ANIMAL GOOSE 1
- ACHETER\_PRODUCT
  - ACHETER\_PRODUCT WHEAT 1
  - ACHETER\_PRODUCT FERTILIZER 1
- VENDRE — Vendre N unités d'un seul article au marché.
  - VENDRE WHEAT 1
- EMBAUCHE — Engager un travailleur pour la journée. Le coût augmente pour chaque autre main embauchée le même jour.
- ACHETER\_LAND \- débloque une nouvelle zone de 5x5 de terrain à planter. Le coût augmente.
  - Les coûts sont : $1k, $2k, $4k

<a id="watering--animal-feed"></a>
## Arrosage / Alimentation des animaux

Les plantes (et les animaux) doivent être arrosées/ alimentées au moins tous les deux jours. L'arrosage ne doit être effectué qu'une fois par jour, et les actions d'arrosage ultérieures sont sans effet. Si une plante n'est pas arrosée pendant deux jours consécutifs, à la fin de la journée, elle devient une HERBE. Si un animal n'est pas alimenté, il s'échappe (indéfectible).

Une nouvelle semence commence avec `consecutive_unwatered = 1` — la journée de plantation elle-même est comptée comme la première journée manquée. Une semence plantée et laissée sans arrosage la même journée atteint 2 à la fin de la journée et devient une herbe la nuit suivante, avant de pousser. Il n'y a pas de période de grâce pour les plantes fraîchement plantées.

Un nouvel animal commencé avec `consecutive_unfed = 0`, donc il survit son premier jour sans nourriture.

Notez que l'arrosage des plantes à rendement unique pendant leur période de rendement augmente leur rendement. Ce n'est pas vrai pour les plantes ou animaux à rendement continu. Voir ci-dessous.

<a id="harvest-yields"></a>
## Rendements de récolte

Les plantes peuvent avoir des rendements plus élevés selon la qualité de leur entretien.

* **Cultures à rendement unique** (blé, carotte, melon) : À partir de la moitié du temps de croissance maximal de la plante (`max_yield_day`), arrondi au supérieur, l'arrosage pendant la période de bonus ajoute une unité par jour au rendement total récoltable.
  * Les plantes fertilisées ajoutent 2 par jour au lieu de cela.
* **Cultures à rendement continu** (tomate, fraise) : La production planifiée se produit à intervalles réguliers. Le rendement de base est de 1 par production planifiée. Si la plante est fertilisée ET arrosée ce jour-là, le rendement est doublé à 2.
* Une fois qu'une plante a atteint sa durée de vie maximale, le rendement total disponible sur la plante diminue de 1 tous les deux tours jusqu'à ce qu'il atteigne 0, à ce moment-là la plante devient une herbe.
  * **Cultures à rendement unique** atteignent leur durée de vie maximale une journée après `max_yield_day`.
  * **Cultures à rendement continu** commencent à dégrader une journée après que leur compteur cumulatif de production atteint `max_yield` (c'est-à-dire qu'ils ont déclenché assez de productions planifiées pour atteindre la limite, quel que soit le fait que les produits aient été récoltés).

<a id="map-features"></a>
## Fonctions de la carte

Chaque joueur possède sa propre ferme avec un nombre fixe de cases. Les joueurs ne peuvent pas voir l'état de la grange de l'autre, mais peuvent voir l'état de la ferme de l'adversaire.

<a id="farm-space"></a>
### Espace de la ferme

- La terre située près de votre ferme est un quadrillage `boardSize` × `boardSize` (par défaut 10×10), divisé en quatre quadrants de 5×5. Au départ, votre ferme occupe un seul quadrant (25 % des cases). Pour une prime de plus en plus élevée, vous pouvez acheter les quadrants voisins et finalement couvrir 100 % des cases.
- Chaque culture ou animal occupe une case sur la ferme.
- Les joueurs peuvent allouer ces cases selon leur choix entre cultures et animaux de ferme. Il n'y a pas de limite spécifique par type.
- Les mauvaises herbes ont une chance de se former sur n'importe quelle case vide sur la ferme, et doivent être éliminées avant que la terre ne puisse être utilisée à d'autres fins.
- Les cases sur la ferme peuvent être occupées par une culture, un poulailler/terrain de pâturage, une mauvaise herbe ou être vides.

<a id="shed-inventory"></a>
### Atelier (Inventaire)

- Sert de stockage pour les produits récoltés mais non encore vendus, ou pour les semences non encore plantées
- Le fermier et les ouvriers embauchés apparaissent à l'atelier au début de chaque jour
- Le fermier et les ouvriers embauchés déposent leur inventaire à la fin de la journée dans l'atelier (si il y a de la place)
- Limite à 100 articles, excluant les semences. Une fois l'atelier plein, tous les articles supplémentaires ajoutés (via `PLACE` au milieu de la journée ou à la fin de la journée) sont éliminés — il n'y a pas de zone de stockage en surcharge, donc le stockage sur les inventaires des fermiers/ouvriers ne permet pas de contourner cette limite.

L'atelier se situe au centre du plateau et n'est pas une case — il ne figure jamais dans l'array `tiles`, dont les seules valeurs sont `None`, `"LOCKED"` et des dictionnaires de structures. « Orthogonalement adjacent à l'atelier » signifie se trouver sur l'une des quatre cases centrales, `(half-1, half-1)`, `(half, half-1)`, `(half-1, half)`, `(half, half)` pour `half = boardSize // 2`. À la taille par défaut `boardSize = 10`, ces cases sont `(4,4)`, `(5,4)`, `(4,5)` et `(5,5)`, une dans chaque quadrant. Puisque seulement le quadrant NW est débloqué au départ, trois des quatre cases sont initialement bloquées ; l'atelier est toutefois accessible depuis chacune d'elles, car l'atelier lui-même n'est jamais bloqué.

<a id="farmerfarm-hand"></a>
### Fermier / Ouvrier de ferme

<a id="hiring"></a>
#### Embauche

- L'embauche est une commande de marché (`HIRE`). Elle coûte de plus en plus chaque fois que vous souhaitez embaucher un autre ouvrier chaque jour. À la fin de la journée, tous les ouvriers disparaissent (ils doivent être réembauchés chaque jour)
- Le coût est `farmHandCostMult * fib(n)` où `n` est le nombre d'embauches déjà effectuées aujourd'hui (séquence de Fibonacci : 1, 1, 2, 3, 5, 8, 13, ...).
  - Avec la valeur par défaut `farmHandCostMult = 1` : 1, 1, 2, 3, 5, 8, 13, 21, etc… (réinitialisée au début de chaque jour)
- Un ouvrier embauché apparaît orthogonalement adjacent à l'atelier dans un espace libre, selon l'ordre NWSE. Si aucun espace libre n'est disponible, il cherche la case avec le moins d'occupants, en cas d'égalité selon l'ordre NWSE.
- La position d'apparition ignore si la case est bloquée. Puisque le fermier principal commence sur `(4,4)`, la règle du moins occupé envoie le premier ouvrier embauché chaque jour sur `(5,4)`, qui est bloqué jusqu'à l'achat du quadrant NE. Les cases bloquées sont passables, donc un ouvrier apparu sur une telle case peut se déplacer vers des terres débloquées.

<a id="inventory"></a>
#### Inventaire

- Lors de la récolte ou de la récupération d'objets, ils sont ajoutés à l'inventaire.
- Peut déposer des objets dans l'atelier
- À la fin de la journée, tous les objets présents dans tous les inventaires sont ajoutés à l'inventaire de l'atelier (si il y a de la place). Tout ce qui ne rentre pas est éliminé — il n'y a pas de stockage en surcharge.

<a id="town-buildings"></a>
### Bâtiments de la ville

Au fur et à mesure que la saison avance, de nouveaux magasins s'ouvrent à intervalles réguliers (chaque `townShopUnlockInterval` jours, par défaut 3). Chaque ouverture est choisie de manière uniforme et aléatoire **avec remise** dans le tableau complet des magasins, de sorte que le même magasin peut s'ouvrir plusieurs fois — une saison peut se terminer avec trois boulangeries et aucun magasin de laine. Une fois ouvert, un magasin reste actif pour le reste du jeu, et l'ouverture s'arrête après 8 instances totales. La demande totale augmente de manière monotone à mesure que de nouveaux magasins s'ouvrent.

Chaque instance de magasin débloquée consomme une unité de chaque produit qu'elle demande tous les `townShopSellInterval` tours (par défaut 4). Ainsi, avec l'intervalle par défaut, un magasin demandant du blé retire 6 unités de blé du marché par jour, et deux exemplaires de ce magasin en retirent 12. Les magasins à un seul produit consomment 2x.

En outre, le centre-ville consomme une unité de chaque produit (excluant le fertilisant) tous les `townCenterSellInterval` tours (par défaut 24, c'est-à-dire une fois par jour). Ce taux est constant tout au long de la saison — il ne s'ajuste pas.

|Type de magasin|Augmente la demande pour|
| :---- | :---- |
|Boulangerie|œufs, blé|
|Pizzeria|lait, tomates, blé|
|Coin du brunch|œufs, blé, fraises|
|Magasin de laine|laine (2x)|
|Magasin de glace|fraises, lait, blé|
|Café pour animaux|carottes (2x)|
|Magasin de smoothie|fraises, lait|
|Marché des agriculteurs|blé, carottes, tomates, fraises|

<a id="market-mechanics"></a>
## Mécaniques du marché

Le marché dispose d'une quantité illimitée de semences et d'animaux à prix fixes. Les prix de vente, en revanche, varient dynamiquement selon les ressources et persistent jour après jour.

Chaque produit (et le fertilisant) commence le jeu avec une quantité de stock de `I0 = 10,000` unités, bien au-dessus de toute production réaliste dans un seul jeu, de sorte que le stock reste essentiellement positif. Le prix de vente d'un produit est de `base` à `I0`, il augmente lorsque le stock diminue (les joueurs l'achètent ou la consommation du centre-ville épuise le stock), et diminue lorsque le stock augmente (les joueurs le vendent).

<a id="selling-inventory-to-the-market"></a>
### Vente de stocks au marché

Les joueurs peuvent créer une liste de commandes de vente ou d'achat (pour une quantité quelconque) dans la liste d'actions du marché. Les commandes sont traitées simultanément entre les joueurs, une unité à la fois. Par exemple, lorsque les deux joueurs déclarent `SELL CARROT 10` en premier, nous prenons le prix actuel des carottes, nous donnons à chaque joueur ce prix pour leur première carotte, puis ajoutons 2 carottes au marché (1 provenant de chaque joueur) — ce qui peut déplacer le prix — et répétons jusqu'à ce que toutes les commandes soient terminées.

Si le prix de vente a été réduit à `$1` (le prix minimal), l'unité est toujours acquise mais n'est pas ajoutée au stock du marché, de sorte que le seuil reste sensible aux achats ultérieurs.

<a id="buying-inventory-from-the-market"></a>
### Achat de stocks au marché

Seuls les identifiants `WHEAT` et `FERTILIZER` peuvent être achetés sur le marché via `BUY_PRODUCT` (les autres produits sont vendus sur le marché mais ne sont pas rachetés). La vente est libre : tout produit, y compris le fertilisant collecté des animaux, peut être vendu via `SELL`. Deux éléments drainent l'inventaire du marché : les édifices de la ville (le centre de la ville et les magasins, qui consomment des produits gratuitement) et les ordres du joueur `BUY_PRODUCT`. Les commandes d'achat suivent la même procédure concurrente par unité que les commandes de vente. Si un joueur est dépourvu de fonds au milieu d'une commande, celle-ci est interrompue.

Le prix d'achat est indiqué à partir de l'inventaire post-achat et le prix de vente est indiqué à partir de l'inventaire pré-vente, de sorte qu'un achat immédiat suivi d'une vente du même produit contre un marché autrement inchangé donne exactement zéro.

<a id="the-price-function"></a>
### La Fonction de Prix

Pour chaque ressource, la courbe est définie par un prix de base, un débit d'ancrage `T`, et une fonction de forme indépendante **fonction de forme** + **mouvement cible** pour chaque côté de l'équilibre :

```
price(inv) = base + sign · amp · f(|inv − I0|)
  sign = +1  if inv < I0   (scarcity → price up)
  sign = −1  if inv > I0   (glut    → price down)
  amp  = target · base / f(T)        (derived; not stored)
  f    ∈ { linear, sq, sqrt, log, log10, hinge }   (log uses ln(1+x), so f(0)=0)
```

Arrondie au plus proche dollar et tronquée à `$1`.

`hinge` est la seule forme qui dépend de `T` plutôt que de `x` seul : avec `u = x / T`, elle vaut `u + 8 · max(0, u − 1)²`. En dessous de `T`, elle est linéaire en `u` ; au-dessus de `T`, le terme quadratique prend le dessus et le prix monte de façon abrupte. Puisque `f(T) = 1` est construit de manière spécifique, `target` conserve son sens habituel.

`T` est la capacité de production d'un seul champ de 5×5 sur une fenêtre de 24 jours, avec une irrigation optimale et sans engrais (les totaux animaux sont pré-remis à 30 % pour tenir compte des coûts d'alimentation du blé, et permettent une journée pour construire la coopérative ou le parcage). La fenêtre de 24 jours est un horizon de calibration, pas la durée de 30 jours de la saison. Elle est plus courte intentionnellement : les premiers jours sont très chargés en mise en place et produisent peu.

`target` indique : « déplacer `T` unités de `I0` déplace le prix de `target × base` ». Choisir des valeurs différentes de `f` et `target` sur chaque côté permet aux ressources ayant des profils de production similaires de jouer de manière très différente stratégiquement — le blé panique en cas de pénurie mais absorbe les surproductions ; le melon réagit peu à la pénurie mais s'effondre en cas de surproduction ; le laine imite le melon à une échelle réduite. Les ressources de qualité (base > $100: strawberry, melon, milk, wool) use `above_target > 1`, so even modest gluts drive them straight to the $1) — le timing des ventes et la consolidation sont plus importants pour ces ressources que pour les produits de base.

Carotte, tomate et œuf utilisent `hinge` côté pénurie, donc leurs prix restent proches de la base sous une demande ordinaire et augmentent brusquement une fois que la demande dépasse `T`. Les commerces de la ville qui les consomment sont listés dans `unlocked_shops`.

- **Carotte** — `hinge` à `below_target` 1.00. Consommée par des cafés pour animaux (produit unique, donc chaque établissement en consomme deux fois) et des marchés agricoles.
- **Tomate** — `hinge` à `below_target` 0.40. Consommée par des boutiques de pizzas et des marchés agricoles.
- **Œuf** — `hinge` à `below_target` 0.40. Consommée par des boulangeries et des lieux de petit-déjeuner.

Les tomates et les œufs conservent le paramètre `below_target` des courbes `linear` qu’ils remplacent. Puisque l’amplitude de `linear` se normalise déjà à `x / T`, ce qui correspond exactement à la branche de `hinge` située sous le point de rupture, leurs prix de `I0` à `I0 − T` restent inchangés ; les courbes ne diffèrent qu’au-delà de ce point.

|Ressource|Base|I0|T|En dessous de la fonction|En dessous de la cible|Au-dessus de la fonction|Au-dessus de la cible|P(I0−T)|P(I0+T)|P(I0+2T)|
| ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- |
|**Blé**| 25 | 10,000 | 400 |sqrt| 0.80 |log| 0.20 | $45 | $20 | $19 |
|**Carotte**| 35 | 10,000 | 450 |hinge| 1.00 |sqrt| 0.70 | $70 | $10 | $1 |
|**Tomate**| 60 | 10,000 | 200 |hinge| 0.40 |sqrt| 0.60 | $84 | $24 | $9 |
|**Fraise**| 120 | 10,000 | 100 |sqrt| 0.70 |linear| 1.60 | $204 | $1 | $1 |
|**Melon**| 250 | 10,000 | 300 |log| 0.20 |sq| 3.60 | $300 | $1 | $1 |
|**Œuf**| 50 | 10,000 | 332 |hinge| 0.40 |log| 0.20 | $70 | $40 | $39 |
|**Lait**| 160 | 10,000 | 122 |sqrt| 0.60 |linear| 1.60 | $256 | $1 | $1 |
|**Laine**| 200 | 10,000 | 105 |log| 0.20 |sq| 3.20 | $240 | $1 | $1 |
|**Fertilisant**| 100 | 10,000 | 200 |linear| 0.40 |linear| 0.40 | $140 | $60 | $20 |

Les valeurs par défaut se trouvent dans `MARKET_PARAMS` dans `kaggriculture.py`. Les surcharges par ressource (sparse : tout sous-ensemble de `base`, `I0`, `T`, `below_func`, `below_target`, `above_func`, `above_target`) peuvent être fournies lors de la création de l'épisode via `env.configuration["marketParams"]` sans modifier le code, par exemple `{"WOOL": {"above_target": 0.95}}`.

<a id="turn-processing-order"></a>
## Ordre de traitement

1. **Validation des actions** — vérifier la légalité de l'action
2. **Actions des joueurs** — enregistrer les actions effectuées par chaque joueur (qui se produisent simultanément)
3. **Actions du marché** \- traiter la file d'attente du marché selon l'ordre des joueurs (décris ci-dessus)
4. **Actions d'achat au centre de ville** \- le centre de ville et les magasins réduisent leur stock
5. **Mise à jour des observations**
   - **Rafraîchissement du jour** — si applicable, mettre à jour l'état des plantes et des animaux pour un nouveau jour, et réinitialiser leur état alimenté/arroser à faux
   - **Rafraîchissement du marché** — modifier le prix des articles sur le marché en fonction des ventes de la dernière étape
   - **Mise à jour des revenus** — mettre à jour le compte bancaire du joueur en fonction des achats ou ventes effectués
   - **Mise à jour de la ferme** — effacer les plantes récoltées, les articles du stock utilisés ou vendus, ajouter de nouvelles plantes/animaux à la ferme, etc

<a id="win-conditions"></a>
## Conditions de victoire

La condition de victoire est simple : celui qui a le plus de pièces à la fin de la saison gagne. Il est également possible que les deux joueurs se partagent la victoire.

<a id="reward"></a>
## Récompense

Le joueur qui a le plus d'argent dans son compte bancaire à la fin du jeu gagne. Les articles non vendus dans le stock ne sont pas comptabilisés dans ce total.

<a id="observation-format"></a>
## Format des observations

L'observation principale transmise à chaque agent :

```py
{
  "player": int,           # 0 or 1
  "day":    int,           # 0-indexed in-game day
  "hour":   int,           # 0-indexed turn within the day
  "farms":  [farm, farm],  # public per-player state, indexed by player id (shared)
  "market": {              # shared
    "inventory": { "WHEAT": int, "CARROT": int, ... },
    "prices":    { "WHEAT": int, "CARROT": int, ... },
  },
  "town": {                # shared
    "unlocked_shops": ["BAKERY", "BAKERY", ...],   # may repeat; each entry consumes independently
  },
  "private": {             # this player only; opponent's private state is not visible
    "shed":        { "WHEAT": int, "GOOSE": int, "FERTILIZER": int, ... },
    "seeds":       { "WHEAT": int, "CARROT": int, ... },
    "inventories": [farmer_inv, hand_inv, ...],  # [0] is the main farmer
  },
}
```

Chaque `farm` dict (public, visible aux deux joueurs) :

```py
{
  "money":              float,
  "tiles":              [[tile, ...], ...],   # tiles[y][x]
  "farmer":             [x, y],
  "hands":              [[x, y], ...],         # hired hands for the current day
  "unlocked_quadrants": ["NW", ...],          # subset of {"NW","NE","SW","SE"}
  "hires_today":        int,                  # used to price the next HIRE
}
```

Un `tile` est l'un de :

- `None` — case vide non débloquée
- `"LOCKED"` — case dans un quadrant que le joueur n'a pas encore acheté
- un dictionnaire de plante :
  ```py
  {
    "kind":                 "PLANT",
    "crop":                 "WHEAT" | "CARROT" | "TOMATO" | "STRAWBERRY" | "MELON",
    "planted_day":          int,
    "watered_today":        bool,   # reset to False each end-of-day
    "consecutive_unwatered": int,   # 2+ → tile turns to a weed
    "yield_units":          int,    # units currently harvestable
    "max_lifespan_step":    int,    # step at which decay begins; -1 for ongoing crops
    "fertilized_until_day": int,    # last day fertilizer bonus applies; -1 if none
  }
  ```
- un dictionnaire de mauvaise herbe : `{"kind": "WEED"}`
- un dictionnaire de structure animale (coopérative/pâturage, facultativement occupée) :
  ```py
  {
    "kind":                 "COOP" | "PASTURE",
    "animal":               "GOOSE" | "COW" | "SHEEP" | None,  # None until PLACEd
    "placed_day":           int,
    "yield_units":          int,
    "fed_today":            bool,
    "consecutive_unfed":    int,    # 2+ → animal escapes
    "cared_today":          bool,
    "fertilizer_available": bool,   # set at end-of-day for every surviving animal; cleared by COLLECT_FERTILIZER
    "pending_care_bonus":   int,    # banked CARE bonus, applied on the next yield tick
  }
  ```

<a id="quick-start"></a>
## Démarrage rapide

```py
from kaggle_environments import make


def my_agent(obs):
    # Buy one wheat seed on the very first turn, then PASS forever after.
    if obs.get("step", 0) == 0:
        return {"farmer": ["PASS"], "market": [["BUY_SEED", "WHEAT", 1]]}
    return {"farmer": ["PASS"], "market": []}


env = make("kaggriculture", configuration={"episodeSteps": 200})
env.run([my_agent, "random"])
env.render(mode="ipython", width=800, height=800)
```

<a id="configuration-defaults"></a>
## Paramètres par défaut

Les coûts par semence par culture et les prix de base par produit ne sont pas configurables ; ils sont documentés dans les tables des types d'objets et des fonctions de prix ci-dessus. Les paramètres configurables sont :

|Paramètre|Valeur par défaut|Description|
| :---- | :---- | :---- |
|episodeSteps| 720 |Nombre total de tours de la saison (24 tours × 30 jours)|
|tailleDuPlateau| 10 |Largeur et hauteur (en cases) de chaque ferme de chaque joueur. Utilisations avancées : 10 = quatre quadrants de 5x5|
|argentDeDepart| 3000 |Pièces que chaque joueur commence avec|
|maxCommandesMarcheParTour| 10 |Nombre maximum de commandes de marché traitées par joueur par tour ; les excédents sont silencieusement ignorés|
|joursParJour| 24 |Nombre de tours qui composent une journée dans le jeu|
|capaciteDeLaGrange| 100 |Nombre maximum d'éléments non semés que peut contenir la grange ; les excédents à la fin du jour sont éliminés|
|probabiliteDeNaissanceDeHerbe| 0.005 |Probabilité par case d'apparition d'une herbe sur une case vide et non verrouillée lors du rafraîchissement à la fin du jour|
|intervalleDeDeverouillageDuMagasinDeVille| 3 |Jours entre deux déverouillages successifs du magasin de ville (répétition avec remise, limite à 8 occurrences)|
|intervalleDeVenteDuMagasinDeVille| 4 |Tours entre les ticks de consommation de chaque instance déverouillée du magasin de ville|
|intervalleDeVenteDuCentreDeVille| 24 |Tours entre les ticks de consommation du centre de ville (taux fixe, une fois par jour)|
|semence|null|Semi-entrée optionnelle pour générer de manière déterministe une épreuve ; supprimée de la configuration après lecture afin de ne pas figurer dans les observations de l'agent|
