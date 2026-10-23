[English](game_mechanics_reference.md) | [Français](game_mechanics_reference.fr.md) | [简体中文](game_mechanics_reference.zh-CN.md)

[README du projet](../README.fr.md)

<a id="kaggriculture--game-mechanics-reference"></a>
# Kaggriculture — Référentiel mécaniques de jeu

Référence rapide des mécaniques principales, des coûts, des taux de production, du comportement du marché et des contraintes utiles au développement d'agents.

---

<a id="1-production"></a>
## 1. Production

Pour les cultures, **Rendement / Case / Jour** est le nombre total d'unités récoltées divisé par le nombre de jours pendant lesquels la case est occupée, en supposant une irrigation quotidienne et une récolte à la rendement maximal.

Pour les animaux, c'est le taux de production stable (`1 / interval`) après la première récolte. Les animaux continuent de produire tant qu'ils survivent.

Pour les animaux, **Rendement maximal** correspond à `max_held`, la quantité maximale de produit accumulée sur la case sans récolte.

|Type|Type de rendement|Coût|Prix de base|Première récolte|Âge maximal de rendement|Récoltes successives|Rendement maximal|Coût d'action|Rendement / Case / Jour|
| ---------------- | ---------- | ---: | ---------: | ----------: | ------------: | ------------------------- | -----------------: | ------------------: | -----------------: |
|**Blé**|Unique|   10 |         25 |2 jours|4 jours|Aucun|6 (4 sans engrais)|                   1 |               0.80 |
|**Carotte**|Unique|   20 |         35 |2 jours|3 jours|Aucun|4 (3 sans engrais)|                   1 |               0.75 |
|**Tomate**|Continu|   50 |         60 |8 jours|11 jours|Chaque jour ×4|                  4 |                   1 |               0.33 |
|**Fraise**|Continu|  100 |        120 |10 jours|16 jours|Chaque deux jours ×4|                  4 |                   1 |               0.24 |
|**Melon**|Unique|   80 |        250 |10 jours|10 jours|Aucun|                  6 |                   1 |               0.55 |
|**Gosse / Œuf**|Continu|  300 |         50 |4 jours|N/A|Chaque jour indéfiniment|4 retenus|1 + 1 construire un abri|               1.00 |
|**Vache / Lait**|Continu|  400 |        160 |8 jours|N/A|Chaque 2 jours indéfiniment|6 retenus|1 + 1 construire un parc|               0.50 |
|**Mouton / Laine**|Continu|  500 |        200 |6 jours|N/A|Chaque 3 jours indéfiniment|6 retenus|1 + 1 construire un parc|               0.33 |
|**Engrais**|N/A|  100 |X|N/A|N/A|N/A|N/A|                   1 |N/A|

<a id="crop-specifics"></a>
### Spécificités des cultures

* **Blé :** rendement maximal de 4 sans engrais, 6 avec engrais.
* **Carotte :** rendement maximal de 3 sans engrais, 4 avec engrais.
* **Melon :** fenêtre de bonus de 6 à 12 jours. Rendement maximal de 6 à 10 jours sans engrais ou de 8 jours avec engrais.
* **Tomate :** 4 récoltes planifiées aux âges 8, 9, 10 et 11, puis elle décline progressivement en herbe sauvage.
* **Fraise :** 4 récoltes planifiées aux âges 10, 12, 14 et 16, puis elle décline progressivement en herbe sauvage.

Les plantes doivent être arrosées chaque jour. Deux jours consécutifs sans arrosage transforment une plante en **herbe sauvage**.

Une semence nouvellement plantée commence avec un jour de déséquilibre d'arrosage déjà compté, donc elle doit être arrosée le jour de plantation, sinon elle devient une mauvaise herbe à la fin de ce jour.

---

<a id="2-animals"></a>
## 2. Animaux

Les animaux doivent être nourris avec **Blé**.

Deux jours consécutifs sans nourriture font fuir l'animal de manière permanente.

Le blé peut être produit sur la ferme ou acheté au marché au prix actuel.

<a id="animal-care"></a>
### Soins des animaux

Les banques de soins accumulent un bonus pour la prochaine production planifiée.

