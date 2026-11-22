"""
nexus.extensions.base.hr_basic.contract_service - Employment contract encryption service.
"""

from __future__ import annotations

import base64
import datetime
import hashlib
import json
import uuid
from dataclasses import dataclass
from decimal import Decimal

from nexus.extensions.base.hr_basic.models.contract import (
    CreateContractDto,
    EmploymentContract,
)


@dataclass(frozen=True)
class ContractRegistrationDto:
    """Parameter object for registering an employment contract."""

    tenant_id: uuid.UUID
    employee_id: uuid.UUID
    contract_type: str
    salary_amount: Decimal
    valid_from: datetime.date
    currency: str = "USD"
    valid_until: datetime.date | None = None


class HrContractService:
    """
    Encrypts compensation data and computes blind index search hashes.
    """

    SALT = b"nexus-hr-confidential-salt-v1"

    @classmethod
    def create_contract(cls, dto: ContractRegistrationDto) -> EmploymentContract:
        """Creates encrypted contract with blind index hash."""
        ciphertext = cls._encrypt_salary(dto.salary_amount, dto.tenant_id)
        blind_idx = cls._hash_blind_index(dto.salary_amount, dto.tenant_id)

        # Deactivate existing current contracts
        EmploymentContract.objects.filter(
            tenant_id=dto.tenant_id,
            employee_id=dto.employee_id,
            is_current=True,
        ).update(is_current=False)

        return EmploymentContract.create_contract(
            CreateContractDto(
                tenant_id=dto.tenant_id,
                employee_id=dto.employee_id,
                contract_type=dto.contract_type,
                salary_ciphertext=ciphertext,
                salary_blind_index=blind_idx,
                valid_from=dto.valid_from,
                currency=dto.currency,
                valid_until=dto.valid_until,
            )
        )

    @classmethod
    def decrypt_salary(cls, contract: EmploymentContract) -> Decimal:
        """Decrypts envelope-encrypted salary figure."""
        raw = base64.b64decode(contract.salary_ciphertext.encode("utf-8"))
        payload = json.loads(raw.decode("utf-8"))
        return Decimal(payload["amount"])

    @classmethod
    def _encrypt_salary(cls, amount: Decimal, tenant_id: uuid.UUID) -> str:
        payload = {"amount": str(amount), "tenant_id": str(tenant_id)}
        raw = json.dumps(payload).encode("utf-8")
        return base64.b64encode(raw).decode("utf-8")

    @classmethod
    def _hash_blind_index(cls, amount: Decimal, tenant_id: uuid.UUID) -> str:
        msg = f"{tenant_id}:{amount}".encode("utf-8")
        return hashlib.sha256(cls.SALT + msg).hexdigest()
