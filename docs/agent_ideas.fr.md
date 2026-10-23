[English](agent_ideas.md) | [Français](agent_ideas.fr.md) | [简体中文](agent_ideas.zh-CN.md)

[README du projet](../README.fr.md)

<a id="agent-ideas"></a>
# Idées de l'agent

<a id="1-state-memory"></a>
## 1. Mémoire d'état

Maintenir une mémoire interne des états persistants des exploitations agricoles afin que l'agent puisse suivre les plantations et les animaux au fil des étapes, au lieu de raisonner uniquement à partir de l'action actuelle.

-   **Plantations :** maintenir une liste des parcelles plantées avec leur position et leur état pertinent, tel que le type de culture, la date de plantation, l'état de croissance ou l'état prévu de récolte.
-   **Animaux :** maintenir une liste des animaux avec leur position et leur état afin de suivre leur évolution et les actions nécessaires au fil du temps.
-   Mettre à jour l'état stocké au fur et à mesure que la partie avance et supprimer ou réinitialiser les entrées lorsque une plantation ou un animal ne correspond plus à l'état stocké.

**État :** implémenté. Le planificateur conservé actualise l'état des cultures et des animaux à partir des observations et synchronise l'état de production stocké lorsque le type de production d'une case change.

<a id="2-general-path-management"></a>
## 2. Gestion de la trajectoire

Gérer le déplacement sous forme de trajet plutôt que de choisir chaque mouvement de manière indépendante. L'agent doit déterminer où il doit aller et suivre une voie appropriée vers cette destination.

-   Utiliser la gestion de la trajectoire pour toutes les actions spatiales, y compris le déplacement entre plantations, animaux, lieux de marché ou autres positions pertinentes.
-   Pour la plantation, définir une trajectoire efficace passant par les parcelles à planter au lieu de sélectionner les parcelles de manière indépendante.
-   La même logique de trajectoire générale peut être réutilisée pour d'autres séquences d'actions spatiales afin de réduire les déplacements inutiles.

**État :** implémenté. Les tâches spatiales sont désormais intégrées dans les calendriers des ouvriers. Le temps de trajet entre les tâches est inclus directement dans le calendrier, et les détours sont choisis parmi les quatre cases d'accès en fonction de l'ensemble du trajet, et non comme des déplacements isolés.

<a id="3-opponent-state-memory"></a>
## 3. Mémoire d'état de l'adversaire

Maintenir une mémoire interne de l'état observable de l'adversaire afin d'estimer ses productions futures potentielles et leur impact possible sur le marché.

- Suivre les plantations et les animaux de l'adversaire à travers les étapes.
- Utiliser leur état actuel pour estimer les productions futures possibles.
- Estimer à quel moment et en quelle quantité chaque ressource l'adversaire pourrait produire.
- Utiliser cette information pour anticiper une augmentation potentielle de l'offre sur le marché.
- Tenir compte des productions estimées de l'adversaire lors de l'évaluation des prix futurs sur le marché et des risques du marché.

**État :** partiellement implémenté. CHI10 peut inclure des projections de l'offre publique de l'adversaire dans les estimations du marché, mais la mémoire persistante de l'état de l'adversaire à travers les étapes n'est pas incluse dans la base de référence conservée.

<a id="4-priority-based-task-planning"></a>
## 4. Planification des tâches basée sur les priorités

Construire le plan quotidien à partir de priorités explicites des tâches plutôt que de considérer toutes les actions comme de la même importance.

- Prioriser les tâches obligatoires telles que la survie des cultures, les cycles de récolte/repontage et l'alimentation/soins des animaux.
- Programmer des travaux optionnels tels que l'extension ou le nettoyage des mauvaises herbes uniquement lorsque la capacité des ouvriers est suffisante.
- Préserver les dépendances entre les tâches afin que les actions se produisent dans un ordre valide.
- Donner une relation de prédécesseur explicite à l'arrosage de survie avant la chaîne correspondante de culture.
- Prioriser la livraison de blé lorsque un autre ouvrier en dépend pour son alimentation.
- Réutiliser la capacité de travail libre des employés pour des tâches à faible priorité et rentable, tant que cela ne menace pas les tâches obligatoires.

