[English](learning_agent.md) | [Français](learning_agent.fr.md) | [简体中文](learning_agent.zh-CN.md)

[README du projet](../README.fr.md)

<a id="learning-agent"></a>
# Agent d'apprentissage

<a id="1-objective"></a>
## 1. Objectif

L'agent d'apprentissage est une alternative expérimentale à l'agent heuristique déterministe.

L'objectif est d'apprendre des décisions stratégiques à partir d'agents performants de Kaggriculture tout en conservant une exécution déterministe pour les actions de base de ferme et les trajectoires.

L'architecture est hybride :

```text
Game observation
       |
       v
Learning policy
       |
       v
Strategic decisions
       |
       v
Deterministic executor
       |
       v
Legal Kaggriculture actions
```

La politique d'apprentissage est responsable de la stratégie. L'exécuteur déterministe reste responsable de l'exécution de ces décisions de manière sûre et efficace.

<a id="2-approach"></a>
## 2. Approche

La pipeline d'apprentissage est divisé en deux étapes principales :

1. Apprentissage par imitation
2. Apprentissage par renforcement

L'apprentissage par comportement est d'abord utilisé pour apprendre à partir d'agents existants performants. L'apprentissage par renforcement peut ensuite affiner la politique apprise grâce à l'interaction avec l'environnement Kaggriculture.

Un apprentissage pur par renforcement à partir de zéro peut être évalué ultérieurement comme référence, mais ce n'est pas l'approche principale.


<a id="3-expert-replays"></a>
## 3. Replays d'experts

Les démonstrations d'experts sont collectées à partir de soumissions d'agents de haut niveau sur le classement Kaggle.

Le téléchargeur suit l'hiérarchie de la compétition de simulation Kaggle :

```text
Leaderboard
    |
    v
Top N teams
    |
    v
Best submission
    |
    v
Episodes
    |
    v
Replay JSON
```

Les reprises sont stockées par l'identifiant stable de l'équipe Kaggle au lieu du classement du classement :

```text
data/
└── expert_replays/
    ├── metadata.json
    ├── team_<team_id>/
    │   ├── <episode_id>.json
    │   └── ...
    └── ...
```

Cela évite d'associer des dossiers de reprises anciens à l'équipe erronée lorsque les classements du classement changent.

Exemple :

```bash
python scripts/download_replays.py --top 10 --episodes 40
```

Les fichiers de reprise existants sont sautés afin de pouvoir reprendre une téléchargement interrompu.

L'ensemble de données des reprises peut être étendu sans modifier le pipeline d'apprentissage. Les statistiques de l'ensemble de données doivent être régénérées avec :

```bash
python scripts/analyze_replays.py
```

<a id="4-replay-dataset"></a>
## 4. Ensemble de données des reprises

`src/learning/replay_dataset.py` lit les fichiers bruts de reprise.

Les reprises Kaggle stockent l'action associée à l'observation précédente. L'alignement correct d'apprentissage est donc :

```text
observation[t]
      |
      v
action[t + 1]
```

Ce décalage temporel est nécessaire pour que le modèle apprenne l'action sélectionnée à partir de l'observation correspondante.

L'expert est identifié à l'aide de `metadata.json` et des noms d'équipes de reprise au lieu de supposer que le joueur ayant la récompense finale la plus élevée est l'expert.

Les fichiers de reprise sont lus de manière récursive à partir du répertoire de reprise des experts.

L'identifiant d'épisode est conservé pour chaque échantillon afin de permettre de séparer l'entraînement et la validation par des épisodes complets.

Le chargement des reprises est en flux. Les reprises sont traitées une par une au lieu de stocker toutes les observations et actions décodées en mémoire. Cela rend le prétraitement scalable à des ensembles de reprises considérablement plus grands.

<a id="5-state-encoding"></a>
## 5. Encodage de l'état

`src/learning/state_encoder.py` convertit une observation brute de Kaggriculture en un vecteur de caractéristiques numérique fixe.