* Un jour où un animal est à la fois nourri et soigné ajoute **+1** à son bonus de soins en attente.
* À la prochaine production planifiée, un animal nourri produit sa rendement de base plus le bonus accumulé.
* Ce bonus est ensuite réinitialisé à 0.
* Si l'animal n'est pas nourri le jour de sa production, la unité de base est produite mais le bonus accumulé est perdu.
* La production reste limitée par `max_held`.

<a id="observed-care-bonus-anomaly"></a>
### Anomalie du bonus de soins observé

Un comportement inexpliqué a été observé avec le **Canard** lors de l'optimisation des actions `CARE`.

Dans la scène testée, le canard est placé le jour 1, nourri chaque jour et récolté le jour 5 :

|Scénario|Jour 4|Production observée le jour 6|
| -------- | ----- | -------------------------: |
|Soins continus| `CARE` |2 œufs|
|Soins omis le jour 4|Aucun `CARE`|1 œuf|

Ce comportement semble incohérent avec la règle documentée sur les soins. D'après cette règle, le bonus `pending_care_bonus` doit être consommé lors de la prochaine production planifiée puis réinitialisé à 0. Puisque le canard produit chaque jour après sa première récolte, le bonus de soin du jour 4 ne devrait pas survivre à une production intermédiaire afin d'influencer le jour 6.

La cause exacte est actuellement inconnue. Des explications possibles incluent l'ordre de mise à jour de la fin de jour, de la production, de l'accumulation et de la réinitialisation du bonus de soins, ou un effet de numérotation ou de timing dans l'environnement. Jusqu'à ce que ce comportement soit entièrement expliqué, l'optimisation des soins fondée uniquement sur `pending_care_bonus` et `max_held` doit être considérée comme unsafe.

<a id="fertilizer-production"></a>
### Production de fertilisant

Chaque animal survivant rend disponible **1 fertilisant par jour**.

Le fertilisant non ramassé **ne s'accumule pas**.

---

<a id="3-fertilizer"></a>
## 3. Fertilisant

Le fertilisant peut être produit par les animaux ou acheté au marché.

Effets importants sur les cultures :

|Culture|Sans fertilisant|Avec fertilisant|
| ---------- | ------------------ | --------------- |
|**Blé**|Max 4|Max 6|
|**Carotte**|Max 3|Max 4|
|**Melon**|Max 6 à l'âge 10|Max 6 à l'âge 8|

---

<a id="4-farm-infrastructure"></a>
## 4. Infrastructure de la ferme

<a id="land"></a>
### Terres

La ferme est divisée en 5×5 segments.

Coûts supplémentaires pour des segments supplémentaires :

|Expansion|Coût|
| --------- | ---------: |
|1er| **$1,000** |
|2e| **$2,000** |
|3e| **$4,000** |
|**Total**| **$7,000** |

<a id="shed"></a>
### Étable

Capacité maximale : **100 éléments non-sémi**.

Les graines ne comptent pas dans cette limite.

---

<a id="5-farm-hands"></a>
## 5. Ouvriers de la ferme

Les ouvriers agricoles sont des travailleurs temporaires embauchés pour une seule journée.

Leur coût suit la suite de Fibonacci :

`cost = farmHandCostMult × fib(n)`

où `n` est le nombre d'ouvriers agricoles déjà embauchés durant la journée en cours.

Avec la valeur par défaut `farmHandCostMult = 1` :

|Ouvrier agricole|Coût|
| --------: | -----: |
|1er|  **1** |
|2e|  **1** |
|3e|  **2** |
|4e|  **3** |
|5e|  **5** |
|6e|  **8** |
|7e| **13** |
|8e| **21** |
|9e| **34** |
|10e| **55** |

La séquence de coût d'embauche **se réinitialise au début de chaque jour**.

---

<a id="6-town-shops"></a>
## 6. Établissements de la ville

De nouveaux établissements s'ouvrent tous les **3 jours**, avec remplacement, jusqu'à **8 exemplaires actifs**.

Chaque établissement consomme ses produits demandés tous les **4 tours**, soit **6 unités par produit par jour**. Les établissements à un seul produit marqués ×2 consomment **12 unités par jour**.

