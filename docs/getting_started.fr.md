[English](getting_started.md) | [Français](getting_started.fr.md) | [简体中文](getting_started.zh-CN.md)

[README du projet](../README.fr.md)

<a id="kaggriculture-getting-started"></a>
# Kaggriculture : Démarrage

Ce guide vous guide dans la création d'un agent, son test local et sa soumission à la compétition Kaggriculture sur Kaggle.

Pour les règles complètes du jeu, les tables des cultures / animaux / magasins, la fonction de prix et l'ordre de traitement des tours, consultez [game_rules.md](game_rules.fr.md).

<a id="game-overview"></a>
## Aperçu du jeu

Kaggriculture est un jeu à deux joueurs de gestion agricole. Chaque joueur gère une ferme et cherche à accumuler le plus de pièces en achetant des semences et des animaux, en plantant, en arrosant, en récoltant, en élevant des animaux, en embauchant des aides et en effectuant des échanges sur un marché dynamique au cours d'une saison fixe.

- **Ferme** — chaque joueur dispose d'un quadrillage de taille `boardSize` × `boardSize` (par défaut 10 × 10) divisé en quatre quadrants de 5 × 5. Seul le quadrant NW est débloqué au début ; les trois autres (`NE`, `SW`, `SE`) peuvent être achetés via `BUY_LAND` pour $1k / $2k / $4k respectivement
- **Solde initial** — `startingMoney` est par défaut de $3000
- **Jardinier et aides** — un jardinier principal par joueur, plus jusqu'à N aides embauchées par jour. Le coût d'embauche est `farmHandCostMult * fib(n)` où `n` est le nombre d'embauches déjà effectuées aujourd'hui ; avec la valeur par défaut `farmHandCostMult = 1`, cela fait `1, 1, 2, 3, 5, 8, 13, 21, ...` et se réinitialise au début de chaque jour. Chaque unité agit indépendamment à chaque tour
- **Cultures** — Blé, Carotte, Tomate (en cours), Fraise (en cours), Melon. Chaque culture a son propre coût de semence, sa durée de croissance, sa courbe de rendement et son prix de vente de base (voir le tableau des types d'objets dans [game_rules.md](game_rules.fr.md))
- **Bonus d'arrosage** — pour les cultures ponctuelles, l'arrosage pendant la période de bonus (commençant à `ceil(max_yield_day / 2)`) ajoute 1 unité par jour au rendement récoltable. `FERTILIZE` double ce bonus pendant 3 jours. Pour les cultures en cours, la production planifiée donne par défaut 1 unité, doublée à 2 si la culture est fertilisée et arrosée le jour même
- **Animaux** — Canard (œufs, nécessite un poulailler), Vache (lait, nécessite un prairie), Mouton (laine, nécessite un prairie). Doivent être nourris quotidiennement ; `CARE` augmente le solde de +1 par jour nourri et soigné, versé intégralement lors de la prochaine production planifiée ; `COLLECT_FERTILIZER` récolte 1 fertilisant par animal par jour. Contrairement aux cultures, les animaux produisent indéfiniment tant qu'ils sont nourris — `max_held` limite le produit non récolté sur la case, et non la production totale au fil du temps
- **Arrosage / alimentation** — les plantes doivent être arrosées et les animaux nourris quotidiennement. Deux jours consécutifs sans mise à jour à la fin de la journée transforment les plantes en mauvaises herbes et font fuir les animaux (non récupérables). La journée de plantation est comptée comme la première journée sans arrosage
- **Dégradation** — une fois une plante dépassée sa durée de vie maximale (une journée après `max_yield_day` pour les cultures ponctuelles, une journée après la limite cumulée de production pour les cultures en cours), `yield_units` diminue de 1 tous les deux tours jusqu'à 0, à ce moment-là la case devient une mauvaise herbe
- **Mauvaises herbes** — chaque case vide débloquée possède un taux de `weedSpawnChance` (par défaut 0.005) de reproduction d'une mauvaise herbe à la fin de la journée ; elles peuvent être éliminées avec `DIG`
- **Étable** — limite de stock non dédié aux semences de 100 articles. Les articles au-delà de cette limite à la fin de la journée sont éliminés. Les semences sont stockées dans leur propre emplacement (sans limite, jamais récupérées par `PICKUP` — `PLANT` les consomme directement)
- **Marché** — prix fixes pour les semences, les animaux et les commandes `BUY_PRODUCT` ; les prix de vente des produits récoltés varient dynamiquement en fonction de l'inventaire du marché. Le prix est de `base` à l'inventaire initial partagé `I0`, il augmente lorsque l'inventaire diminue et diminue lorsque l'inventaire augmente, en utilisant une fonction de forme par ressource (`linear`, `sq`, `sqrt`, ou `log`) qui peut différer d'un côté à l'autre de `I0` — ainsi, les surstocks affectent fortement les produits de qualité (fraises, melon, lait, laine), les ramenant au seuil de 1 $, tandis que les produits de base absorbent les surstocks de manière plus douce (voir le tableau de la Fonction de Prix dans [game_rules.md](game_rules.fr.md)). Seulement le blé et les engrais peuvent être rachetés via `BUY_PRODUCT` ; tous les produits peuvent être vendus via `SELL`. Chaque tour, au maximum `maxMarketOrdersPerTurn` (par défaut 10) commandes sont traitées par joueur ; les commandes en excès sont supprimées sans avertissement
- **Ville** — le centre de la ville exige toujours un produit (1 exemplaire de chaque produit non engrais tous les `townCenterSellInterval` tours, par défaut 24 — une fois par jour, constant pendant toute la saison). Des commerces supplémentaires s'ouvrent tous les `townShopUnlockInterval` jours (par défaut 3, tirés de manière uniforme au hasard **avec remise**, donc des doublons sont possibles ; limités à 8 exemplaires) ; chaque instance de commerce débloquée consomme un exemplaire de chaque produit qu'elle exige tous les `townShopSellInterval` tours (par défaut 4, les commerces uniques consomment 2×) — voir le tableau des Édifices de la Ville dans [game_rules.md](game_rules.fr.md)
- **Durée de la saison** — 24 tours par jour × 30 jours = 720 tours par défaut
- **Condition de victoire** — le plus grand nombre de pièces dans la banque à la fin de la saison ; des égalités sont possibles

<a id="your-agent"></a>
## Votre Agent

Votre agent est une fonction qui reçoit une observation et retourne un dictionnaire d'action.

**Champs d'observation**
- `player` — votre indice de joueur (0 ou 1)
- `step` — tour actuel (indexé à partir de 0 ; fourni par le cadre kaggle-environments)
- `day` — jour en jeu actuel (indexé à partir de 0)
- `hour` — tour au sein du jour (indexé à partir de 0, de 0 à `turnsPerDay`-1)
- `farms` — liste avec une entrée par joueur (public ; les deux exploitations sont visibles). Chaque entrée comporte :
  - `money` — solde bancaire actuel
  - `tiles` — tableau à deux dimensions indexé `tiles[y][x]`. Chaque case est `None` (vide débloquée), `"LOCKED"` (quadrant bloqué), un dictionnaire de végétaux (`kind="PLANT"`, `crop`, `planted_day`, `watered_today`, `consecutive_unwatered`, `yield_units`, `max_lifespan_step`, `fertilized_until_day`), un dictionnaire d'herbes (`kind="WEED"`), ou un dictionnaire de structure animale (`kind="COOP"` ou `"PASTURE"`, optionnellement avec `animal`, `placed_day`, `yield_units`, `fed_today`, `consecutive_unfed`, `cared_today`, `fertilizer_available`, `pending_care_bonus`)
  - `farmer` — position `[x, y]` du fermier principal (x = colonne, y = ligne)
  - `hands` — liste des positions `[x, y]` de tout employé engagé aujourd'hui
  - `unlocked_quadrants` — sous-ensemble de `["NW", "NE", "SW", "SE"]`
  - `hires_today` — nombre de mains embauchées jusqu'à présent aujourd'hui (détermine le coût suivant de l'EMPLOI)
- `private` — uniquement pour votre joueur ; l'état de l'adversaire est caché :
  - `shed` — `{item: count}` pour les produits récoltés, les animaux et les engrais en stock
  - `seeds` — `{crop: count}` ; les graines sont stockées dans leur propre emplacement et sont consommées directement par `PLANT`
  - `inventories` — `[main_farmer_inv, hand1_inv, ...]` ; les inventaires unitaires transportés dans le champ
- `market` — partagé :
  - `inventory` — `{product: int}` offre de marché actuelle
  - `prices` — `{product: int}` prix unitaire actuel (arrondi, plafond 1)
- `town` — partagé : `unlocked_shops` — liste des noms des magasins actuellement en fonction ; les noms peuvent se répéter (les magasins sont tirés avec remplacement) et chaque entrée est consommée de manière indépendante

**Format d'action :**

```py
{
  "farmer": [op, ...args],          # one main-farmer op this turn
  "hands":  [[op, ...args], ...],   # one op per hired hand, in hands order
  "market": [[op, ...args], ...],   # ordered list of market orders, capped at maxMarketOrdersPerTurn
}
```

Opérations du fermier / manuelles :
- Déplacement : `"NORTH"`, `"SOUTH"`, `"EAST"`, `"WEST"`, `"PASS"`. Les cases verrouillées sont passables — les unités peuvent traverser les quadrants non achetés, mais ne peuvent pas agir sur ces quadrants
- Écurie / inventaire : `"PICKUP" <item> [n]` (à partir de l'écurie), `"PLACE" <item> [n]` (place un animal sur une structure correspondante lorsqu'il se trouve sur celle-ci, ou dépose des objets dans l'écurie lorsqu'il est adjacent à celle-ci), `"DROP"` (lorsque l'écurie est adjacente, vide l'ensemble de l'inventaire dans l'écurie ; les éléments excédentaires au-delà de `shedCapacity` sont rejetés). "Adjacente à l'écurie" signifie se trouver sur l'une des quatre cases centrales : `(4,4)`, `(5,4)`, `(4,5)`, `(5,5)`. L'écurie elle-même n'est pas dans `tiles`.
- Plantes : `"PLANT" <crop>`, `"WATER"`, `"HARVEST"`, `"FERTILIZE"`
- Animaux : `"BUILD_COOP"`, `"BUILD_PASTURE"`, `"FEED"`, `"COLLECT_FERTILIZER"`, `"CARE"`
- Terrain : `"DIG"` (supprime une plante, une mauvaise herbe ou un *cooperage* ou *pâturage* vide sur la case actuelle ; une structure avec un animal sur elle ne peut pas être creusée)

Opérations du marché : `["BUY_SEED", crop, n]`, `["BUY_PRODUCT", item, n]`, `["BUY_ANIMAL", animal, n]`, `["SELL", item, n]`, `["HIRE"]`, `["BUY_LAND"]`. Les actions invalides sont des opérations sans effet.

**Exemple — Boucle du blé :**

Pour le blé (`first_yield_day = 2`, `max_yield_day = 4`), la fenêtre de récolte est les jours 2 à 4. Nous plantons, arrosions pendant cette fenêtre, et récoltons à partir du jour 2.

```python
def agent(obs):
    player = obs["player"]
    me = obs["farms"][player]
    private = obs["private"]
    fx, fy = me["farmer"]
    tile = me["tiles"][fy][fx]

    market = []
    if private["seeds"].get("WHEAT", 0) == 0 and me["money"] >= 10:
        market.append(["BUY_SEED", "WHEAT", 1])
    # Sell any wheat sitting in the shed.
    wheat_in_shed = private["shed"].get("WHEAT", 0)
    if wheat_in_shed > 0:
        market.append(["SELL", "WHEAT", wheat_in_shed])

    if tile is None and private["seeds"].get("WHEAT", 0) > 0:
        return {"farmer": ["PLANT", "WHEAT"], "hands": [], "market": market}
    if isinstance(tile, dict) and tile.get("kind") == "PLANT":
        crop_age = obs["day"] - tile["planted_day"]
        if crop_age >= 2:  # WHEAT first_yield_day = 2; harvest as soon as possible
            return {"farmer": ["HARVEST"], "hands": [], "market": market}
        if not tile["watered_today"]:
            return {"farmer": ["WATER"], "hands": [], "market": market}

    return {"farmer": ["PASS"], "hands": [], "market": market}
```

Pour un exemple plus complet (et les détails par culture sur rendement et coût pour la carotte, le tomate, la fraise et le melon), consultez les sections Types d'objets et Démarrage rapide dans [game_rules.md](game_rules.fr.md).

<a id="test-locally"></a>
## Tester localement

Installez l'environnement depuis PyPI (n'importe quelle version récente incluant Kaggriculture) :

```bash
pip install -U kaggle-environments
```

Exécutez un jeu depuis Python ou un notebook — vous pouvez passer directement des fonctions d'agent ou des chemins vers les fichiers `.py` :

```python
from kaggle_environments import make

env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=True)
env.run([agent, "random"])  # or env.run(["main.py", "random"]) to load from a file

# View result
final = env.steps[-1]
for i, s in enumerate(final):
    print(f"Player {i}: reward={s.reward}, status={s.status}")

# Render in a notebook
env.render(mode="ipython", width=1200, height=800)

# Or dump a replay JSON for the visualizer / offline analysis
import json
with open("replay.json", "w") as f:
    json.dump(env.toJSON(), f)
```

Trois agents intégrés sont disponibles par nom : `"pass"`, `"random"` et `"starter"` (un baseline déterministe).

<a id="set-up-the-kaggle-cli"></a>
## Configurer le CLI Kaggle

Installez le CLI :

```bash
pip install kaggle
```

Vous aurez besoin d'un compte Kaggle — inscrivez-vous à https://www.kaggle.com si vous n'avez pas encore de compte. Ensuite, téléchargez vos identifiants API à https://www.kaggle.com/settings/api en cliquant sur **"Générer un nouveau token"** dans la section "API".

**Recommandé : fichier de token API.** Enregistrez la chaîne de token dans `~/.kaggle/access_token` :

```bash
mkdir -p ~/.kaggle
# Paste the token from the Kaggle settings UI into this file
nano ~/.kaggle/access_token
chmod 600 ~/.kaggle/access_token
```

Méthodes d'authentification alternatives :
- **OAuth (flux de navigateur) :** `kaggle auth login`
- **Variable d'environnement :** `export KAGGLE_API_TOKEN=xxxxxxxxxxxxxx`

Vérifiez que le CLI est correctement configuré :

```bash
kaggle competitions list -s "kaggriculture"
```

<a id="find-the-competition"></a>
## Trouver la compétition

```bash
kaggle competitions list -s "kaggriculture"
kaggle competitions pages kaggriculture
kaggle competitions pages kaggriculture --content
```

<a id="accept-the-competition-rules"></a>
## Accepter les règles de la compétition

Avant de soumettre, vous **devez** accepter les règles sur le site Kaggle. Navigez vers `https://www.kaggle.com/competitions/kaggriculture` et cliquez sur **"Rejoindre la compétition"**.

Vérifiez que vous avez rejoint :

```bash
kaggle competitions list --group entered
```

<a id="download-competition-data"></a>
## Télécharger les données de la compétition

```bash
kaggle competitions download kaggriculture -p kaggriculture-data
```

<a id="submit-your-agent"></a>
## Soumettre votre agent

Votre soumission doit contenir un `main.py` au niveau racine avec une fonction `agent`.

**Agent unique dans un fichier :**

```bash
kaggle competitions submit kaggriculture -f main.py -m "Wheat loop v1"
```

**Agent multi-fichier** — regroupe dans un tar.gz avec `main.py` à la racine :

```bash
tar -czf submission.tar.gz main.py helper.py model_weights.pkl
kaggle competitions submit kaggriculture -f submission.tar.gz -m "Multi-file agent v1"
```

**Soumission de notebook** :

```bash
kaggle competitions submit kaggriculture -k YOUR_USERNAME/kaggriculture-agent -f submission.tar.gz -v 1 -m "Notebook agent v1"
```

<a id="monitor-your-submission"></a>
## Surveiller votre soumission

Vérifier l'état de soumission :

```bash
kaggle competitions submissions kaggriculture
```

Notez l'ID de soumission dans la sortie — vous l'aurez besoin pour les épisodes.

<a id="list-episodes"></a>
## Liste des épisodes

Une fois que votre soumission a joué quelques parties :

```bash
kaggle competitions episodes <SUBMISSION_ID>
```

Sortie CSV pour scripting :

```bash
kaggle competitions episodes <SUBMISSION_ID> -v
```

<a id="download-replays-and-logs"></a>
## Télécharger les reprises et les journaux

Télécharger le JSON de la reprise d'un épisode (pour visualisation ou analyse) :

```bash
kaggle competitions replay <EPISODE_ID>
kaggle competitions replay <EPISODE_ID> -p ./replays
```

Télécharger les journaux de l'agent pour déboguer le comportement de votre agent :

```bash
# Logs for the first agent (index 0)
kaggle competitions logs <EPISODE_ID> 0

# Logs for the second agent (index 1)
kaggle competitions logs <EPISODE_ID> 1 -p ./logs
```

<a id="check-the-leaderboard"></a>
## Vérifier le classement

```bash
kaggle competitions leaderboard kaggriculture -s
```

<a id="typical-workflow"></a>
## Workflow typique

```bash
# Test locally
python -c "
from kaggle_environments import make
env = make('kaggriculture', debug=True)
env.run(['main.py', 'random'])
print([(i, s.reward) for i, s in enumerate(env.steps[-1])])
"

# Submit
kaggle competitions submit kaggriculture -f main.py -m "v1"

# Check status
kaggle competitions submissions kaggriculture

# Review episodes
kaggle competitions episodes <SUBMISSION_ID>

# Download replay and logs
kaggle competitions replay <EPISODE_ID>
kaggle competitions logs <EPISODE_ID> 0

# Check leaderboard
kaggle competitions leaderboard kaggriculture -s
```
