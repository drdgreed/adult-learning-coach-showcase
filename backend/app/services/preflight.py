"""
Preflight checks — validate API keys, models, and account balances
before starting a long transcription + analysis pipeline.

Why bother? Without these checks:
  - A bad model name fails AFTER a 10-minute video upload
  - A negative AssemblyAI balance fails AFTER a 10-minute video upload
  - A bad API key fails after wasting the user's time

With these checks, we fail fast (in < 5 seconds) with a clear,
actionable error message BEFORE any expensive work begins.

Checks performed:
  1. Anthropic API key is valid
  2. Configured Claude model actually exists
  3. AssemblyAI API key is valid and account balance is not negative

Usage:
    checker = PreflightChecker()
    result = checker.run()
    if not result.ok:
        raise Exception(result.error_message)
"""

import httpx
from dataclasses import dataclass, field

import anthropic
import assemblyai as aai

from app.config import settings


@dataclass
class PreflightResult:
    """The result of all preflight checks."""
    ok: bool                              # True only if ALL checks passed
    checks: dict = field(default_factory=dict)  # Per-check results for logging
    error_message: str = ""              # Human-readable summary if ok=False

    def summary(self) -> str:
        """Return a formatted summary of all check results for the log."""
        lines = ["🔍 [PREFLIGHT] Results:"]
        for name, result in self.checks.items():
            icon = "✅" if result["passed"] else "❌"
            lines.append(f"  {icon} {name}: {result['message']}")
        return "\n".join(lines)


class PreflightChecker:
    """
    Runs all preflight checks before the evaluation pipeline starts.

    Each check is independent — we run all of them so the user gets
    a complete picture (e.g., both APIs are broken, not just one).
    """

    def run(self) -> PreflightResult:
        """Run all preflight checks and return a combined result.

        Returns:
            PreflightResult with ok=True only if every check passed.
        """
        checks = {}

        # --- Check 1: Anthropic API key + model ---
        anthropic_ok, anthropic_msg = self._check_anthropic()
        checks["Anthropic API"] = {"passed": anthropic_ok, "message": anthropic_msg}

        # --- Check 2: AssemblyAI API key + balance ---
        assemblyai_ok, assemblyai_msg = self._check_assemblyai()
        checks["AssemblyAI API"] = {"passed": assemblyai_ok, "message": assemblyai_msg}

        all_passed = all(c["passed"] for c in checks.values())

        # Build a clear error message listing every failure
        failures = [
            f"{name}: {c['message']}"
            for name, c in checks.items()
            if not c["passed"]
        ]
        error_message = " | ".join(failures) if failures else ""

        return PreflightResult(
            ok=all_passed,
            checks=checks,
            error_message=error_message,
        )

    def _check_anthropic(self) -> tuple[bool, str]:
        """
        Verify the Anthropic API key is valid AND the configured model exists.

        Strategy: Call the /v1/models endpoint, which lists all available models.
        - If the key is invalid → 401 error
        - If the key is valid → we get a list of model IDs
        - We then check if our configured model is in that list

        This is better than making a test completion call because:
        - It's free (no tokens consumed)
        - It's fast (< 1 second)
        - It gives us the exact model list to validate against
        """
        try:
            client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

            # Fetch the list of all available models
            # client.models.list() returns a paginated list of ModelInfo objects
            models_page = client.models.list()
            available_ids = {m.id for m in models_page.data}

            # Check if our configured model is available
            # We get the model name from AnalysisService to keep it DRY
            from app.services.analysis import AnalysisService
            configured_model = AnalysisService().model

            if configured_model not in available_ids:
                # Show the user what models ARE available to help them fix it
                claude_models = sorted([m for m in available_ids if "claude" in m.lower()])
                return False, (
                    f"Model '{configured_model}' not found. "
                    f"Available Claude models: {', '.join(claude_models)}"
                )

            return True, f"API key valid, model '{configured_model}' confirmed available"

        except anthropic.AuthenticationError:
            return False, "Invalid API key — check ANTHROPIC_API_KEY in your .env file"
        except anthropic.APIConnectionError:
            return False, "Could not connect to Anthropic API — check your internet connection"
        except Exception as e:
            return False, f"Unexpected error: {type(e).__name__}: {str(e)}"

    def _check_assemblyai(self) -> tuple[bool, str]:
        """
        Verify the AssemblyAI API key is valid and account balance is not negative.

        Strategy: Call AssemblyAI's transcript list endpoint (GET /v2/transcript).
        - It's a lightweight read operation (no audio processing, no cost)
        - A 401 response means the API key is invalid
        - A 200 response means the key works AND balance is positive
          (negative balance accounts get blocked from ALL endpoints)
        - We specifically detect the "negative balance" error message

        Why not use the AssemblyAI SDK here? The SDK doesn't expose a
        direct "check balance" method, so we use httpx to call the REST
        API directly for this lightweight check.
        """
        try:
            response = httpx.get(
                "https://api.assemblyai.com/v2/transcript",
                headers={"authorization": settings.ASSEMBLYAI_API_KEY},
                params={"limit": 1},  # Fetch just 1 record — minimal data transfer
                timeout=10.0,
            )

            if response.status_code == 200:
                return True, "API key valid, account balance is positive"

            if response.status_code == 401:
                return False, "Invalid API key — check ASSEMBLYAI_API_KEY in your .env file"

            # Parse the error body for the specific negative balance message
            try:
                error_body = response.json()
                error_msg = error_body.get("error", "")
            except Exception:
                error_msg = response.text

            if "balance is negative" in error_msg.lower():
                return False, (
                    "Account balance is negative — "
                    "add credits at https://www.assemblyai.com/dashboard"
                )

            return False, f"API returned HTTP {response.status_code}: {error_msg}"

        except httpx.ConnectError:
            return False, "Could not connect to AssemblyAI — check your internet connection"
        except httpx.TimeoutException:
            return False, "AssemblyAI API timed out — check your internet connection"
        except Exception as e:
            return False, f"Unexpected error: {type(e).__name__}: {str(e)}"