L'état actuel contient 107 caractéristiques couvrant :

- jour et heure ;
- argent ;
- ouvriers embauchés ;
- terres débloquées ;
- contenus du bâtiment ;
- semences disponibles ;
- produits transportés ;
- inventaire du marché ;
- prix du marché ;
- magasins débloqués ;
- état de la production des cultures ;
- état de la production des animaux ;
- état de l'arrosage ;
- état de l'alimentation ;
- état de soin ;
- état de fertilisation.

Les caractéristiques de quantités non négatives importantes utilisent le scaling `log1p` pour réduire les écarts de magnitude entre de petites et de grandes quantités de stocks ou de productions.

Les jours et les heures sont normalisés. Les stocks de marché sont représentés par rapport à leurs stocks de base et les prix de marché par rapport à leurs prix de base.

Les positions des tuiles ne sont pas actuellement encodées individuellement. La production est regroupée par type de culture et d'animal car l'exécution spatiale fine reste la responsabilité de l'exécuteur déterministe.

Le premier modèle d'apprentissage exclut intentionnellement l'état de l'adversaire. Le modèle d'adversaire est réservé pour une variante ultérieure après que l'agent d'apprentissage de base ait été optimisé.

<a id="6-decision-extraction"></a>
## 6. Extraction des décisions

`src/learning/decision_extractor.py` convertit les actions expertes brutes en décisions stratégiques.

Les décisions stratégiques actuelles incluent :

```text
HIRE
BUY_LAND
BUY_SEED
BUY_ANIMAL
BUY_PRODUCT
SELL
PLANT
PLACE
FERTILIZE
BUILD_COOP
BUILD_PASTURE
```

Les actions d'exécution à bas niveau sont intentionnellement exclues :

```text
NORTH
SOUTH
EAST
WEST
PASS
PICKUP
DROP
WATER
FEED
CARE
HARVEST
COLLECT_FERTILIZER
```

Ces actions restent la responsabilité de l'exécuteur déterministe.

Les quantités de marché et les compteurs d'actions des ouvriers sont conservés. Les demandes excessives invalides de `SELL` trouvées dans certains actions de reprise sont limitées à la quantité effectivement disponible dans le bâtiment.

<a id="7-replay-analysis"></a>
## 7. Analyse de reprise

`scripts/analyze_replays.py` analyse l'ensemble d'experts avant la formation.

Il rapporte :

- nombre de reprises ;
- nombre d'échantillons utilisables ;
- échantillons invalides ;
- équipes d'experts représentées ;
- fréquence de chaque décision stratégique ;
- distributions de quantités ;
- décisions stratégiques par jour ;
- décisions stratégiques par heure ;
- observations sans décision stratégique.

Exécution :

```bash
python scripts/analyze_replays.py
```

Les actions stratégiques se produisent fréquemment assez à chaque tick pour préserver la résolution temporelle initiale.

La représentation sélectionnée est donc au niveau du tick :

```text
observation at tick t
        |
        v
strategic decisions selected from tick t
```

Plusieurs décisions stratégiques peuvent se produire durant le même tick.

Les ticks sans décisions stratégiques sont conservés car ils enseignent la politique lorsqu'il ne faut pas initier une nouvelle action stratégique.

<a id="8-learning-targets"></a>
## 8. Cibles d'apprentissage

`src/learning/target_encoder.py` convertit les décisions stratégiques extraites en cibles adaptées à l'apprentissage par imitation.

Cinq groupes de cibles sont actuellement utilisés.

<a id="hire"></a>
### Embauche

L'embauche est représentée comme une cible de régression :

```text
log1p(number_of_hires)
```

La prédiction est convertie en un nombre entier d'embauches lors de l'inférence.

Cela évite de traiter les compteurs d'embauches voisins comme des classes complètement indépendantes.

<a id="purchase-bundle"></a>
### Acheter un ensemble

Les décisions d'achat sont représentées conjointement au lieu de cibles binaires indépendantes.

