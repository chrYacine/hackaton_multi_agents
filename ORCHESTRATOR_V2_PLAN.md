# 🎯 Plan de Finalisation - Orchestrator V2

## 📋 Objectif

Transformer l'Orchestrator V1 (POC) en Orchestrator V2 (production-ready) avant d'attaquer les intégrations réelles.

**Stratégie** : D'abord le cerveau, ensuite les muscles 🧠💪

---

## ✅ État Actuel (V1)

L'orchestrateur fait déjà :
- ✅ Reçoit un `AgentSpec`
- ✅ Classifie le `agent_type` (EMAIL_SUMMARY_AGENT, etc.)
- ✅ Génère un `AgentInstance`
- ✅ Génère un `ExecutionPlan` structuré avec steps et tools

**Verdict** : POC fonctionnel, logique validée ✅

---

## 🎯 Orchestrator V2 - 5 Améliorations Clés

### A. Pipeline Clair à 4 Étapes

Transformer l'orchestrateur en workflow déterministe :

```
1. Validation/Debug pré-plan
   ↓
2. Classification & Strategy
   ↓
3. Plan Generation
   ↓
4. Handoff (optionnel)
```

#### 1️⃣ Validation/Debug Pré-Plan
- [ ] Appel interne au Debug Service sur l'AgentSpec
- [ ] Si `invalid` → ne pas générer de plan
- [ ] Retourner `debug_report` + `status="blocked"`
- [ ] Évite de générer des plans invalides

**Bénéfice** : Détection précoce des problèmes

#### 2️⃣ Classification & Strategy
- [ ] Mapping `agent_type` → `plan_strategy`
- [ ] Stocké dans config (YAML/JSON), pas hard-codé
- [ ] Extensible sans modifier le code

**Bénéfice** : Ajout de nouveaux agents sans toucher au code

#### 3️⃣ Plan Generation
- [ ] Génère `ExecutionPlan` avec :
  - `plan_id`
  - `agent_type`
  - `schema_version` ✨ (nouveau)
  - `steps` avec `is_critical` ✨ (nouveau)
  - `correlation_id` ✨ (nouveau)

**Bénéfice** : Plans versionnés et traçables

#### 4️⃣ Handoff vers Executor
Deux options :

**Option A** (Recommandée) : Orchestrator = Planner pur
- Retourne juste le plan
- L'Executor est appelé séparément
- Séparation des responsabilités claire

**Option B** : Orchestrator = Planner + Launcher
- Flag `auto_execute: bool` dans la requête
- Si `true`, appelle `/api/execute` automatiquement
- Plus pratique mais couplage plus fort

**Choix recommandé** : Option A pour V2

---

### B. Normaliser les Contrats

#### Contrat d'Entrée (Request)
```json
{
  "request_id": "uuid",
  "correlation_id": "uuid",  // ✨ Nouveau (optionnel, généré si absent)
  "user_id": "yacine",
  "agent_spec": {
    "schema_version": "1.0",  // ✨ Nouveau
    "agent_type": "EMAIL_SUMMARY_AGENT",
    "user_intent": { ... },
    "inputs": { ... },
    "outputs": { ... }
  }
}
```

#### Contrat de Sortie (Response)
```json
{
  "request_id": "uuid",
  "correlation_id": "uuid",  // ✨ Nouveau
  "status": "planned" | "blocked",  // ✨ Nouveau
  "agent_instance": {
    "schema_version": "1.0",  // ✨ Nouveau
    "agent_id": "uuid",
    "agent_type": "EMAIL_SUMMARY_AGENT",
    "config": { ... }
  },
  "execution_plan": {
    "schema_version": "1.0",  // ✨ Nouveau
    "plan_id": "uuid",
    "correlation_id": "uuid",  // ✨ Nouveau
    "agent_type": "EMAIL_SUMMARY_AGENT",
    "steps": [
      {
        "step_id": "1",
        "name": "Connect to Gmail",
        "tool": "gmail_auth",
        "parameters": {},
        "is_critical": true  // ✨ Nouveau
      }
    ]
  },
  "approval": {  // ✨ Nouveau
    "required": true,
    "approved": false,
    "approved_by": null,
    "approved_at": null
  },
  "debug_report": null  // ✨ Nouveau (si validation échoue)
}
```

**Tâches** :
- [ ] Ajouter `schema_version` à tous les modèles
- [ ] Ajouter `is_critical` aux steps
- [ ] Ajouter `approval` object
- [ ] Ajouter `debug_report` (si validation échoue)
- [ ] Documenter les contrats dans le code

---

### C. Correlation ID Global

#### Implémentation
- [ ] Si `correlation_id` absent dans la requête → générer un UUID
- [ ] Propager à travers tous les composants :
  - `AgentInstance.correlation_id`
  - `ExecutionPlan.correlation_id`
  - Logs structurés
  - Appels au Debug Service
  - Appels à l'Executor

#### Exemple de Log Structuré
```json
{
  "timestamp": "2025-11-26T10:30:00Z",
  "level": "INFO",
  "correlation_id": "f37c-...",
  "request_id": "2b08b15a-...",
  "service": "orchestrator",
  "message": "Plan generated successfully",
  "agent_type": "EMAIL_SUMMARY_AGENT",
  "plan_id": "eb7e48..."
}
```

**Bénéfice** : Traçage end-to-end du pipeline complet

---

### D. Intégration de l'Approbation ("Commandeur")

#### Workflow d'Approbation

```
1. Orchestrator génère le plan
   ↓
2. Retourne approval.required = true, approved = false
   ↓
3. Plan stocké en "pending" (future DB)
   ↓
4. Commandeur review via UI Console (future)
   ↓
5. Commandeur approve → approval.approved = true
   ↓
6. Executor vérifie approval avant exécution
```

