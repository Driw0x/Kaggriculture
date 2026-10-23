[English](public_agent.md) | [Français](public_agent.fr.md) | [简体中文](public_agent.zh-CN.md)

[README du projet](../README.fr.md)

<a id="public-agents"></a>
# Agents publics

Ce document regroupe uniquement les agents Kaggriculture appartenant à la ligne dérivée ou de référence publique conservée dans le référentiel.

Le numéro ci-dessous correspond au numéro d'identification utilisé dans ce fichier. Les noms d'origine des fichiers sont conservés pour la traçabilité et la reproductibilité.

<a id="alias-mapping"></a>
## Carte d'alias

|Agent public|Nom original|Artefact original|Rôle|
| --- | --- | --- | --- |
|Agent public 1|CHI11| `src/agents/chi11.py` |CHI10 + couche publique-meta|
|Agent public 2|Ye| `src/agents/ye.py` |Référence publique V58 conservée|
|Agent public 3|Ye1| `src/agents/ye1.py` |Exécution renforcée V58|
|Agent public 4|Jet| `src/agents/jet.py` |Base de route publique V27 lisible|
|Agent public 5|Jet1| `src/agents/jet1.py` |Isolation de secours + liquidation terminale|
|Agent public 6|Jet2| `src/agents/jet2.py` |Couche de préemption de vente dans l'état public|
|Agent public 7|Jet3| `src/agents/jet3.py` |Sous-système d'Agent public 3 + corrections terminales|
|Agent public 8|Jet4| `src/agents/jet4.py` |Expérience de recrutement tardif rejetée|
|Agent public 9|Jet5| `src/agents/jet5.py` |Filtre mort pour l'achat de fertilisants|
|Agent public 10|Jet6| `src/agents/jet6.py` |Monétisation précoce + correction terminale des fertilisants|

<a id="lineage"></a>
## Ligne de descendance

Ces versions ne forment pas une seule chaîne d'héritage.

```text
CHI10
└── Public Agent 1

Public Agent 2
└── Public Agent 3

Public Agent 4
├── Public Agent 5
│   └── Public Agent 6
└── Public Agent 7  (built from Public Agent 3 behavior)
    ├── Public Agent 8  (rejected experiment)
    └── Public Agent 9
        └── Public Agent 10
```

La descendance suit les relations explicitement documentées dans les notes des agents fournis ; le numéro est uniquement une convention de documentation unifiée.

<a id="public-agent-1--public-meta-shop-and-market-overlay"></a>
## Agent public 1 — couche de boutique et de marché publique

**Nom original :** CHI11   **Source :** `src/agents/chi11.py`

`src/agents/chi11.py` est une variante expérimentale de CHI 10 inspirée par des travaux publics de haute performance dans Kaggriculture. Elle transfère intentionnellement des mécanismes généraux au lieu de copier des enregistrements d'action de répétition.

L'Agent public 1 conserve le plan économique CHI 10 et ajoute une couche d'observation limitée basée sur l'état de jeu public.

<a id="public-agent-11-public-references"></a>
### Public Agent 1.1 Références publiques

- Notebook public v48 de Kaito Fukami (score public historique : 3009.0) : https://www.kaggle.com/code/kaitofukami/40-40-early-floor-39-46-top-10-v48-fast-routes
- Politique économique consciente de la scène de GzmCR : https://github.com/GzmCR/Kaggriculture
- Analyse de répétition, marché et routage de lonespear : https://github.com/lonespear/kaggriculture

Les itinéraires de Kaito v48, selon les déverrouillages de boutiques visibles publiquement, sélectionnent un seul contrôleur enfant par tour et accordent une priorité explicite aux ventes sensibles aux collisions. L'Agent public 1 adapte ces idées au plan fermé de CHI 10.

<a id="public-agent-12-changes-from-chi-10"></a>
### Public Agent 1.2 Modifications par rapport à CHI 10

Les modifications conservées sont :

1. les premières et deuxième boutiques déverrouillées appliquent des préférences de demande de 8 % et 3 % respectivement aux scores de production marginaux initialement inchangés ;
2. un empreinte de ferme publique suit la situation où les deux fermes restent presque identiques pendant 24 tours consécutifs ;
3. les emplacements existants de `SELL` sont réorganisés selon l'impact estimé sur le prix, tout en conservant l'emplacement initial pour chaque commande non de vente ;
4. lors d'un état de clone persistant, les lots ordinaires de ventes sont limités à dix afin de réduire les collisions sur le marché simultané ;
5. CHI 10 est appelé exactement une fois par observation.

Aucune identité d'adversaire, aucun niveau de compétence, aucun identifiant d'épisode, aucun inventaire caché, aucune recherche de reprise ni aucune action future n'est utilisée. La liquidation du jour final n'est jamais limitée.

<a id="public-agent-13-shop-order-production-prior"></a>
### Production préalable des commandes de l'agent public 1.3

L'ordre des boutiques débloquées est utilisé comme une priorité modérée de production.

La première boutique débloquée applique un multiplicateur de 8 % et la deuxième un multiplicateur de 3 % à la production dont la sortie correspond à la demande de la boutique publique correspondante.

Ces multiplicateurs sont appliqués en plus du score de production existant de CHI 10 :

```text
Public Agent 1 score = CHI 10 score × public shop multiplier
```

L'ajustement reste intentionnellement petit afin que le calcul existant de la marge marginale reste décisif, sauf si les candidats de production sont déjà proches.