Les actions d'achat sont :

```text
BUY_LAND
BUY_SEED_WHEAT
BUY_SEED_CARROT
BUY_SEED_TOMATO
BUY_SEED_STRAWBERRY
BUY_SEED_MELON
BUY_ANIMAL_GOOSE
BUY_ANIMAL_COW
BUY_ANIMAL_SHEEP
BUY_PRODUCT_WHEAT
BUY_PRODUCT_FERTILIZER
```

Les 11 indicateurs d'achat sont encodés sous forme de masque binaire :

```text
2^11 = 2048 possible purchase bundles
```

Un ensemble catégoriel d'achat empêche la politique d'associer indépendamment des modes d'achat incompatibles qui n'ont jamais été combinés dans les trajectoires d'experts.

<a id="occurrence"></a>
### Occurrence

Les décisions stratégiques non d'achat sont représentées avec des cibles binaires d'occurrence indépendantes.

Exemples :

```text
plant_WHEAT
place_COW
fertilize
build_pasture
sell_WHEAT
```

Plusieurs décisions d'occurrence peuvent être actives durant la même étape.

<a id="quantity"></a>
### Quantité

Les actions utilisant des quantités utilisent :

```text
log1p(quantity)
```

La perte de quantité est évaluée uniquement lorsque l'action correspondante est active.

<a id="sell-ratio"></a>
### Ratio de vente

Les quantités de ventes sont représentées par rapport à l'inventaire disponible à vendre :

```text
sell_ratio = sold_quantity / available_quantity
```

Cela permet à la politique de distinguer les ventes partielles des liquidations complètes sans dépendre de la taille absolue de l'inventaire.

Ce ratio est borné à :

```text
0 <= sell_ratio <= 1
```

<a id="9-behavioral-cloning-dataset"></a>
## 9. Ensemble de données de clonage comportemental

`src/learning/bc_dataset.py` combine l'encodage de l'état et l'encodage cible.

Chaque échantillon de formation contient :

```text
state
hire
purchase_bundle
occurrence
quantity
quantity_mask
sell_ratio
sell_mask
episode
```

Les pertes de quantité et de vente sont masquées afin que les décisions inactives ne contribuent pas à leurs pertes de régression.

La formation et la validation sont divisées par épisode complet plutôt que par étapes aléatoires :

```text
episode A -> train
episode B -> train
episode C -> validation
```

Les étapes d'un même replay ne peuvent donc pas apparaître à la fois dans la formation et la validation.

Cela empêche une fuite temporelle entre observations fortement corrélées et voisines.

Pour de grands ensembles de replay, `scripts/preencode_bc.py` construit un ensemble tensoriel pré-encodé :

```text
data/processed/bc_dataset.pt
```

La chaîne de prétraitement effectue deux passages en continu :

```text
pass 1 -> count valid samples
pass 2 -> encode samples directly into preallocated tensors
```

Cela maintient l'utilisation mémoire du JSON du replay bornée tout en préservant le format tensoriel final utilisé pour la formation.

<a id="10-behavioral-cloning-model"></a>
## 10. Modèle de clonage comportemental

`src/learning/model.py` implémente la politique stratégique.

Le modèle utilise un MLP partagé :

```text
107 state features
        |
        v
Linear(107, 256)
ReLU
LayerNorm
Dropout
        |
        v
Linear(256, 256)
ReLU
LayerNorm
        |
        +-----------+------------------+------------------+------------------+------------------+
        |           |                  |                  |                  |
        v           v                  v                  v                  v
      Hire      Purchase bundle     Occurrence         Quantity          Sell ratio
   regression     2048 classes      multi-label       regression         regression
```

Le modèle reste intentionnellement compact.

Les têtes de sortie sont :

- `hire` : sortie de régression scalaire ;
- `purchase_bundle` : 2048 logits catégoriels ;
- `occurrence` : un logit par décision stratégique restante ;
- `quantity` : une valeur de régression par cible de quantité ;
- `sell_ratio` : une valeur de régression par cible de vente.

