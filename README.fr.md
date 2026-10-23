[English](README.md) | [Français](README.fr.md) | [简体中文](README.zh-CN.md)

<a id="kaggriculture"></a>
# Kaggriculture

Agent d’IA développé pour la compétition Kaggriculture sur Kaggle.

<a id="competition"></a>
## Compétition

Kaggriculture est une compétition de stratégie au tour par tour où les participants développent des agents autonomes pour gérer des fermes, des ressources, la production et les interactions sur le marché.

L'objectif de ce dépôt était de développer, évaluer et améliorer itérativement des agents pour la compétition.

<a id="project-status"></a>
## État du projet

Ce dépôt conserve désormais un **instantané d’un projet terminé**. Les résultats retenus sont les suivants :

- **Planificateur heuristique :** `chi14.py` est la dernière implémentation validée de la branche reconstruite du planificateur heuristique. `heuristic_ideas_v4` et `heuristic_ideas_final` restent des références de conception uniquement ; les tentatives ultérieures d'implémentation, y compris `CHI16` / `chi_final`, n'ont pas été conservées comme successeurs validés.
- **Agent d'apprentissage :** Le clonage comportemental et l’exécuteur hybride sont conservés comme une piste expérimentale, mais l'agent d'apprentissage n'a pas été retenu pour une utilisation autonome en compétition.
- **Branche dérivée publique :** `jet6.py` (Agent Public 10) est la dernière base locale conservée de cette branche.

Aucune implémentation d'agent source `CHI16` ou `chi_final` n'est incluse dans l'état final du dépôt.

<a id="repository-map"></a>
## Carte du dépôt

|Chemin|Objectif|
| --- | --- |
| `src/agents/` |Implémentations des agents|
| `src/learning/` |Modèles, ensembles de données, encodeurs et politiques d'apprentissage par clonage|
| `scripts/` |Scripts d’entraînement, d’évaluation et utilitaires|
| `experiments/` |Résultats des expériences et comparaisons de stratégies|
| `submissions/` |Agents soumis à Kaggle|
| `data/` |Données de replay et ensembles de données traités pour l'apprentissage|
| `models/` |Checkpoints entraînés et configuration d'inférence|
| `tests/` |Tests automatisés|
| `docs/` |Règles du jeu et documentation de développement des agents|
| `requirements.txt` |Dépendances en Python|
| `LICENSE` |Licence Apache 2.0|

<a id="setup"></a>
## Mise en place

Cloner le dépôt :

```bash
git clone https://github.com/Driw0x/kaggriculture.git
cd kaggriculture
```

Créer un environnement virtuel :

```bash
python -m venv .venv
```

Activer sur Windows :

```powershell
.\.venv\Scripts\Activate.ps1
```

Installer les dépendances :

```bash
pip install -r requirements.txt
```

<a id="documentation"></a>
## Documentation

* [`docs/game_rules.md`](docs/game_rules.fr.md) --- Règles complètes du jeu et mécanismes

* [`docs/getting_started.md`](docs/getting_started.fr.md) --- Guide de développement des agents, de tests locaux et de soumission à Kaggle

* [`docs/game_mechanics_reference.md`](docs/game_mechanics_reference.fr.md) --- Référence sur les mécanismes fondamentaux du jeu, la production, les animaux, l'infrastructure de ferme, les ouvriers, les magasins de ville et le comportement du marché.

* [`docs/chi_agents.md`](docs/chi_agents.fr.md) --- Ligne de descente initiale du planificateur heuristique CHI, depuis CHI10 jusqu'au test temporel.

* [`docs/heuristic_agents.md`](docs/heuristic_agents.fr.md) --- Branche réévaluée du planificateur heuristique depuis CHI12 jusqu'à l'implémentation finale conservée CHI14, ainsi que la continuation archivée v4/fin de conception uniquement.

* [`docs/learning_agent.md`](docs/learning_agent.fr.md) --- Piste expérimentale basée sur l'apprentissage, résultats hors ligne, évaluation autonome et la décision de ne pas la conserver pour une évolution ultérieure.

* [`docs/public_agent.md`](docs/public_agent.fr.md) --- Familles d'agents dérivés de la base publique, provenance, benchmarks locaux, expériences rejetées, et la base finale conservée de l'Agent Public 10.

* [`docs/agent_ideas.md`](docs/agent_ideas.fr.md) --- Inventaire historique des idées d'agents et de leur état d'implémentation.


<a id="license"></a>
## Licence

Ce projet est soumis à la licence Apache 2.0.

Voir [`LICENSE`](LICENSE) pour les détails.

<!-- multilingual-documentation -->

## Documentation complémentaire

- [docs/pseudo_code/heuristic_ideas_final.md](docs/pseudo_code/heuristic_ideas_final.fr.md)
- [docs/pseudo_code/heuristic_ideas_v1.md](docs/pseudo_code/heuristic_ideas_v1.fr.md)
- [docs/pseudo_code/heuristic_ideas_v2.md](docs/pseudo_code/heuristic_ideas_v2.fr.md)
- [docs/pseudo_code/heuristic_ideas_v3.md](docs/pseudo_code/heuristic_ideas_v3.fr.md)
- [docs/pseudo_code/heuristic_ideas_v4.md](docs/pseudo_code/heuristic_ideas_v4.fr.md)