**Statut:** mis en œuvre grâce à la génération de tâches temporelles, aux prédécesseurs explicites, aux indicateurs de tâches obligatoires/optionnelles et à la recherche d'attribution bornée.

<a id="5-dynamic-workforce-management"></a>
## 5. Gestion dynamique de l'effectif

Choisir dynamiquement le nombre d'employés à partir de la charge de travail attendue et de la valeur économique de la capacité supplémentaire.

- Rechercher le nombre minimal d'employés nécessaire pour accomplir les tâches requises.
- Tenir compte de la date effective de début et de la position d'apparition des nouveaux employés embauchés.
- Vérifier si les actions obligatoires peuvent encore s'inscrire avant la limite temporelle quotidienne avec les employés actuellement disponibles.
- Comparer la valeur attendue créée par un employé supplémentaire avec le coût de recrutement suivant de la suite de Fibonacci.
- Arrêter les embauches lorsque la valeur supplémentaire attendue ne justifie plus le recrutement du prochain employé.
- Ne pas imposer un maximum artificiel de dix main-d'œuvre.

**Statut:** mis en œuvre.

<a id="6-conditional-watering-and-production-timing"></a>
## 6. Arrosage et calendrier de production conditionnel

Éviter d'employer des actions sur les cultures lorsque l'arrosage ou la production continue ne créent plus de valeur utile.

- Arroser uniquement lorsque cela est nécessaire à la survie des cultures ou lorsque l'arrosage est nécessaire avant une récolte utile.
- Suivre le calendrier des cultures afin que les décisions de récolte et de replantage respectent le cycle de production.
- Éviter de planter ou de replanter des cultures qui ne pourront pas produire avant la dernière vente utile.
- Appliquer la même règle de faisabilité finale aux nouveaux animaux.
- Arrêter la maintenance de la production une fois qu'aucune récolte profitable supplémentaire ne peut être réalisée à temps.

**Statut:** mis en œuvre.

<a id="7-dynamic-production-selection"></a>
## 7. Sélection dynamique de la production

Choisir une nouvelle production en fonction de la rentabilité attendue plutôt qu'un layout fixe après l'ouverture.

- Évaluer les cultures et les animaux pour les cases vides ou bientôt vides.
- Inclure le coût d'achat, le coût de nourriture, le coût du travail, la durée d'occupation et l'occupation spatiale dans l'évaluation.
- Estimer le revenu marginal en utilisant l'état de marché attendu.
- Conserver uniquement les choix de production positifs et accessibles.
- Transformer le plan de production sélectionné en ordres de semences, d'animaux et de marché du blé.

**Statut:** mis en œuvre.

<a id="8-profit-aware-land-expansion"></a>
## 8. Expansion du territoire en fonction de la rentabilité

Considérer l'achat de terres comme un investissement qui doit être justifié par la production pouvant être installée sur ce territoire.

- Estimer la valeur de production disponible sur le nouveau quadrant.
- Inclure les coûts de semences, d'animaux, de nourriture et de recrutement supplémentaire.
- Vérifier la faisabilité avant d'acheter une parcelle de terre.
- Éviter une expansion tardive lorsque le temps restant n'est pas suffisant pour récupérer l'investissement.
- Privilégier l'espace de production utile plutôt que l'expansion automatique.

**Statut:** mis en  œuvre.

<a id="9-market-aware-valuation-and-sales"></a>
## 9. Évaluation et ventes en fonction du marché

Utiliser l'évolution attendue du marché lorsqu'on décide de produire ou de vendre.