<a id="public-agent-14-public-farm-similarity-detection"></a>
### Détection de la similarité des fermes par l'agent public 1.4

L'agent public 1 construit une signature compacte à partir des informations déjà visibles dans l'observation :

- comptes de cultures ;
- comptes d'animaux ;
- nombre de quadrants débloqués ;
- nombre d'ouvriers agricoles.

Les deux fermes sont considérées comme persistemment similaires uniquement après une répétition de similarité proche de ces signatures publiques.

Les seuils conservés sont :

```text
detection starts at step 48
signature distance <= 2
24 consecutive matching turns
overlay can become active from step 160
```

<a id="public-agent-15-market-impact-aware-sell-ordering"></a>
### Commande de vente consciente de l'impact sur le marché par l'agent public 1.5

L'agent public 1 ne crée pas une stratégie de vente séparée. Il réorganise uniquement les commandes de vente déjà existantes dans l'action CHI 10.

Pour chaque vente existante, le planificateur estime l'impact immédiat sur le prix provenant de la quantité vendue :

```text
impact = quantity × max(current price - post-sale price, 0)
```

Les slots de vente avec le plus grand impact estimé sont exécutés en premier, tandis que chaque slot de marché non de vente conserve sa position originale.

Lors d'un état de clone public persistant, les quantités ordinaires de ventes sont limitées à 10 unités afin de réduire les collisions sur le marché simultané. La liquidation du jour final n'est jamais limitée.

<a id="public-agent-16-standalone-submission"></a>
### Public Agent 1.6 — Soumission autonome

L'agent public 1 intègre directement l'implémentation de CHI 10 dans le même module.

Le résultat final `agent(obs)` :

1. détecte l'état public-méta ;
2. applique temporairement le multiplicateur de production des commandes de boutiques ;
3. appelle exactement une fois l'agent CHI 10 intégré ;
4. restaure la fonction de scoring de production originale ;
5. réorganise les slots de vente résultants.

Aucune importation locale de projet n'est requise, donc `chi11.py` peut être soumis directement comme un seul fichier d'agent Kaggle.

<a id="public-agent-17-relationship-with-public-agent-4"></a>
### Public Agent 1.7 — Relation avec Public Agent 4

L'agent public 4 est une branche expérimentale séparée et n'est pas un successeur de l'agent public 1.

L'agent public 1 transfère des idées publiques sélectionnées dans le planificateur heuristique fermé du projet. L'agent public 4 conserve au contraire une route d'action publique forte comme base afin que cette route puisse être inspectée et améliorée directement.

En gardant les deux familles séparées, les améliorations de CHI et les améliorations dérivées de la route sont mesurables de manière indépendante.

<a id="public-agent-18-preliminary-local-validation"></a>
### Public Agent 1.8 — Validation locale préliminaire

La comparaison déterministe utilise les semences 1101 et 1102 dans les deux sièges :

|Séance|Siège de l'Agent Public 1|Agent Public 1|CHI 10|Marge|
| ---: | ---: | ---: | ---: | ---: |
| 1101 | 0 | 102,843 | 91,104 | +11,739 |
| 1101 | 1 | 104,727 | 100,928 | +3,799 |
| 1102 | 0 | 82,811 | 82,009 | +802 |
| 1102 | 1 | 84,203 | 79,258 | +4,945 |

Résultat : 4 victoires sur 4, marge moyenne +5 321,2. Cela correspond à un écran de développement réduit, pas à une preuve d'amélioration du classement.

Exécuter la comparaison avec :

```powershell
.\.venv\Scripts\python.exe experiments\compare_chi11.py
```

