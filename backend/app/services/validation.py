"""
Deterministic Validation Service.

Validates demo case data BEFORE attempting any portal interaction.
All checks are rule-based — no LLM is involved.
"""

from __future__ import annotations

import json
import logging
from datetime import date

from app.models.demo_case import DemoCase

logger = logging.getLogger(__name__)


class ValidationCheck:
    def __init__(self, name: str, passed: bool, message: str):
        self.name = name
        self.passed = passed
        self.message = message

    def to_dict(self) -> dict:
        return {"name": self.name, "passed": self.passed, "message": self.message}


class ValidationService:
    """
    Validates a DemoCase record against required workflow preconditions.
    Returns a list of ValidationCheck results — all deterministic, no AI.
    """

    def validate_demo_case(self, case: DemoCase) -> tuple[bool, list[dict]]:
        """
        Run all validation checks on a demo case.
        Returns (all_passed: bool, checks: list[dict])
        """
        checks: list[ValidationCheck] = [
            self._check_synthetic_flag(case),
            self._check_patient_name(case),
            self._check_beneficiary_id(case),
            self._check_dob(case),
            self._check_hospital(case),
            self._check_procedure(case),
            self._check_amount(case),
            self._check_documents(case),
        ]

        all_passed = all(c.passed for c in checks)
        result = [c.to_dict() for c in checks]

        if not all_passed:
            failed = [c.name for c in checks if not c.passed]
            logger.warning("Validation failed for case %s: %s", case.case_ref, failed)

        return all_passed, result

    # -------------------------------------------------------------------------
    # Individual check methods
    # -------------------------------------------------------------------------

    def _check_synthetic_flag(self, case: DemoCase) -> ValidationCheck:
        passed = case.demo_is_synthetic is True
        return ValidationCheck(
            name="Synthetic data flag",
            passed=passed,
            message=(
                "OK — confirmed synthetic data"
                if passed
                else "BLOCKED — real data not permitted in demo"
            ),
        )

    def _check_patient_name(self, case: DemoCase) -> ValidationCheck:
        passed = bool(case.demo_patient_name and case.demo_patient_name.strip())
        return ValidationCheck(
            name="Beneficiary name",
            passed=passed,
            message="OK" if passed else "Beneficiary name is empty",
        )

    def _check_beneficiary_id(self, case: DemoCase) -> ValidationCheck:
        passed = bool(case.demo_beneficiary_id and len(case.demo_beneficiary_id.strip()) >= 5)
        return ValidationCheck(
            name="Beneficiary ID",
            passed=passed,
            message="OK" if passed else "Beneficiary ID is missing or too short",
        )

    def _check_dob(self, case: DemoCase) -> ValidationCheck:
        try:
            dob = case.demo_dob
            passed = isinstance(dob, date) and dob.year > 1900 and dob < date.today()
            msg = "OK" if passed else "Date of birth is invalid or in the future"
        except Exception:
            passed = False
            msg = "Date of birth could not be parsed"
        return ValidationCheck(name="Date of birth", passed=passed, message=msg)

    def _check_hospital(self, case: DemoCase) -> ValidationCheck:
        passed = bool(case.demo_hospital_name and case.demo_hospital_code)
        return ValidationCheck(
            name="Hospital information",
            passed=passed,
            message="OK" if passed else "Hospital name or code is missing",
        )

    def _check_procedure(self, case: DemoCase) -> ValidationCheck:
        passed = bool(case.demo_procedure_name and case.demo_procedure_code)
        return ValidationCheck(
            name="Procedure information",
            passed=passed,
            message="OK" if passed else "Procedure name or code is missing",
        )

    def _check_amount(self, case: DemoCase) -> ValidationCheck:
        try:
            amount = float(case.demo_amount)
            passed = amount > 0
            msg = "OK" if passed else "Amount must be greater than zero"
        except (TypeError, ValueError):
            passed = False
            msg = "Amount is not a valid number"
        return ValidationCheck(name="Claim amount", passed=passed, message=msg)

    def _check_documents(self, case: DemoCase) -> ValidationCheck:
        try:
            docs = json.loads(case.demo_documents or "[]")
            passed = isinstance(docs, list)
            msg = f"OK — {len(docs)} document(s) listed" if passed else "Document list is invalid"
        except (json.JSONDecodeError, TypeError):
            passed = False
            msg = "Document list could not be parsed"
        return ValidationCheck(name="Document availability", passed=passed, message=msg)