<a id="11-behavioral-cloning-training"></a>
## 11. Formation du clonage comportemental

`scripts/train_bc.py` forme la politique stratégique à partir de l'ensemble pré-encodé.

La configuration de base utilise :

```text
Train / validation split: 80% / 20% by episode
Batch size: 512
Hidden size: 256
Learning rate: 1e-3
```

Le nombre d'époques est configurable :

```bash
python scripts/train_bc.py --epochs 50
```

Les pertes actuelles sont :

```text
hire            -> SmoothL1Loss
purchase bundle -> CrossEntropyLoss
occurrence      -> BCEWithLogitsLoss
quantity        -> masked SmoothL1Loss
sell ratio      -> masked SmoothL1Loss
```

La formation actuelle ne utilise pas le poids par fréquence inverse. Des pertes pondérées antérieures ont causé une sur-prédiction des actions stratégiques rares.

Un clipping des gradients est appliqué pendant la formation.

Le checkpoint de validation le meilleur est stocké comme :

```text
models/bc_best.pt
```

Un mode de fumée est également disponible :

```bash
python scripts/train_bc.py --smoke
```

<a id="12-evaluation-metrics"></a>
## 12. Métriques d'évaluation

`scripts/evaluate_bc.py` évalue le checkpoint de clonage comportemental le meilleur.

L'évaluation rapporte :

- MAE de l'emploi log ;
- MAE du nombre d'emplois ;
- précision exacte de l'emploi ;
- précision globale du bundle d'achat ;
- précision du bundle d'achat par classe ;
- précision, rappel et F1 par décision d'occurrence ;
- F1 micro d'occurrence ;
- F1 macro d'occurrence ;
- MAE de la quantité ;
- MAE du ratio de vente ;
- seuils optimisés d'occurrence.

Le modèle des 50 dernières époques a atteint :

```text
Hire count MAE: 0.0736
Hire exact accuracy: 0.950
Purchase bundle accuracy: 0.904
Occurrence micro F1 @ 0.5: 0.554
Occurrence macro F1 @ 0.5: 0.549
Occurrence macro F1 with calibrated thresholds: 0.611
```

Les seuils optimisés d'occurrence sont stockés dans :

```text
models/bc_thresholds.json
```

Ces seuils doivent rester associés au checkpoint utilisé pour les générer.

<a id="13-autonomous-hybrid-agent"></a>
## 13. Agent hybride autonome

`src/agents/bc_agent.py` intègre la politique stratégique apprise avec une exécution déterministe.

La chaîne autonome est :

```text
Observation
     |
     v
State encoder
     |
     v
BC policy
     |
     +---------------------------+
     |                           |
     v                           v
Market / workforce          Production intent
     |                           |
     +-------------+-------------+
                   |
                   v
        Deterministic executor
                   |
                   v
      Worker allocation / pathing
                   |
                   v
          Kaggriculture action
```

Le modèle appris détermine l'intention stratégique. L'exécuteur gère les mécanismes qui doivent rester déterministes, y compris le déplacement, les opérations de prise et de pose, l'arrosage, l'alimentation, les soins, la récolte, la collecte de fertilisants, l'affectation des tâches aux ouvriers et les contraintes juridiques.

L'exécuteur protège également la politique apprise contre des actions invalides ou physiquement impossibles.

L'agent autonome est évalué séparément de la validation en mode hors ligne car de petites erreurs de prédiction peuvent conduire la politique à des états non bien représentés dans les trajectoires expertes.

<a id="14-closed-loop-evaluation"></a>
## 14. Évaluation en boucle fermée

Les métriques de clonage comportemental hors ligne sont nécessaires mais ne sont pas suffisantes pour mesurer la performance autonome.

Pendant la partie autonome :

```text
prediction error
      |
      v
different next state
      |
      v
state distribution shift
      |
      v
new prediction error
```