Tests unitaires ciblés :

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_chi11.py -q -p no:cacheprovider
```

<a id="public-agent-2--retained-public-v58-agent"></a>
## Agent Public 2 — Agent public V58 conservé

**Nom original :** Ye   **Source :** `src/agents/ye.py`

`src/agents/ye.py` est l'agent public V58 indépendant conservé publié par [Kaito Fukami](https://www.kaggle.com/code/kaitofukami/238-238-known-streams-v58-minimax-closed-loop). Le dépôt conserve l'artefact exécutable en Python lui-même, et non un archivage de notebook téléchargeable.

Le contrat d'intégrité actuel est :

- taille du fichier : **315 484 octets**;
- SHA-256 : `b041058ec187a8d0a01edc0eab8de068b53deca3e6c1973faf74ace6916ddcb9`;
- points d'entrée : `agent`, `_kaggle_submission_entrypoint` et `kaggle_agent_v58`;
- dépendances de fonctionnement : uniquement la bibliothèque standard de Python;
- ensemble de politiques : dix itinéraires, chacun contenant 719 actions.

<a id="public-agent-21-runtime-architecture"></a>
### Public Agent 2.1 — Architecture d’exécution

L'Agent Public 2 reconstruit dynamiquement ses modules de contrôle empaquetés en mémoire et expose dix itinéraires de politique :

|Politique|Rôle actuel|
| --- | --- |
| `base_backbone` |Itinéraire par défaut|
| `base_yarn` |Branche YARN du premier magasin|
| `base_pet` |Continuation du PET sélectionné dans le deuxième magasin public|
| `recovery` |Branche de récupération d'état public|
| `smoothie` |Continuation de la transition des FARMERS vers les SMOOTHIE|
| `clone` |Continuation de la réplication publique persistante|
| `known_yarn` |Continuation d'état public exact suivant un ouverture YARN|
| `ice_minimax` |Continuation ICE récupération / minimax|
| `bakery_yarn` |Continuation de la transition BAKERY vers YARN|
| `pizza_recovery` |Continuation de récupération PIZZA vers PET|

Un contrôleur est construit à chaque appel précoce. Son préfixe d'observation manquée est retransmis avant qu'il ne devienne disponible. Après le phase de réchauffement, tous les contrôleurs construits sont évalués et le routeur retourne l'action sélectionnée.

<a id="public-agent-22-public-state-routing"></a>
### Public Agent 2.2 — Routage fondé sur l’état public

Le routage dépend uniquement de la configuration visible et des observations :

|Tic|Signal public|Résultat possible|
| ---: | --- | --- |
| 72 |Premier magasin, les deux valeurs de fonds publics, l'inventaire du marché WHEAT, et les actifs de l'adversaire visibles|Récupération, minimax ICE, attente dans le deuxième magasin ou itinéraire de base|
| 96 |Signatures publiques exactes suivant une ouverture YARN|Continuation `known_yarn`|
| 144 |Deuxième magasin débloqué|Continuation SMOOTHIE, BAKERY/YARN ou PIZZA/PET|
| 360 |Au moins 240 ticks consécutifs d'égalité exacte entre les fermes publiques|Continuation `clone`|

Le routeur actif ne consulte ni l'identité de l'adversaire, ni les IDs de soumission, ni la graine cachée, ni l'état privé de l'adversaire, ni les actions futures de l'adversaire.

<a id="public-agent-23-current-limitations"></a>
### Limites actuelles de l'Agent Public 2.3

- Tous les contrôleurs disponibles sont évalués après le phase de réchauffement, y compris ceux qui ne sont pas sélectionnés. Cela augmente le coût de fonctionnement et permet à une panne d'un contrôleur inutilisé d'affecter l'ensemble du tic.
- Un gestionnaire d'exception général rechute sur `_v51_safe_action` sans fournir un compteur diagnostique.
- Plusieurs portes de route exigent une somme exacte, des signatures d'inventaire et d'actif. Une petite déviation de trajectoire ou d'engine maintient donc l'agent sur sa route de base plutôt que de choisir une récupération voisine.
- L'enregistrement dynamique de module dans `sys.modules` est adapté à un travailleur isolé mais peut provoquer des conflits avec d'autres agents dans un processus de recherche longue durée.
- Le dépôt conservé prouve l'intégrité de l'artefact et le comportement d'importation ; il ne contient ni le notebook d'évaluation original ni une référence stratégique indépendamment répétable pour l'Agent Public 2.

<a id="public-agent-3--hardened-v58-execution"></a>
## Agent Public 3 — Exécution renforcée V58

**Nom original :** Ye1   **Source :** `src/agents/ye1.py`

`src/agents/ye1.py` conserve `src/agents/ye.py` comme référence publique V58 inaltérée et ajoute des améliorations limitées en matière d'exécution, de sécurité et d'équivalence d'engine. Il préserve les itinéraires, les signatures, les seuils de V58 et le contrat de routage exclusif au statut public.

L'Agent Public 3 réchauffe les candidats d'itinéraire V58 via l'ouverture du magasin caché, puis sélectionne le contrôleur `known_yarn` au premier point de contrôle public. Ce contrôleur a produit la moyenne la plus élevée de la somme finale paire dans l'écran local conservé et est avancé seul pour le reste de l'épisode.

Chaque contrôleur requis est isolé derrière sa propre limite d'exception. L'échec d'un contrôleur est compté dans `_YE1_TELEMETRY` et recourt à l'action de route alignée de ce contrôleur au lieu de faire tomber l'ensemble du tick sur le retour global PASS. Les données de suivi enregistrent les appels totaux, les appels de politique, les erreurs de politique, les erreurs externes et les utilisations de retour.

Les aides du marché désactivées sont représentées par un objet pas-rien différé, évitant ainsi les copies de leurs itinéraires et l'allocation de leur état. La liquidation terminale utilise actuellement `episodeSteps`, `shedCapacity` et `maxMarketOrdersPerTurn`, et projette PICKUP, DROP et PLACE avant de construire la file finale SELL. Les calculs de valeur de marché fusionnent les surcharges sparses `configuration.marketParams` et les paramètres d'observation efficaces, avec les valeurs d'observation ayant la priorité.

L'écran agrégé conservé utilise les semences 11, 22, 33 et 44 dans les deux sièges contre l'Agent Public 2. La moyenne de la somme finale a augmenté de 62 120,25 pour l'Agent Public 3 initial à 75 230,25 pour la variante optimisée ; ses adversaires pairs d'Agent Public 2 avaient une moyenne de 66 657,50. L'Agent Public 3 a remporté six sur huit parties paires, sans nul match nul. L'importation propre, l'isolement des pannes, la projection terminale PICKUP, les paramètres de marché sparses et les huit completions de partie entières ont été validés. Ces résultats sont locaux, pas une déclaration de classement. `src/agents/ye.py` reste la référence publique V58 inaltérée.

<a id="public-agent-23-verification-and-provenance"></a>
### Vérification et traçabilité de l'Agent Public 2–3

`src/agents/ye.py` reste la référence publique V58 inaltérée publiée par [Kaito Fukami](https://www.kaggle.com/code/kaitofukami/238-238-known-streams-v58-minimax-closed-loop).

Le dépôt conserve l'artefact exécutable en Python lui-même. Les vérifications structurelles incluent l'importation propre, la taille du fichier du document public Agent 2 documenté et son digest SHA-256, ses points d'entrée appelables, et les dix itinéraires de politique à 719 actions.

Ces vérifications établissent l'intégrité de l'artefact et la structure en temps d'exécution. Elles ne constituent ni une déclaration de classement ni une référence stratégique indépendamment répétable pour l'agent original Agent Public 2.

<a id="public-agent-4--readable-public-route-baseline"></a>
## Agent Public 4 — Base d'itinéraire publique lisible

**Nom original :** Jet   **Source :** `src/agents/jet.py`

`src/agents/jet.py` est la base de référence conservant le comportement.

L'itinéraire original était stocké sous forme de données compressées. Il a été mécaniquement décompressé pour former une liste Python lisible contenant exactement 719 actions d'itinéraire, organisées par jour, heure et étape.

La conversion modifie uniquement la représentation. Elle ne modifie pas intentionnellement les actions d'itinéraire.

Le comportement en temps réel hérité de l'agent public inclut :

- un itinéraire d'action fixe pour l'épisode ;
- une alignement manuel avec l'observation actuelle ;
- un remplacement local de WEED autour de `PLANT` et `BUILD_PASTURE` ;
- une estimation officielle du prix de marché ;
- l'ordre des slots de vente existants d'itinéraire classés par impact estimé de prix ;
- un poids de demande de ville borné dans le régime de rééquilibrage ;
- aucune identification d'adversaire, aucune recherche d'épisode ni de recherche d'action future.

La base reste intentionnellement orientée vers l'itinéraire plutôt qu'un plan général.

<a id="public-agent-5--safe-fallback-and-final-liquidation"></a>
## Agent public 5 — Fallback sécurisé et liquidation finale

**Nom original :** Jet1   **Source :** `src/agents/jet1.py`

`src/agents/jet1.py` conserve le même itinéraire macro à 719 étapes et ajoute deux améliorations de fonctionnement mineures.

<a id="public-agent-51-staged-runtime-fallback"></a>
### Agent public 5.1 Fallback en temps réel progressif

La base encapsule l'ensemble du pipeline en temps réel dans un gestionnaire d'exception global. Tout erreur inattendue peut donc remplacer l'ensemble de l'action prévue par `PASS`.

L'agent public 5 isole les étapes en temps réel :

```text
base route action
      |
      v