|Type d'établissement|Augmente la demande pour|
| --- | --- |
|**Boulangerie**|Œufs, blé|
|**Pizzeria**|Lait, tomates, blé|
|**Coin du petit-déjeuner**|Œufs, blé, fraises|
|**Magasin de laine**|Laine ×2|
|**Magasin de glace**|Fraises, lait, blé|
|**Café pour animaux**|Carottes ×2|
|**Magasin de smoothie**|Fraises, lait|
|**Marché des agriculteurs**|Blé, carottes, tomates, fraises|

Les instances multiples du même établissement cumulent leurs demandes.

---

<a id="7-market-prices"></a>
## 7. Prix du marché

Pour la calcul complète des prix et les définitions des courbes de marché, voir la [Fonction de prix](game_rules.fr.md#the-price-function)

<a id="market-inventory"></a>
### Inventaire du marché

`inventory` représente la **stock global du marché d'un ressource**, et non la quantité stockée sur une ferme du joueur.

L'inventaire du marché évolue lorsque des produits entrent ou quittent le marché :

* Les produits vendus par les joueurs **augmentent** l'inventaire du marché.
* Les produits achetés au marché **diminuent** l'inventaire du marché.
* La consommation des établissements de la ville **diminue** l'inventaire du marché.
* L'inventaire du marché persiste tout au long du jeu.

Comportement général :

* `inventory < I0` → pénurie → **prix augmente**
* `inventory = I0` → équilibre → **prix de base**
* `inventory > I0` → surabondance → **prix diminue**
* Prix minimal du marché → **$1**

Plus l'inventaire s'éloigne de `I0`, plus le prix varie selon la courbe spécifique du marché de la ressource.

<a id="market-behavior-summary"></a>
### Résumé du comportement du marché

|Ressource|Pénurie|Surabondance|Comportement clé|
| -------------- | --------------------------------- | ----------------------- | --------------------------------- |
|**Blé**|Augmentation rapide au début|Diminution lente|Résistant à la surabondance|
|**Carotte**|Accélère sous forte pénurie|Diminution rapide|Potentiel de pénurie forte|
|**Tomate**|Accélère sous forte pénurie|Diminution rapide|Potentiel de rareté élevé|
|**Fraise**|Augmentation rapide|Diminution très rapide|Très sensible à un excès d'offre|
|**Melon**|Augmentation lente|Diminution extrêmement rapide|Très sensible à un excès d'offre|
|**Oeuf**|Accélère sous un fort manque|Diminution lente|Résistante à un excès d'offre|
|**Lait**|Augmentation rapide|Diminution très rapide|Très sensible à un excès d'offiad|
|**Laine**|Augmentation lente|Diminution extrêmement rapide|Très sensible à un excès d'offre|
|**Fertilisant**|Augmentation régulière|Diminution régulière|Prévisible|

Pour **Carotte, Tomate et Oeuf**, les prix peuvent augmenter brusquement lorsque la rareté du marché devient significative.

Pour **Fraise, Melon, Lait et Laine**, un excès d'offre peut rapidement pousser le prix du marché vers le **sol $1**.

<a id="market-price-curves"></a>
### Courbes de prix du marché

![Market price curves](../images/market_price_curves.png)

---

<a id="8-key-constraints"></a>
## 8. Contraintes clés

|Mécanique|Contrainte|
| --------------------- | -------------------------------------------------------------------- |
|**Plantes**|Deux jours consécutifs sans eau → herbe|
|**Animaux**|Deux jours consécutifs sans blé → perdu définitivement|
|**Fertilisant animal**|1 disponible par animal survivant par jour ; ne s'accumule pas|
|**Soins des animaux**|Les jours de nourriture et de soins accumulent un bonus pour la production suivante|
|**Production des animaux**|La production non récoltée est limitée par `max_held`|
|**Étable**|Maximum 100 éléments non semés|
|**Terre**|Les expansions coûtent $1,000 → $2,000 → $4,000|
|**Produits premium**|Fraise, Melon, Lait et Laine sont très vulnérables à un excès d'offre|
|**Produits pivot**|Carotte, Tomate et Oeuf peuvent augmenter brusquement sous forte rareté|
|**Magasins de la ville**|La composition des magasins modifie directement la demande|