#### Implémentation V2
- [ ] Ajouter `approval` object dans la réponse
- [ ] Executor vérifie `approval.approved` (déjà partiellement fait)
- [ ] Bloquer strictement si `approved = false`
- [ ] Logger qui a approuvé et quand

#### Future (V3)
- [ ] Endpoint `POST /api/orchestrate/{plan_id}/approve`
- [ ] UI Console pour lister et approuver les plans
- [ ] Persistance des plans en attente

**Bénéfice** : Sécurité - aucune exécution sans validation humaine

---

### E. Configuration Driven (YAML/JSON)

#### Structure de Config Proposée

**Fichier** : `orchestrator_service/config/agent_types.yaml`

```yaml
schema_version: "1.0"

agent_types:
  EMAIL_SUMMARY_AGENT:
    description: "Agent qui résume des emails Gmail et envoie un rapport"
    category: "email_automation"
    steps:
      - id: "1"
        name: "Connect to Gmail"
        description: "Authenticate with Gmail API"
        tool: "gmail_auth"
        critical: true
        parameters: {}
        
      - id: "2"
        name: "Fetch Emails"
        description: "Retrieve unread emails"
        tool: "gmail_fetch"
        critical: true
        parameters:
          filter: "is:unread newer_than:30m"
          
      - id: "3"
        name: "Summarize with LLM"
        description: "Generate summary using Groq"
        tool: "llm_summarize"
        critical: true
        parameters:
          format: "structured"
          
      - id: "4"
        name: "Post to Slack"
        description: "Send summary to Slack"
        tool: "slack_post"
        critical: false
        parameters:
          channel: "#email-summaries"

  SLACK_NOTIFIER_AGENT:
    description: "Agent qui envoie des notifications Slack"
    category: "notification"
    steps:
      - id: "1"
        name: "Prepare Message"
        tool: "message_formatter"
        critical: true
        
      - id: "2"
        name: "Send to Slack"
        tool: "slack_post"
        critical: true
```

#### Implémentation
- [ ] Créer `orchestrator_service/config/agent_types.yaml`
- [ ] Créer `ConfigLoader` pour charger la config
- [ ] Modifier `PlanGenerator` pour utiliser la config
- [ ] Valider la config au démarrage
- [ ] Ajouter tests pour la config

**Bénéfice** : Ajout de nouveaux agents sans modifier le code Python

---

## 📅 Plan d'Implémentation

### Phase 1 : Contrats & Versioning (1 jour)
- [ ] Ajouter `schema_version` aux modèles
- [ ] Ajouter `is_critical` aux steps
- [ ] Ajouter `approval` object
- [ ] Mettre à jour les tests

### Phase 2 : Correlation ID (0.5 jour)
- [ ] Générer/propager `correlation_id`
- [ ] Ajouter aux logs
- [ ] Mettre à jour les tests

### Phase 3 : Validation Pré-Plan (0.5 jour)
- [ ] Appeler Debug Service avant génération
- [ ] Retourner `debug_report` si invalide
- [ ] Tester le workflow

### Phase 4 : Configuration YAML (1 jour)
- [ ] Créer `agent_types.yaml`
- [ ] Implémenter `ConfigLoader`
- [ ] Refactorer `PlanGenerator`
- [ ] Tests de la config

### Phase 5 : Approbation Stricte (0.5 jour)
- [ ] Renforcer la vérification dans Executor
- [ ] Logger les approbations
- [ ] Tests d'approbation

**Total estimé : 3.5 jours**

---

## 🎯 Critères de Succès V2

- [ ] Tous les modèles ont `schema_version`
- [ ] `correlation_id` propagé partout
- [ ] Validation pré-plan fonctionnelle
- [ ] Config YAML pour au moins 2 agent_types
- [ ] Approbation strictement vérifiée
- [ ] Logs structurés JSON avec correlation_id
- [ ] Tests passent pour tous les scénarios
- [ ] Documentation à jour

---

## 🔄 Après Orchestrator V2

Une fois l'orchestrateur finalisé, on attaque les intégrations réelles :

1. **Gmail API** (OAuth2 + fetch)
2. **Groq LLM** (résumés réels)
3. **Slack API** (notifications réelles)
4. **Persistance** (Redis/Postgres)
5. **Secret Management** (SecretProvider)

---

## 📊 Comparaison V1 vs V2

| Fonctionnalité | V1 (POC) | V2 (Production-Ready) |
|----------------|----------|----------------------|
| Génération de plan | ✅ | ✅ |
| Validation pré-plan | ❌ | ✅ |
| Schema versioning | ❌ | ✅ |
| Correlation ID | ❌ | ✅ |
| Config YAML | ❌ | ✅ |
| Approbation stricte | ⚠️ Warning | ✅ Bloquant |
| Steps critiques | ❌ | ✅ |
| Logs structurés | ⚠️ Basique | ✅ JSON |

---

## 💡 Pourquoi Cette Approche ?

**Cerveau d'abord, muscles ensuite** 🧠💪

1. **Stabilité** : Orchestrateur = cœur du système
2. **Testabilité** : Facile à tester avec mocks
3. **Évolutivité** : Config YAML = ajout d'agents sans code
4. **Traçabilité** : Correlation ID = debug facile
5. **Sécurité** : Approbation stricte = contrôle total

Une fois le cerveau solide, brancher les muscles (APIs réelles) sera beaucoup plus simple et sûr.

---

**Prêt à attaquer l'Orchestrator V2 ? 🚀**