WEED repair
      |
      v
final liquidation
      |
      v
SELL ordering
      |
      v
hand alignment
```

Si une étape optionnelle échoue, l'agent conserve l'action d'itinéraire valide précédente. Un fallback complet pour `PASS` reste uniquement dans les cas où l'itinéraire de base ne peut pas être récupéré.

Ceci est conçu comme une amélioration de robustesse, et non une modification stratégique.

<a id="public-agent-52-observation-based-final-liquidation"></a>
### Agent public 5.2 Liquidation finale basée sur l'observation

L'itinéraire original contient des quantités fixes de vente finale. L'agent public 5 remplace uniquement l'action de marché finale actionable par une liquidation construite à partir de l'inventaire observable.

La logique :

1. déduit l'étape finale actionable à partir de `episodeSteps` ;
2. lit le contenu actuel du dépôt ;
3. projette les actions de `DROP` au dépôt avant l'exécution sur le marché ;
4. crée une commande de vente pour chaque produit non vide disponible ;
5. respecte le nombre maximum configuré d'ordres de marché.

Les actions d'itinéraire antérieures restent inchangées.

<a id="public-agent-6--public-state-market-overlay"></a>
## Agent public 6 — Superposition de marché basée sur l'état public

**Nom original :** Jet2   **Source :** `src/agents/jet2.py`

`src/agents/jet2.py` est un agent de routage autonome. Son itinéraire macro actif est le même itinéraire public V27 de 719 étapes que celui intégré à Public Agent 5. L’implémentation conserve le classement SELL de Public Agent 5 et ajoute une seule intervention sur le marché : anticiper, de manière bornée, une vente prévue sur l’itinéraire lorsque les deux fermes publiques restent suffisamment similaires.

<a id="public-agent-61-active-runtime-pipeline"></a>
### Agent public 6.1 Pipeline en temps réel actif

L'action retournée à chaque tick est construite par le pipeline suivant :

```text
719-step route action
        |
        v
hand-count alignment
        |
        v
public-state expert update
        |
        v
WEED repair
        |
        v
terminal liquidation, when applicable
        |
        v
clone-route sale preemption
        |
        v
Public Agent 5 SELL-slot ranking
        |
        v