- Estimer les prix futurs à partir de l'inventaire actuel, de l'offre prévue, de la demande des magasins et de l'offre visible des concurrents publics.
- Simuler les ventes projetées par unité au lieu de supposer un prix de vente fixe unique.
- Évaluer l'incertitude de l'adversaire avec des scénarios alternatifs de fourniture ou de timing au lieu de supposer un modèle exact futur de vente de l'adversaire.
- Vendre continuellement les produits récoltés lorsqu'il est approprié au lieu d'attendre une liquidation globale.
- Vendre plus activement lorsque des fonds sont nécessaires ou lorsque la pression s'accentue, tout en conservant une réserve de blé pour les animaux actifs.
- Mesurer les ventes de produits sensibles au prix afin d'éviter une influence excessive sur le prix.
- Permettre la vente indépendante de l'engrais.
- Liquidation de l'inventaire restant vendable à la fin de la journée 29.

**Statut :** mis en œuvre dans toute la famille de planificateurs CHI9/CHI10 conservés.

<a id="10-shed-and-inventory-logistics"></a>
## 10. Gestion de la décharge et des logistiques

Considérer la décharge comme un point de logistique contraint au lieu d'un simple emplacement de stockage passif.

- Diriger les ouvriers vers la case la plus proche d'accès à la décharge lorsqu'ils retournent des produits ou collectent des ressources.
- Utiliser les quatre cases d'accès valides à la décharge lors du choix des itinéraires de retour.
- Tenir compte des produits transportés par les ouvriers et des produits déposés durant le tour actuel.
- Prévenir les surcharges de décharge lors de la planification des récoltes et des ventes.
- Coordonner la récolte de blé, le dépôt à la décharge et la récupération ultérieure lorsque l'alimentation des animaux dépend du blé produit durant la même journée.
- Représenter les ressources partagées avec un tick d'indisponibilité afin qu'un ouvrier puisse attendre une ressource que l'autre déposera plus tard.
- Permettre à un ouvrier déjà transportant du blé de créer une tâche de livraison explicite pour un autre ouvrier.

**Statut :** mis en œuvre.

<a id="11-animal-production-management"></a>
## 11. Gestion de la production animale

Gérer les animaux en fonction de leur état de production, de leur dépendance alimentaire et de leur capacité utile restante.

- Récolter les produits disponibles des animaux et collecter l'engrais avant de commencer le cycle suivant de nourrissage ou d'entretien, lorsque cela est approprié.
- Assurer que les tâches dépendantes de nourrissage soient reportées jusqu'à ce que suffisamment de blé soit disponible.
- Éviter les actions inutiles de CARE lorsque le bonus en attente et la production en attente s'approchent déjà de la capacité utile de l'animal.
- Inclure les effets de CARE lors de l'estimation de la valeur de production animale.
- Arrêter l'entretien des animaux lorsque aucune vente utile future ne reste ou lorsque le bénéfice estimé restant sur les animaux devient négatif.
- Grouper les tâches liées aux animaux lorsque cela réduit la fragmentation des itinéraires.

**Statut :

<a id="12-observation-checked-execution"></a>
## 12. Exécution vérifiée par observation

Ne pas exécuter de manière aveugle une pile d'actions précédemment générée lorsque l'observation actuelle ne correspond plus aux hypothèses utilisées pour la créer.

- Valider les actions planifiées des ouvriers contre l'état actuel du jeu.
- Vérifier la disponibilité des stocks de semences partagés, des stocks de décharge, des récoltes des ouvriers, des mutations de cases et de la capacité de décharge dans l'ordre d'exécution de l'engine avant de retourner les actions.
- Réactualiser l'état de production lorsque le contenu ou le type de production d'une case change.
- Recalculer les informations relatives aux ventes et à l'inventaire lorsque des produits sont déposés durant le tour actuel.
- Remplacer les actions planifiées invalides par `PASS` au lieu d'exécuter aveuglément une action périmée.

**Statut :** implémenté dans `chi10_temporal.py`.

<a id="13-bounded-temporal-scheduling"></a>
## 13. Planification temporelle bornée

