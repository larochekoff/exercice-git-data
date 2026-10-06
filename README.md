#exercice-git-data
# Exercice MLOps - Démarche Data Science

## 1. Fiche de cadrage
* **Objectif métier** : Prédire le risque de défaut de paiement bancaire pour sécuriser les décisions d'octroi de crédit.
* **Métrique de succès** : ROC-AUC >= 0.80 et Rappel (Recall) >= 0.75 sur les clients à risque.
* **Type de problème** : Classification binaire.

## 2. Jeu de données
* **Source** : Données clients et historiques financiers (`credit_data.csv`).
* **Stockage** : Stocké dans le dossier `data/` (exclu de Git via `.gitignore`).

## 3. Démarche et modélisation
* **Baseline** : Modèle de Régression Logistique.
* **Limites identifiées** : Sensibilité au déséquilibre de classes et présence de valeurs manquantes.