final hand-count alignment
```

Chaque étape d'amélioration a sa propre limite d'exception. Si une étape échoue, l'Agent Public 6 enregistre l'erreur dans son état de fonctionnement par siège et conserve l'action valide précédente. Pour la phase du marché, les modifications d'état sont préparées sur une copie et validées uniquement après que l'ensemble de la phase ait réussi, de sorte qu'un échec ne laisse pas de dettes de ventes partiellement enregistrées.

<a id="public-agent-62-selected-market-behavior"></a>
### Comportement du marché sélectionné pour l'Agent Public 6.2

L'interface de marché active utilise uniquement des observations publiques et la route de l'agent lui-même :

- une distance est calculée à partir des actifs agricoles visibles des deux joueurs ;
- le signal de clone nécessite 24 observations consécutives avec une distance maximale de deux et ne peut pas être activé avant le tick 160 ;
- pendant que le signal est valide, l'agent examine sa propre vente planifiée deux ticks plus tard ;
- il peut avancer au maximum dix unités déjà disponibles dans son dépôt ;
- chaque quantité avancée est enregistrée par produit et soustraite de la vente planifiée sur la route ;
- les quantités non payées sont transférées d'au plus un tick lorsque la vente prévue n'est pas disponible ;
- la limite de commande de marché configurée est respectée ;
- la liquidation finale se produit à `episodeSteps - 2` et est basée sur le contenu projeté du dépôt au même tick.

Aucune identité d'adversaire, aucun inventaire privé de l'adversaire, aucun identifiant d'épisode, aucune graine cachée, ni aucune action future de l'adversaire n'est utilisée.

<a id="public-agent-63-code-retained-but-inactive"></a>
### Agent Public 6.3 : code conservé mais inactif

Le fichier contient encore des aides pour l'estimation de l'approvisionnement adverse, des experts de marché hystérétiques, le report de ventes après la demande, le classement des séries de ventes SELL continues, et des ventes sur des ticks de marché inactifs. Ces aides ne sont pas appelées par la pipeline active `agent` et ne doivent pas être décrites comme faisant partie de la stratégie active de l'Agent Public 6.

La pipeline active appelle intentionnellement `_jet1_rank_sell_slots` ; le triateur alternatif et le générateur général `_market_overlay` restent des outils expérimentaux.

<a id="public-agent-64-current-limitations"></a>
### Limites actuelles de l'Agent Public 6.4

- Le plan agricole reste une route fixe plutôt qu'un plan général.
- La récupération WEED est locale et ne prouve pas que la route complète a été synchronisée après une divergence importante.
- La similarité entre fermes publiques est uniquement une heuristique de distance des actifs. Elle ne prouve pas que l'adversaire vendra le même produit au même moment.
- L'optimisation de la préemption s'adapte au timing face à un adversaire similaire à une route et n'est pas une preuve d'amélioration universelle face à des stratégies non liées.
- Plusieurs aides de marché restent dans le module malgré leur inactivité, ce qui augmente la surface d'analyse et rend la pipeline active moins visible.

<a id="public-agent-7--public-agent-3-backbone-and-terminal-corrections"></a>
## Agent Public 7 — fondation de l'Agent Public 3 et corrections terminales

Nom original : Jet3   Source : `src/agents/jet3.py`

`src/agents/jet3.py` est la base locale de l'expérience de l'Agent Public 8. Il conserve le comportement complet de l'Agent Public 3 et ajoute deux corrections bornées sans remplacer la route sélectionnée ni sa stratégie de production :

- `_jet3_final_drop` envoie les stocks conservés vers le dépôt le plus proche juste à temps pour la liquidation terminale existante ;
- `_jet3_filter_dead_seed_buys` élimine les achats de semences que la continuation sélectionnée n'aura jamais plantées ;
- la liquidation terminale basée sur les observations existante reste active à `episodeSteps - 2`.

Sur l'ensemble de huit parties de test contre l'Agent Public 3, l'Agent Public 7 a obtenu en moyenne 85 286,25 unités de monnaie contre 84 041,75 pour l'Agent Public 3, soit une augmentation de 1 244,50 unités, et a remporté toutes les huit parties.

<a id="public-agent-8--rejected-late-hiring-experiment"></a>
## Agent Public 8 — Expérience de recrutement tardif rejetée

**Nom original :** Jet4   **Source :** `src/agents/jet4.py`

`src/agents/jet4.py` est une copie autonome de l'Agent Public 7 avec une seule filtration appliquée aux ordres de marché sur `HIRE`. L'expérience a été motivée par une analyse séparée de 813 répétitions des top-10 : les classements 1 à 3 ont effectué en moyenne 105 recrutements tardifs par partie, tandis que les classements 8 à 10 ont effectué en moyenne 119. Cette corrélation a été traitée uniquement comme une hypothèse expérimentale : réduire les recrutements tardifs qui ne pourraient peut-être pas rembourser leur coût avant la fin de la partie.

Chaque ordre `HIRE` recrute un employé. Le compteur public `hires_today` identifie le coût suivant de Fibonacci, exprimé en unités uniques, multiplié par `farmHandCostMult`. L'Agent Public 8 suppose un rendement conservateur de une unité de monnaie par tick restant de l'employé et conserve un recrutement uniquement lorsque les ticks restants jusqu'à `episodeSteps - 2` sont au moins égaux à son temps estimé de remboursement. Ainsi, la filtration est fondée sur le coût et l'horizon ; elle ne désactive pas tous les recrutements après une date fixe. Tous les comportements de non-recrutement restent inchangés par rapport à l'Agent Public 7.

La référence directe utilisée initialise les semences 0 à 9, les deux sièges pour chaque semence, et la même configuration de 720 étapes, pour 20 parties paires :

|Métrique|Agent Public 7|Agent Public 8|
| --- | ---: | ---: |
|Montant final moyen| 81,960.70 | 80,391.10 |
|Minimum| 54,254.00 | 53,514.00 |
|Maximum| 116,539.00 | 114,292.00 |
|Victoires| 20 | 0 |

La différence entre l'Agent Public 8 et l'Agent Public 7, dans les paires, a été en moyenne de -1 569,60, avec un minimum de -3 138,00 et un maximum de -463,00. Ni l'un ni l'autre agent n'a enregistré une erreur externe, une erreur de politique ou un recours par défaut. L'Agent Public 8 a examiné 5 580 ordres de recrutement, a modifié 120, et a donc évité 120 recrutements d'employés, soit six par partie.

Le résultat de l'Agent Public 8 était de 0 victoire et 20 défaites. L'expérience est rejetée car elle a systématiquement dégradé le montant final. La corrélation observée dans les 813 répétitions des top-10 ne se traduit pas par un gain réplicable sous cette règle de remboursement au ratio de rendement, donc l'Agent Public 7 reste la base locale plus forte.

<a id="public-agent-9--dead-fertilizer-purchase-filter"></a>
## Agent Public 9 — Filtre de rejet des achats de fertilisant

**Nom original :** Jet5   **Source :** `src/agents/jet5.py`

`src/agents/jet5.py` part directement de Public Agent 7 et n’hérite pas de l’expérience rejetée de Public Agent 8. Sa seule modification teste si Public Agent 7 achète de l’engrais que la suite d’actions sélectionnée ne peut plus consommer. L’hypothèse provient d’une analyse distincte de 813 replays : les équipes moins bien classées du top 10 achetaient nettement plus d’engrais, surtout en fin de partie. Il s’agit d’une corrélation, pas d’une preuve causale.

Les achats de fertilisant sont représentés par `["BUY_PRODUCT", "FERTILIZER", quantity]`. Chaque action valide d'un acteur `FERTILIZE` consomme une unité. Avant l'étape 72, le filtre compte les actions restantes `base_backbone` jusqu'à l'étape 71 suivies par les actions `known_yarn` à partir de l'étape 72 ; à partir de l'étape 72, il compte les actions restantes `known_yarn` de la suite. Il somme les fertilisants observés dans le grenier et tous les inventaires transportés, autorise de manière conservatrice la consommation prévue dans la même étape, et limite les achats à l'usage planifié restant. Un achat reste inchangé lorsqu'il est entièrement nécessaire, est réduit lorsqu'il est partiellement excessif, et est supprimé lorsque aucune unité supplémentaire ne peut être consommée. L'information sur l'inventaire manquante laisse l'action du Public Agent 7 inchangée, et la collecte de fertilisant futur est intentionnellement ignorée afin de maintenir le filtre conservateur.

La validation finale a utilisé les graines 0 à 99, les deux sièges pour chaque graine, et la même configuration de 720 étapes, pour 200 parties paires. Le Public Agent 7 a obtenu en moyenne 84 209,90 unités de argent final et le Public Agent 9 a obtenu en moyenne 84 251,37. La différence entre le Public Agent 9 et le Public Agent 7 dans les paires était de +41,46. Le Public Agent 9 a enregistré 184 victoires et 16 défaites, avec des résultats positifs sur 94 des 100 graines. Ni l'un ni l'autre agent n'a enregistré une erreur externe, une erreur de politique ou un recours automatique.

Le gain est petit mais reproduisible dans la validation plus large. Le Public Agent 9 est actuellement la base conservée.

<a id="public-agent-10--earlier-monetization-of-finished-products"></a>
## Public Agent 10 — Monétisation précoce des produits finis

**Nom original :** Jet6   **Source :** `src/agents/jet6.py`

<a id="initial-public-agent-10-experiment"></a>
### Première expérience du Public Agent 10

Le Public Agent 10 a commencé à partir du Public Agent 9 avec un filtre de viabilité tardif des tomates. L'hypothèse provient d'une corrélation observée dans une analyse préalable des meilleurs reprises, mais la suite du Public Agent 9 sélectionné n'a émis aucune plante de tomate. Les graines 0 à 99, les deux sièges, ont donc produit zéro action examinée ou modifiée de tomate, zéro graine évitée, et une différence moyenne par paire de 0,00. L'expérience a été inconclusive et son code a été supprimé.

<a id="terminal-fertilizer-correction"></a>
### Correction terminale du fertilisant

Un trace de fonctionnement a révélé un défaut réel terminal. Entre les étapes 714 et 717, un ouvrier pouvait tenter de collecter sur une prairie vide, prendre soin de l'animal adjacent, et collecter le fertilisant uniquement après qu'il était trop tard pour le retourner dans le grenier. Le Public Agent 10 commence maintenant cette route de collecte sur une seule case à l'étape 714, ou avance une étape de `CARE` à `COLLECT_FERTILIZER` à l'étape 715, uniquement lorsque la collecte, le retour et le dépôt peuvent encore être effectués avant la liquidation. L'information manquante et les actions non liées restent inchangées.

La correction a obtenu +1,00 sur l'écran de 20 parties. Sur les graines 0 à 99, elle a obtenu une moyenne finale de 84 225,79 contre 84 224,79 pour le Public Agent 9 : différence moyenne par paire de +0,99, plage par paire de -21 913 à +21 914, 196 victoires et 4 défaites, avec tous les 100 graines positifs après combinaison des deux sièges. Aucune erreur ni recours n'a été enregistré. Les données de suivi ont enregistré 400 collectes mortes examinées, 174 itinéraires de récupération lancés, 373 collectes avancées et 373 unités de fertilisant récupérées. La règle est conservée comme une correction de bug valide, et non comme l'amélioration principale du Public Agent 10.

<a id="public-research-and-runtime-diagnosis"></a>
### Recherche publique et diagnostic en temps réel

La phase de recherche a examiné les éléments suivants :

- l'agent [Lonespear Kaggriculture et le journal d'ajustement](https://github.com/lonespear/kaggriculture), dont les expériences mesurées rejettent les ventes concentrées tardives, identifient la fuite d'inventaire en fin de partie, et valident le regroupement local des tâches des ouvriers ;
- l'agent [Multi-Route Farming Agent](https://www.kaggle.com/code/flexonafft/kaggriculture-multi-route-farming-agent), qui sélectionne des continuations fixes à partir de l'état observable du magasin ;
- l'agent [COK public agent and strategy notes](https://github.com/COK-ZhangZiliang/Kaggriculture), qui utilise une récupération de l'état public en cas d'échec et une liquidation projetée ;
- le [notebook AgroBoss](https://www.kaggle.com/code/songoku2005/kaggriculture), qui utilise une affectation greedy vers le travailleur le plus proche ;
- la [documentation officielle de l'environnement](https://github.com/Kaggle/kaggle-environments/blob/master/kaggle_environments/envs/kaggriculture/AGENTS.md).

La liste restreinte a été intentionnellement petite. La récupération de l'inventaire terminal était déjà largement implémentée par l'Agent Public 9, le remplissage du terrain à la fin de la partie était déjà présent dans le ruban sélectionné, et l'affectation des tâches par cluster allait remplacer la stratégie de production fixe. La sélection multi-route publique était directement applicable mais à haut risque. Les ventes préalables étaient fréquentes, locales, compatibles avec le parcours, et soutenues par la découverte publique selon laquelle une concentration de ventes terminal perd de la valeur par effet de marché.

Le continuant actif a été inspecté de manière statique et sur les semences 0 à 9, pour les deux sièges. Les inventaires finaux et des semences étaient nuls. Avant la correction terminale, 16 unités de fertilisant restaient réparties sur 20 parties. Le parcours a acheté deux quadrants de terrain et n'a pas montré de preuves que des terrains verrouillés supplémentaires limitaient la production. Il a émis 279 ordres `HIRE` par partie, bien que seulement les recrutements initiaux puissent réussir ; en supprimant uniquement ces opérations sans danger, il n'était pas possible d'augmenter le montant final. Le parcours fixe utilisait seulement 697 des 7 200 slots possibles de commandes de marché par partie.

Les actions de marché importantes sur le parcours sélectionné étaient :

|Action et article|Commandes|Quantité|Premier pas|Dernier pas|Commande la plus importante|
| --- | ---: | ---: | ---: | ---: | ---: |
| `BUY_PRODUCT WHEAT` | 53 | 140 | 1 | 278 | 5 |
| `BUY_PRODUCT FERTILIZER` | 18 | 51 | 150 | 697 | 8 |
| `BUY_SEED WHEAT` | 25 | 187 | 1 | 624 | 11 |
| `BUY_SEED STRAWBERRY` | 15 | 44 | 96 | 264 | 23 |
| `BUY_SEED MELON` | 2 | 13 | 1 | 284 | 12 |
| `BUY_SEED CARROT` | 6 | 10 | 96 | 669 | 3 |
| `BUY_ANIMAL COW` | 5 | 6 | 1 | 176 | 2 |
| `BUY_ANIMAL SHEEP` | 6 | 11 | 1 | 265 | 2 |
| `BUY_LAND` | 2 | 2 | 150 | 265 | 1 |
| `SELL WHEAT` | 57 | 359 | 2 | 718 | 50 |
| `SELL FERTILIZER` | 96 | 358 | 30 | 717 | 17 |
| `SELL WOOL` | 44 | 285 | 150 | 711 | 20 |
| `SELL MILK` | 43 | 236 | 195 | 711 | 15 |
| `SELL STRAWBERRY` | 33 | 272 | 388 | 713 | 16 |
| `SELL MELON` | 8 | 72 | 248 | 264 | 12 |
| `SELL CARROT` | 5 | 18 | 676 | 715 | 6 |

Les 20 parties de fonctionnement ont émis 4 740 `PLANT`, 1 220 `FERTILIZE`, 5 580 `HIRE`, 340 constructions de pâturages, 40 constructions de coopératives, et 2 180 placements. Les totaux de marché en cours incluaient 2 800 blés achetés, 620 fertilisants achetés après le filtre de l'Agent Public 9, 7 246 blés vendus, 7 244 fertilisants vendus, 5 700 laine vendue, 4 720 lait vendu, 5 440 fraises vendues, 1 440 melon vendu, et 360 carottes vendues. Ainsi, la production a été finalisée, mais les produits finis attendaient souvent dans le hangar alors que les slots de marché étaient inutilisés. C'était la faiblesse économique la plus récurrente ; les semences faibles se terminaient également avec beaucoup moins d'argent, donc la récupération de centaines par partie était proportionnellement plus importante là-bas.

<a id="candidates-tested-and-retained-mechanism"></a>
### Mécanisme testé et conservé

L'activation du sélecteur multi-parcours public intégré a été testée en premier. Il a été activé sur 3 882 étapes de récupération de parcours et 1 246 étapes connues de Yarn dans l'écran de 20 parties, mais a réduit de 3 340,00 la moyenne du montant final. Il a remporté 7 semences et a perdu 3, avec des résultats associés allant de -32 874 à +15 353. Ce candidat a été rejeté et complètement annulé.

Le mécanisme conservé remplit les slots de marché inutilisés par des ventes de produits finis déjà visibles dans le hangar privé. Il soustrait les quantités déjà couvertes par l'action actuelle, ne dépasse jamais la limite configurée des commandes, et exclut le blé et le fertilisant car le parcours fixe peut encore les utiliser comme entrées. Il ne modifie pas les actions des ouvriers, la production, les achats, les terrains ou les itinéraires. C'est une transfert spécifique au projet de la découverte publique sur le moment de vente, et non une copie de code d'agent public.

Sur l'écran des semences 0–9, l'Agent Public 10 a obtenu en moyenne 81 730,10 contre 80 564,40 pour l'Agent Public 9. Le gain pair était de +1 165,70 (+1,45 %), avec 18 victoires, 2 défaites, 9 semences positives, 1 semence négative et aucune erreur. La validation complète des semences 0–99 était :

|Métrique|Agent Public 9|Agent Public 10|
| --- | ---: | ---: |
|Montant final moyen| 83,019.35 | 83,979.63 |
|Médiane| 82,499.00 | 83,438.00 |
|Minimum| 41,061.00 | 41,934.00 |
|Maximum| 138,151.00 | 138,732.00 |

Le gain pair moyen était de +960,27, soit +1,16 %, avec une plage pair de -21 250 à +23  233. L'Agent Public 10 a enregistré 190 victoires, 10 défaites et aucune nul. Au niveau des semences, 96 étaient positives, 4 négatives et aucune neutre. Les extrêmes importants du gain étaient dus à des effets d'interaction entre sièges opposés ; leurs totaux de semences restaient représentatifs, et le gain n'était pas dépendant de quelques valeurs atypiques. Aucune erreur externe, aucune erreur de politique, ni aucune fallback n'a été détecté. Les données de télémétrie sur les ventes précoce ont enregistré 7 028 opportunités, 6 469 commandes ajoutées, 42 101 unités offertes et 3 001 opportunités observées sur des tours dont la liste des commandes de marché était déjà pleine.

L'ensemble non touché de validation a utilisé les semences 100–129, les deux sièges. L'Agent Public 9 a obtenu en moyenne 80 703,08 et l'Agent Public 10 a obtenu en moyenne 81 842,42. Le gain pair était de +1 139,33, soit +1,41 %, avec une plage allant de -219 à +3 009. L'Agent Public 10 a enregistré 59 victoires, 1 défaite et aucune nul ; toutes les 30 semences étaient positives. Aucune erreur ni fallback n'a été détecté. Les données de télémétrie sur l'ensemble non touché ont enregistré 2 104 opportunités, 1 936 commandes ajoutées, 12 723 unités offertes et 900 sauts sur marchés complets. Aucun seuil n'a été ajusté sur l'ensemble non touché.

Le mécanisme de vente précoce est donc conservé. Ensemble avec le correctif du bug sur le fertilisant terminal, il fait de l'Agent Public 10 la **base locale finale conservée** à la clôture du projet. Cette conclusion est limitée aux benchmarks locaux pairs et ne constitue pas une affirmation de classement.

<a id="shared-benchmark-protocol"></a>
## Protocole de benchmark partagé

Chaque modification de l'Agent Public 4 doit être comparée directement avec la version précédente de l'Agent Public 4.

Comparaison recommandée :

```text
same environment configuration
same seeds
both player seats when relevant
Public Agent 4 vs Public Agent 5
```

Enregistrement minimum :

- montant final / récompense ;
- minimum, maximum et moyenne sur plusieurs parties ;
- complétion / erreurs ;
- inventaire final de la grange ;
- inventaire final transporté ;
- nombre d'actions de route invalides ou perdues si instrumentées.

Une modification doit rester isolée jusqu'à ce que son effet soit compris.

<a id="archived-improvement-candidates"></a>
## Candidats d'amélioration archivés

Le projet est terminé. Les candidats suivants n'ont pas été mis en œuvre et sont conservés uniquement comme notes de recherche ; toute utilisation ultérieure doit préserver d'abord la route macro.

<a id="high-priority"></a>
### Priorité élevée

1. **Détection de divergence de route**
   - comparer l'état observé avec les points d'arrêt attendus par la route ;
   - déceler des différences dans les positions des ouvriers, l'inventaire, la production ou les fonds.

2. **Résynchro de WEED**
   - remplacer la fenêtre de replay fixe par une condition de résynchro de route ;
   - reprendre la route uniquement lorsque l'acteur concerné est de nouveau dans un état compatible.

3. **Récartographie locale des ouvriers**
   - lorsqu'un indice d'ouvrier ne correspond plus à l'état attendu de la route, récartographier uniquement la tâche affectée en utilisant les positions actuelles ;
   - éviter de remplacer l'entier allocateur de route.

4. **Simulation séquentielle d'ACHAT**
   - évaluer plusieurs ordres d'ACHAT dans l'ordre effectif de leur exécution ;
   - mettre à jour la projection de l'inventaire de marché après chaque vente simulée.

<a id="later-candidates"></a>
### Candidats ultérieurs

- quantités d'ACHAT adaptatives ;
- plusieurs points d'arrêt compatibles ou variantes de parcours ;
- estimation de l'approvisionnement avec prise en compte de l'adversaire ;
- des modifications plus importantes de parcours macro.

Ces éléments doivent être tentés uniquement après avoir mesuré les modifications de base et de robustesse, car le parcours fixe est actuellement la principale source de force de l'Agent Public 4.

<a id="documentation-and-provenance"></a>
## Documentation et provenance

Conserver l'origine du parcours public dans le dépôt et préserver toute attribution ou mention de licence nécessaire à la source publique originale.

L'Agent Public 4 ne doit pas être présenté comme une stratégie CHI originale. La contribution de ce branche au projet consiste en une reconstruction lisible, en un benchmarking et dans des améliorations ultérieures en temps de fonctionnement et de stratégie.