Planifier du travail avec une heure explicite au lieu d'attribuer simplement une liste ordonnée de tâches à chaque ouvrier.

- Représenter chaque tâche avec sa position, sa séquence d'action, sa valeur attendue, son statut requis/optionnel et ses dépendances précedentes.
- Représenter chaque ouvrier avec sa position actuelle, son heure actuelle, son inventaire et sa séquence d'action temporelle.
- Inclure le temps de déplacement, le temps de récupération, le temps d'attente des ressources et le temps d'action dans les vérifications de faisabilité.
- Réserver les stocks partagés en fonction de la minute à laquelle chaque quantité devient disponible.
- Imposer la deadline réelle de fin de journée, y compris la deadline plus courte de la dernière journée requise pour vendre les biens déposés avant la fin de l'épisode.
- Utiliser une recherche bornée petite pour conserver plusieurs alternatives d'affectation ouvrier/tâche sans rendre la planification exhaustive prohibitivement coûteuse.
- Permettre de sauter les tâches optionnelles lorsque cela permet une continuation meilleure ou plus faisable du calendrier.

**Statut :** implémenté.

<a id="14-tick-by-tick-worker-replanning"></a>
## 14. Réplanification en temps réel des ouvriers

Ne pas exécuter une seule route fixe d'ouvrier pendant toute la journée lorsque l'état du jeu peut avoir changé.

- Reconstruire l'ensemble temporel des tâches en temps réel à chaque appel de l'agent.
- Recalculer les affectations des ouvriers en utilisant leurs positions réelles, leurs inventaires, les stocks observés des ateliers et les états des tuiles actuels.
- Réplanifier autour des ressources devenues disponibles, des tâches déjà terminées ou des actions devenues invalides.
- Conserver le plan de production quotidien, les décisions de recrutement, les plans de terrain et de marché, tout en réplanifiant continuellement la couche d'exécution des ouvriers.
- Enregistrer uniquement le nouveau calendrier temporel pour l'observation actuelle et valider l'action due au tick actuel avant son exécution.

**Statut :** implémenté dans `chi10_temporal.py`.

<a id="15-public-shop-order-production-prior"></a>
## 15. Priorité de production basée sur les commandes des magasins publics

Utiliser l'ordre des magasins publiquement débloqués comme un signal de demande faible lorsque plusieurs candidats à la production ont déjà des scores économiques similaires.

- Associer chaque culture ou animal à son produit de marché.
- Comparer ce produit avec la demande des deux premiers magasins débloqués.
- Appliquer uniquement un petit multiplicateur afin que le modèle de rentabilité marginale sous-jacent reste le critère principal de décision.
- Utiliser uniquement des informations déjà présentes dans l'observation publique.

**Statut :** implémenté dans `chi11.py`. Le premier magasin débloqué applique un multiplicateur de 8 % sur le score de production et le deuxième un multiplicateur de 3 % lorsque la sortie candidate correspond à la demande du magasin concerné.

<a id="16-public-farm-similarity-and-clone-aware-sales"></a>
## 16. Similarité entre les fermes publiques et ventes conscientes des clones

Utiliser la similarité répétée entre les deux fermes visibles publiquement comme un signal faible indiquant que des actions simultanées peuvent créer une collision de marché évitable.

- Construire une signature publique compacte à partir du nombre de cultures, du nombre d'animaux, des quadrants débloqués et du nombre d'ouvriers sur la ferme.
- Exiger que la similarité persiste sur de nombreux tours consécutifs avant d'activer tout comportement spécial.
- Ne pas utiliser l'identité de l'adversaire, les inventaires cachés, les identifiants d'épisode, les recherches de reprise ou les actions futures.
- Lorsque la condition est active, réduisez la taille du lot de vente ordinaire plutôt que de remplacer la politique de vente de base.
- Ne jamais restreindre la liquidation finale.

