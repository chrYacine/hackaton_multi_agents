# 🗺️ Roadmap V2 - Multi-Agent System

## 📋 État Actuel (V1 - Complété ✅)

- ✅ Agent 1 - Chat Service (dialogue utilisateur)
- ✅ Agent 2 - Interpretation Service (génération AgentSpec)
- ✅ Agent 3 - Orchestrator Service (génération ExecutionPlan)
- ✅ Agent Debugger - Debug Service (validation statique)
- ✅ Agent 4 - Execution Service (moteur d'exécution avec mocks)

**Architecture** : Hexagonale, modulaire, bien séparée
**Tests** : Scripts de test pour chaque service + end-to-end
**État** : POC fonctionnel avec outils mock

---

## 🎯 Objectif V2

Transformer le POC en système **production-ready** avec :
- Intégrations réelles (Gmail, Groq, Slack)
- Persistance et traçabilité
- Gestion d'erreurs robuste
- Sécurité et monitoring

---

## 📅 Plan d'Attaque V2 (Ordre Recommandé)

### Phase 1 : Intégrations Réelles 🔌
**Priorité** : CRITIQUE  
**Objectif** : Prouver que le système fonctionne avec de vraies API

#### 1.1 Gmail + Groq (Scénario Complet)
- [ ] Implémenter `GmailAuthTool` avec OAuth2 réel
  - Utiliser `google-auth` + `google-api-python-client`
  - Gérer le flow OAuth (credentials, refresh token)
- [ ] Implémenter `GmailFetchTool` avec Gmail API
  - Requêtes avec filtres (is:unread, newer_than, etc.)
  - Parsing des emails (from, subject, snippet, date)
- [ ] Implémenter `LLMSummarizeTool` avec Groq
  - Appel API Groq avec prompt structuré
  - Parsing de la réponse (text + JSON)
- [ ] Tester le flow complet : Auth → Fetch → Summarize

#### 1.2 Slack (Notification)
- [ ] Implémenter `SlackPostTool` avec Webhook
  - Formatage du message (markdown, blocks)
  - Gestion des erreurs Slack
- [ ] Tester le flow complet : Gmail → Groq → Slack

**Livrables** :
- Outils réels dans `infrastructure/tools/`
- Script de test `test_real_integrations.py`
- Documentation des credentials nécessaires

---

### Phase 2 : Gestion des Secrets 🔐
**Priorité** : CRITIQUE (avant prod)  
**Objectif** : Ne jamais exposer de credentials

#### 2.1 SecretProvider Abstraction
- [ ] Créer `interfaces/secret_port.py`
  ```python
  class ISecretProvider(Protocol):
      async def get_secret(self, key: str) -> str
  ```
- [ ] Implémenter `EnvSecretProvider` (lit depuis .env)
- [ ] (Futur) `VaultSecretProvider`, `GCPSecretProvider`

#### 2.2 Intégration dans les Tools
- [ ] Modifier les tools pour utiliser `SecretProvider`
- [ ] Ne jamais logger les secrets (filtrage dans logs)
- [ ] Ajouter validation : secrets requis vs disponibles

**Livrables** :
- Module `execution_service/infrastructure/secrets/`
- `.env.example` avec toutes les clés nécessaires
- Documentation sécurité

---

### Phase 3 : Persistance & Traçabilité 💾
**Priorité** : HAUTE  
**Objectif** : Historique complet, resumabilité, debugging

#### 3.1 Persistance des Résultats
- [ ] Créer `interfaces/storage_port.py`
  ```python
  class IExecutionStorage(Protocol):
      async def save_execution(self, result: ExecutionResult)
      async def get_execution(self, request_id: str) -> ExecutionResult
      async def list_executions(self, filters: dict) -> list[ExecutionResult]
  ```
- [ ] Implémenter `RedisExecutionStorage` (V2.1)
- [ ] Implémenter `PostgresExecutionStorage` (V2.2)

#### 3.2 Correlation ID Global
- [ ] Ajouter `correlation_id` à tous les modèles
  - `AgentSpec.correlation_id`
  - `ExecutionRequest.correlation_id`
  - `ExecutionResult.correlation_id`
- [ ] Propager le `correlation_id` à travers tout le pipeline
- [ ] Logs structurés JSON avec `correlation_id`

#### 3.3 Resumabilité
- [ ] Ajouter `resume_from_step_id` dans `ExecutionRequest`
- [ ] Modifier `ExecutionEngine` pour reprendre à un step donné
- [ ] Charger le context depuis l'état sauvegardé

**Livrables** :
- Module `execution_service/infrastructure/storage/`
- Migration DB (si Postgres)
- Script `test_persistence.py`

---

### Phase 4 : Politiques d'Erreur ⚠️
**Priorité** : HAUTE  
**Objectif** : Gestion robuste des échecs

#### 4.1 Error Policy Configuration
- [ ] Ajouter au modèle `ExecutionRequest` :
  ```python
  error_policy: ErrorPolicy = Field(default_factory=lambda: ErrorPolicy(
      on_tool_error="stop",  # stop | continue | retry
      max_retries=2,
      retry_backoff_sec=5,
      skip_on_non_critical=False
  ))
  ```
- [ ] Marquer certains steps comme `critical: bool`

#### 4.2 Retry Logic
- [ ] Implémenter retry avec backoff exponentiel
- [ ] Logger chaque tentative
- [ ] Limiter le nombre total de retries

#### 4.3 Continue on Error
- [ ] Permettre de continuer si step non-critique échoue
- [ ] Marquer le résultat comme `partial_success`

**Livrables** :
- `ErrorPolicy` dans `domain/models.py`
- Logique retry dans `ExecutionEngine`
- Tests de scénarios d'erreur

---

### Phase 5 : Versioning & Contrats 📜
**Priorité** : MOYENNE  
**Objectif** : Éviter les breaking changes

#### 5.1 Schema Versioning
- [ ] Ajouter `schema_version: str` à :
  - `AgentSpec`
  - `ExecutionPlan`
  - `ExecutionResult`
- [ ] Valider la compatibilité des versions
- [ ] Documenter les changements de version

#### 5.2 Tests de Contrat
- [ ] Créer `tests/contract/` avec :
  - `test_agent_spec_contract.py`
  - `test_execution_plan_contract.py`
- [ ] Valider que les services respectent les contrats

**Livrables** :
- Champ `schema_version` partout
- Suite de tests de contrat
- CHANGELOG.md pour les versions

---

### Phase 6 : Console d'Approbation 🖥️
**Priorité** : MOYENNE  
**Objectif** : Validation humaine avant exécution

#### 6.1 API d'Approbation
- [ ] Créer endpoints :
  - `GET /api/pending-executions` : Liste des plans en attente
  - `POST /api/approve/{request_id}` : Approuver un plan
  - `POST /api/reject/{request_id}` : Rejeter un plan

#### 6.2 UI Simple (Streamlit ou FastAPI + HTML)
- [ ] Page listant les plans en attente
- [ ] Affichage détaillé : steps, outils, paramètres
- [ ] Boutons Approve ✅ / Reject ❌
- [ ] Historique des exécutions

**Livrables** :
- Module `approval_service/`
- UI accessible sur port 8001
- Documentation utilisateur

---

### Phase 7 : Limites & Sécurité 🛡️
**Priorité** : MOYENNE  
**Objectif** : Éviter les abus et timeouts

#### 7.1 Timeouts & Limites
- [ ] Ajouter `timeout_sec` par step
- [ ] Limiter la taille des données :
  - `max_emails` dans Gmail fetch
  - `max_summary_length` dans LLM
- [ ] Timeout global par exécution

#### 7.2 Kill Switch
- [ ] Endpoint `POST /api/cancel/{request_id}`
- [ ] Arrêter une exécution en cours
- [ ] Marquer comme `cancelled` dans la DB

#### 7.3 Rate Limiting
- [ ] Limiter le nombre d'exécutions par utilisateur
- [ ] Limiter les appels API externes (quotas)

**Livrables** :
- Configuration des limites dans `.env`
- Endpoint de cancellation
- Tests de timeout

---

### Phase 8 : Monitoring & Métriques 📊
**Priorité** : BASSE (après stabilisation)  
**Objectif** : Observabilité production

#### 8.1 Logs Structurés
- [ ] Passer tous les logs en JSON structuré
- [ ] Ajouter contexte : `correlation_id`, `request_id`, `step_id`
- [ ] Niveaux appropriés (DEBUG, INFO, WARNING, ERROR)

#### 8.2 Métriques Basiques
- [ ] Durée totale par exécution
- [ ] Nombre de steps OK / KO
- [ ] Types d'erreurs les plus fréquents
- [ ] Taux de succès par agent_type

#### 8.3 Monitoring Avancé (Optionnel)
- [ ] Intégration Prometheus + Grafana
- [ ] Alertes sur taux d'erreur élevé
- [ ] Dashboard temps réel

**Livrables** :
- Logs JSON dans `logs/`
- Script d'analyse `analyze_metrics.py`
- (Optionnel) Dashboard Grafana

---

### Phase 9 : Exécution Parallèle ⚡
**Priorité** : BASSE (optimisation)  
**Objectif** : Accélérer les plans avec steps indépendants

#### 9.1 Détection de Dépendances
- [ ] Analyser le DAG des steps (qui dépend de quoi)
- [ ] Marquer les steps parallélisables

#### 9.2 Exécution Async Parallèle
- [ ] Utiliser `asyncio.gather()` pour steps indépendants
- [ ] Gérer les erreurs en parallèle

**Livrables** :
- Logique de parallélisation dans `ExecutionEngine`
- Tests de performance (before/after)

---

## 🎯 Ordre d'Attaque Recommandé

```
1. Gmail + Groq réels (Phase 1.1)           ← Prouve que ça marche
2. Secrets (Phase 2)                        ← Sécurise avant d'aller plus loin
3. Persistance + Correlation (Phase 3)      ← Traçabilité essentielle
4. Error Policy (Phase 4)                   ← Robustesse
5. Slack réel (Phase 1.2)                   ← Complète le scénario
6. Versioning (Phase 5)                     ← Prépare l'évolution
7. Console d'Approbation (Phase 6)          ← UX pour le "commandeur"
8. Limites & Sécurité (Phase 7)             ← Prod-ready
9. Monitoring (Phase 8)                     ← Observabilité
10. Parallélisme (Phase 9)                  ← Optimisation finale
```

---

## 📝 Notes Importantes

### Pourquoi cet ordre ?

1. **Gmail + Groq d'abord** : Prouve que le système fonctionne end-to-end avec de vraies API
2. **Secrets ensuite** : Évite de commiter des credentials par accident
3. **Persistance tôt** : Essentielle pour debugger les intégrations réelles
4. **Error policy avant Slack** : Sinon tu vas spammer Slack en cas d'erreur
5. **Parallélisme en dernier** : Ne pas débugger parallélisme + intégrations en même temps

### Risques à Surveiller

- **Quotas API** : Gmail/Groq ont des limites, prévoir des mocks pour les tests
- **OAuth Refresh** : Gérer le renouvellement des tokens Gmail
- **Coûts LLM** : Groq peut devenir cher, monitorer l'usage
- **Complexité** : Ne pas tout faire en même temps, valider chaque phase

---

## 🚀 Quick Wins (Gains Rapides)

Si tu veux des résultats visibles rapidement :

1. **Gmail réel** (1-2 jours) → Démo impressionnante
2. **Correlation ID** (2h) → Debug 10× plus facile
3. **Logs JSON** (1h) → Exploitabilité immédiate
4. **Error retry** (3h) → Robustesse perçue

---

## 📚 Ressources Nécessaires

### APIs & SDKs
- `google-auth`, `google-api-python-client` (Gmail)
- `groq` SDK Python
- `slack-sdk` ou webhooks simples
- `redis-py` ou `asyncpg` (persistance)

### Infrastructure
- Redis (local ou cloud) pour cache/state
- PostgreSQL (optionnel, pour persistance durable)
- .env pour secrets locaux
- (Futur) GCP Secret Manager / HashiCorp Vault

---

## ✅ Critères de Succès V2

- [ ] Un scénario complet fonctionne avec vraies API (Gmail → Groq → Slack)
- [ ] Aucun secret en clair dans le code ou les logs
- [ ] Tous les `ExecutionResult` sont persistés et traçables
- [ ] Les erreurs sont gérées avec retry automatique
- [ ] Un humain peut approuver/rejeter un plan via UI
- [ ] Le système tourne 24h sans crash
- [ ] Les métriques de base sont disponibles

---

**Prêt à attaquer la Phase 1 ? 🚀**
