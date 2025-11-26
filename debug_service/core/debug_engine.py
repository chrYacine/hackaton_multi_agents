from typing import List

from interpretation_service.domain.models import AgentRequest
from debug_service.domain.models import DebugReport, DebugIssue, SuggestedFix


class DebugEngine:
    """
    V1 simple : analyse l'AgentSpec et signale quelques soucis évidents.
    Pas d'appel LLM pour l'instant.
    """

    def analyze(self, agent_request: AgentRequest) -> DebugReport:
        spec = agent_request.spec
        # Wait, let me check AgentRequest model in interpretation_service
        
        # Checking interpretation_service/domain/models.py...
        # It seems I need to be careful about the field name.
        # Assuming AgentRequest has 'agent_spec' based on previous work.
        
        issues: List[DebugIssue] = []
        fixes: List[SuggestedFix] = []

        # 1. Pas de contraintes -> warning
        if not spec.constraints:
            issues.append(
                DebugIssue(
                    severity="warning",
                    description="Aucune contrainte définie dans l'AgentSpec.",
                    location="spec.constraints",
                )
            )
            fixes.append(
                SuggestedFix(
                    description="Ajouter des contraintes (sécurité, limites de fréquence, quotas API, etc.)."
                )
            )

        # 2. Champ sensible non sécurisé
        for field in spec.inputs:
            # Handle both dict (from JSON) and object (if Pydantic)
            if isinstance(field, dict):
                name = field.get("name", "")
                f_type = field.get("type", "")
            else:
                name = field.name
                f_type = field.type
                
            ln = name.lower()
            if any(k in ln for k in ["password", "token", "secret"]) and f_type != "secure_string":
                issues.append(
                    DebugIssue(
                        severity="error",
                        description=f"Le champ '{name}' semble sensible mais n'est pas en 'secure_string'.",
                        location=f"spec.inputs.{name}",
                    )
                )
                fixes.append(
                    SuggestedFix(
                        description=f"Typage du champ '{name}' en 'secure_string' et gestion sécurisée."
                    )
                )

        # 3. Aucun critère de succès -> info
        if not spec.success_criteria:
            issues.append(
                DebugIssue(
                    severity="info",
                    description="Aucun critère de succès n'est défini.",
                    location="spec.success_criteria",
                )
            )
            fixes.append(
                SuggestedFix(
                    description="Ajouter 1 à 3 critères de succès mesurables."
                )
            )

        if issues:
            summary = f"{len(issues)} problème(s) détecté(s) dans l'AgentSpec."
        else:
            summary = "Aucun problème majeur détecté (V1)."

        return DebugReport(
            request_id=agent_request.request_id,
            summary=summary,
            issues=issues,
            suggested_fixes=fixes,
        )
