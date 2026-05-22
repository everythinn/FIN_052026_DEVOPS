# FIN_052026_DEVOPS — Feature Flags API

API REST de gestion de feature flags développée avec FastAPI.

## Stack technique

- **Python 3.12**
- **FastAPI** — framework REST
- **Pydantic** — validation des données
- **Pytest** — tests unitaires et d'intégration
- **Ruff** — linting
- **Docker** — containerisation
- **Scaleway** — déploiement serverless

## Lancer le projet en local

```bash
# Créer et activer l'environnement virtuel
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Installer les dépendances
pip install -r requirements.txt

# Lancer le serveur
uvicorn src.main:app --reload
```

L'API est disponible sur `http://localhost:8000`
La documentation Swagger est disponible sur `http://localhost:8000/docs`

## Lancer les tests

```bash
# Tests uniquement
pytest tests/ -v

# Tests avec coverage
pytest tests/ -v --cov=src --cov-report=term-missing
```

## Structure du projet
FIN_052026_DEVOPS/
├── src/
│   ├── main.py
│   ├── storage.py
│   ├── models/
│   │   ├── user.py
│   │   ├── group.py
│   │   ├── environment.py
│   │   └── feature.py
│   ├── routers/
│   │   ├── users.py
│   │   ├── groups.py
│   │   ├── environments.py
│   │   └── features.py
│   └── services/
│       └── feature_evaluator.py
├── tests/
│   ├── test_health.py
│   ├── test_users.py
│   ├── test_groups.py
│   ├── test_environments.py
│   ├── test_features.py
│   ├── test_evaluate_unit.py
│   └── test_evaluate_integration.py
├── Dockerfile
├── requirements.txt
└── README.md

## Documentation API

### Healthcheck
| Méthode | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Statut de l'API |
| GET | `/api/version` | Version de l'API |

### Users
| Méthode | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/users` | Créer un utilisateur |
| GET | `/api/users` | Lister les utilisateurs |
| GET | `/api/users/:id` | Récupérer un utilisateur |
| PATCH | `/api/users/:id` | Modifier un utilisateur |
| DELETE | `/api/users/:id` | Supprimer un utilisateur |

### Groups
| Méthode | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/groups` | Créer un groupe |
| GET | `/api/groups` | Lister les groupes |
| GET | `/api/groups/:id` | Récupérer un groupe |
| PATCH | `/api/groups/:id` | Modifier un groupe |
| DELETE | `/api/groups/:id` | Supprimer un groupe |
| POST | `/api/groups/:id/users/:userId` | Ajouter un user au groupe |
| DELETE | `/api/groups/:id/users/:userId` | Retirer un user du groupe |
| GET | `/api/groups/:id/users` | Lister les users d'un groupe |

### Environments
| Méthode | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/environments` | Créer un environnement |
| GET | `/api/environments` | Lister les environnements |
| GET | `/api/environments/:name` | Récupérer un environnement |
| PATCH | `/api/environments/:name` | Modifier un environnement |
| DELETE | `/api/environments/:name` | Supprimer un environnement |

### Features
| Méthode | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/features` | Créer une feature |
| GET | `/api/features` | Lister les features |
| GET | `/api/features/:key` | Récupérer une feature |
| PATCH | `/api/features/:key` | Modifier une feature |
| DELETE | `/api/features/:key` | Supprimer une feature |
| PATCH | `/api/features/:key/enable` | Activer une feature |
| PATCH | `/api/features/:key/disable` | Désactiver une feature |

### Feature Config
| Méthode | Endpoint | Description |
|--------|----------|-------------|
| PUT | `/api/features/:key/environments/:env/config` | Configurer une feature par env |
| GET | `/api/features/:key/environments/:env/config` | Récupérer la config |
| DELETE | `/api/features/:key/environments/:env/config` | Supprimer la config |

### Evaluate ⭐
| Méthode | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/features/:key/evaluate?userId=1&env=prod` | Évaluer l'accès d'un user |

Réponse :
```json
{
  "feature": "new-dashboard",
  "enabled": true,
  "reason": "user belongs to allowed group beta-testers"
}
```

## Règles d'évaluation

Une feature est accessible si :
1. Elle existe
2. Elle est activée globalement
3. Elle est activée dans l'environnement demandé
4. ET l'utilisateur est explicitement autorisé **OU** appartient à un groupe autorisé **OU** fait partie du rollout

## CI/CD

Chaque push déclenche :
- ✅ Lint avec Ruff
- ✅ Tests avec Pytest (100% coverage)

Chaque merge sur `main` déclenche en plus :
- 🐳 Build de l'image Docker
- 🚀 Push sur Scaleway Container Registry
- ☁️ Déploiement sur Scaleway Serverless