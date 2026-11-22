"""
nexus.extensions.base.hr_basic.service - Barrel re-exports for HR basic services.
"""

from nexus.extensions.base.hr_basic.attendance_service import (
    ClockInRequestDto,
    ClockOutRequestDto,
    HrAttendanceService,
    ManagerCorrectionDto,
)
from nexus.extensions.base.hr_basic.contract_service import (
    ContractRegistrationDto,
    HrContractService,
)

__all__ = [
    "ClockInRequestDto",
    "ClockOutRequestDto",
    "ContractRegistrationDto",
    "HrAttendanceService",
    "HrContractService",
    "ManagerCorrectionDto",
]