**Statut :** mis en œuvre dans `chi11.py`. La détection commence à l'étape 48, exige une distance de signature de au plus 2 sur 24 tours consécutifs et peut être activée à l'étape 160. Les quantités de VENTE ordinaires sont limitées à 10 unités pendant que la condition est active.

<a id="17-market-impact-aware-sell-ordering"></a>
## 17. Ordre de VENTE conscient de l'impact sur le marché

Lorsque plusieurs ordres de VENTE existent déjà dans la même action de marché, privilégiez ceux qui sont les plus exposés à leur propre impact de prix.

- Estimer le prix post-vente en utilisant l'inventaire public actuel et le modèle de prix unitaire existant.
- Classer les emplacements de VENTE existants selon la perte estimée immédiate.
- Réorganiser uniquement les ordres de VENTE.
- Préserver tous les emplacements de marché non VENTE et ne pas créer de nouvelles ventes.

**Statut :** mis en œuvre dans `chi11.py`.

<a id="18-standalone-submission-packaging"></a>
## 18. Empaquetage de soumission autonome

Garantir que l'agent de concurrence reste directement soumis comme un seul fichier Python, même si une version de développement dépendrait autrement d'un module local.

- Intégrer directement l'implémentation de l'agent de base conservé dans le fichier de soumission.
- Éliminer les imports locaux au projet dans le fichier final de concurrence.
- Conserver l'entrée publique `agent(obs)` inchangée.
- Préserver le comportement de l'agent de base et appliquer le recouvrement expérimental autour d'une seule appel à l'agent de base.

**Statut :** mis en œuvre pour CHI 11. `chi11.py` contient le planneur de base de CHI 10 et le recouvrement de CHI 11 dans un seul fichier autonome.

<a id="19-public-route-baseline"></a>
## 19. Base de référence routière publique

Conserver un agent de route fixe fort comme base expérimentale séparée, au lieu de mélanger directement son bandeau d'action dans le planneur CHI.

- Stocker la route publique sous forme lisible en Python afin que chaque jour, heure et action puisse être inspecté et modifié.
- Conserver exactement la séquence d'action initiale dans la première base de référence.
- Maintenir les expériences basées sur la route séparées de la famille de planneurs CHI afin que les améliorations puissent être attribuées clairement.
- Utiliser la route publique comme référence concurrente et améliorer la robustesse autour d'elle avant de modifier sa stratégie macro.

**Statut :** mis en œuvre dans `jet.py`. La route compressée v27 a été étendue mécaniquement en 719 actions lisibles sans modifier leur contenu.

<a id="20-staged-runtime-fallbacks"></a>
## 20. Retours progressifs en temps réel

Ne pas abandonner un tick complet de route lorsque l'une des corrections de temps réel optionnelles soulève une exception.

- Conserver l'action de route de base avant d'appliquer les recouvrements en temps réel.
- Isoler la réparation WEED, la liquidation finale et l'ordre de VENTE dans des étapes séparées protégées.
- Si un recouvrement échoue, conserver l'action valide la plus récente au lieu de retourner une série complète de tours `PASS`.
- Réserver le retour complet `PASS` au cas où aucune action de route utilisable ne peut être récupérée.

**Statut :** mis en œuvre dans `jet1.py`.

<a id="21-observation-based-final-liquidation"></a>
## 21. Liquidation finale basée sur les observations

Remplacer les quantités fixes de vente finale d'un ruban de route par une liquidation fondée sur l'inventaire effectivement vendable à l'étape ultime actionable.

- Déterminer l'étape ultime actionable à partir de `episodeSteps`.
- Lire le contenu réel des hangars au lieu de se fier aux quantités préenregistrées de fin de vente.
- Inclure les produits déposés par des actions du même tick `DROP` avant de construire les ordres VENTE finaux.
- Respecter la limite configurée pour les ordres de marché.
- Laisser le trajet inchangé à chaque étape antérieure.

**Statut :** mis en œuvre dans `jet1.py`.