Ce problème d'accumulation d'erreurs explique pourquoi un modèle avec de bonnes métriques de validation peut tout de même se comporter mal dans des jeux complets de Kaggriculture.

L'agent autonome doit donc être évalué sur plusieurs parties en utilisant :

- le meilleur rendement ;
- le rendement maximal ;
- le rendement moyen ;
- la distribution du rendement ;
- le nombre total d'embauches ;
- le nombre de plantes et de récoltes ;
- les actions de non-activité des ouvriers ;
- l'inventaire final de la grange ;
- l'inventaire final des ouvriers ;
- les cultures et animaux restants ;
- les mauvaises herbes et autres cas d'échec.

L'agent heuristique déterministe reste la base de référence.

<a id="15-reinforcement-learning"></a>
## 15. Apprentissage par renforcement

Après le clonage comportemental, la politique apprise peut être affinée par apprentissage par renforcement.

L'objectif principal reste le rendement de Kaggriculture :

```text
final money
```

La séquence prévue est :

```text
Expert replays
      |
      v
Behavioral Cloning
      |
      v
Autonomous BC agent
      |
      v
Reinforcement Learning
      |
      v
Optimized learning agent
```

Un apprentissage par renforcement pur à partir de zéro peut être utilisé ultérieurement comme base de comparaison.

<a id="16-opponent-modeling"></a>
## 16. Modélisation de l'adversaire

La modélisation de l'adversaire est intentionnellement exclue de l'agent initial d'apprentissage.

L'objectif premier est de maximiser la performance de la politique de base sans dépendre d'informations sur les adversaires.

Une fois que la version optimisée est stable, deux variantes peuvent être maintenues :

```text
Base optimized agent
Base optimized agent + opponent modeling
```

Cela permet de mesurer de manière indépendante l'effet de la modélisation de l'adversaire par rapport à la stratégie principale.

<a id="17-current-status"></a>
## 17. État actuel

Implémenté et validé :

- le téléchargement de reprises expertes ;
- le stockage stable des reprises en équipe ;
- les métadonnées d'identité des experts ;
- la découverte récursive des reprises ;
- le prétraitement en continu des reprises ;
- l'alignement temporel corrigé `observation[t] -> action[t + 1]` ;
- l'encodeur d'état avec 107 caractéristiques ;
- l'extraiteur de décision stratégique ;
- l'analyse des reprises et des états ;
- la représentation d'apprentissage au niveau du tick ;
- le cible de régression d'embauche ;
- le cible de bundle d'achat conjoint ;
- les cibles de non-achat multivaluées.
- cibles de quantité ;
- cibles de vente normalisées ;
- séparation d'entraînement/validation au niveau de l'épisode ;
- ensemble de données d'apprentissage par clonage comportemental pré-encodé ;
- modèle à plusieurs têtes d'apprentissage par clonage comportemental ;
- pertes d'entraînement non pondérées et masquées ;
- sauvegarde des points de contrôle ;
- évaluation par décision ;
- calibration du seuil d'occurrence ;
- intégration de la politique BC autonome ;
- couche d'exécution déterministe ;
- tests unitaires et tests d'ombre pour la chaîne d'apprentissage.

Modèle en mode hors ligne le plus récent :

```text
Training: 50 epochs
Validation samples: 145957
Hire count MAE: 0.0736
Hire exact accuracy: 95.0%
Purchase bundle accuracy: 90.4%
Occurrence micro F1: 0.554
Occurrence macro F1: 0.549
Calibrated occurrence macro F1: 0.611
```

Décision finale :

L'agent autonome fondé sur l'apprentissage n'est pas conservé pour une future évolution. Bien que les métriques de validation hors ligne soient encourageantes, les résultats autonomes sont moins stables et inférieurs à ceux de l'agent heuristique déterministe.

L'implémentation et les résultats de l'apprentissage sont conservés comme une piste expérimentale. Le projet est désormais fermé ; aucune évolution future de l'agent d'apprentissage ou de l'agent heuristique n'est impliquée par ce document.
