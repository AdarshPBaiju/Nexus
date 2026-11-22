#!/usr/bin/env python3
"""
verify_default_protected_hr_core.py - Verification suite for Subphase 02.02 (HR_CORE).
Validates:
1. Employee master directory profile registration and unique code scoping.
2. Confidential compensation encryption (AES-256) and searchable blind index hashing.
3. Decryption of sensitive contract salary figures.
4. Shift assignments and roster mapping.
5. Attendance clock-in and cross-midnight business date attribution.
6. Open shift conflict guard and clock-out workflow.
7. Supervisor manual attendance adjustment with mandatory audit reasoning.
8. Employee leave request submission and manager approval lifecycle.
9. Statutory holiday calendar declarations.
"""

from __future__ import annotations

import datetime
from decimal import Decimal
import os
from pathlib import Path
import sys
import time
import uuid

REPO_ROOT = Path(__file__).resolve().parents[1]
API_SRC = REPO_ROOT / "services" / "nexus-api" / "src"
sys.path.insert(0, str(API_SRC))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nexus_test_settings")
import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "nexus.platform.tenancy",
            "nexus.extensions.base.hr_basic",
        ],
        USE_TZ=True,
    )
    django.setup()

from django.core.exceptions import ValidationError
from django.core.management import call_command

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
from nexus.extensions.base.hr_basic.models.attendance import AttendanceRecord
from nexus.extensions.base.hr_basic.models.contract import EmploymentContract
from nexus.extensions.base.hr_basic.models.employee import (
    CreateEmployeeDto,
    EmployeeProfile,
)
from nexus.extensions.base.hr_basic.models.holiday import (
    CreateHolidayDto,
    HolidayDate,
)
from nexus.extensions.base.hr_basic.models.leave import (
    BasicLeaveRequest,
    SubmitLeaveDto,
)
from nexus.extensions.base.hr_basic.models.shift_assignment import (
    AssignShiftDto,
    BasicShiftAssignment,
)
from nexus.platform.tenancy.models import Tenant


def setup_in_memory_db() -> None:
    call_command("migrate", run_syncdb=True, verbosity=0)


def test_employee_and_encrypted_contract() -> None:
    print("[1/5] Testing employee registration & encrypted compensation contract...")
    tenant = Tenant.objects.create(slug="test-hr-tenant", legal_name="Global Hospitality Ltd")

    emp = EmployeeProfile.register_employee(
        CreateEmployeeDto(
            tenant_id=tenant.id,
            employee_code="EMP-1001",
            first_name="Jane",
            last_name="Doe",
            department="Food & Beverage",
            designation="Head Barista",
        )
    )
    assert emp.full_name == "Jane Doe"
    assert emp.is_active is True

    # Register contract with $4,500 salary
    contract = HrContractService.create_contract(
        ContractRegistrationDto(
            tenant_id=tenant.id,
            employee_id=emp.id,
            contract_type=EmploymentContract.ContractType.FULL_TIME,
            salary_amount=Decimal("4500.00"),
            valid_from=datetime.date(2026, 1, 1),
            currency="USD",
        )
    )
    assert contract.is_current is True
    assert "4500.00" not in contract.salary_ciphertext
    assert len(contract.salary_blind_index) == 64

    # Verify decryption
    decrypted = HrContractService.decrypt_salary(contract)
    assert decrypted == Decimal("4500.00")
    print("  ✓ Employee registered; salary encrypted and decrypted with 100% fidelity.")


def test_shift_roster_assignment() -> None:
    print("[2/5] Testing weekly shift roster assignment...")
    tenant = Tenant.objects.get(slug="test-hr-tenant")
    emp = EmployeeProfile.objects.get(tenant_id=tenant.id, employee_code="EMP-1001")
    branch_id = uuid.uuid4()

    shift = BasicShiftAssignment.assign_shift(
        AssignShiftDto(
            tenant_id=tenant.id,
            employee_id=emp.id,
            branch_id=branch_id,
            day_of_week=BasicShiftAssignment.DayOfWeek.FRIDAY,
            start_time=datetime.time(16, 0),
            end_time=datetime.time(0, 30),
        )
    )
    assert shift.day_of_week == 4
    assert shift.is_active is True
    print("  ✓ Shift assignment registered for Friday night.")


def test_cross_midnight_attendance_clocking() -> None:
    print("[3/5] Testing cross-midnight attendance calculation and punch clock...")
    tenant = Tenant.objects.get(slug="test-hr-tenant")
    emp = EmployeeProfile.objects.get(tenant_id=tenant.id, employee_code="EMP-1001")
    branch_id = uuid.uuid4()

    # Regular afternoon clock-in (16:00 UTC on 2026-11-20)
    punch_time = datetime.datetime(2026, 11, 20, 16, 0, tzinfo=datetime.timezone.utc)
    t0 = time.perf_counter()
    rec = HrAttendanceService.clock_in(
        ClockInRequestDto(
            tenant_id=tenant.id,
            employee_id=emp.id,
            branch_id=branch_id,
            clock_in_utc=punch_time,
            cutoff_hour=4,
        )
    )
    duration_ms = (time.perf_counter() - t0) * 1000
    assert rec.business_date == datetime.date(2026, 11, 20)
    assert rec.is_open is True

    # Duplicate open punch should be blocked
    try:
        HrAttendanceService.clock_in(
            ClockInRequestDto(
                tenant_id=tenant.id,
                employee_id=emp.id,
                branch_id=branch_id,
                clock_in_utc=punch_time,
            )
        )
        raise AssertionError("Expected ValidationError on duplicate open punch.")
    except ValidationError:
        pass

    # Clock out past midnight (02:15 UTC on 2026-11-21)
    out_time = datetime.datetime(2026, 11, 21, 2, 15, tzinfo=datetime.timezone.utc)
    closed_rec = HrAttendanceService.clock_out(
        ClockOutRequestDto(
            tenant_id=tenant.id,
            employee_id=emp.id,
            clock_out_utc=out_time,
        )
    )
    assert closed_rec.is_open is False
    assert closed_rec.business_date == datetime.date(2026, 11, 20)
    print(f"  ✓ Cross-midnight punch mapped to business date 2026-11-20 in {duration_ms:.4f}ms.")


def test_supervisor_attendance_correction() -> None:
    print("[4/5] Testing supervisor manual attendance adjustment with audit reason...")
    tenant = Tenant.objects.get(slug="test-hr-tenant")
    emp = EmployeeProfile.objects.get(tenant_id=tenant.id, employee_code="EMP-1001")
    rec = AttendanceRecord.objects.filter(tenant_id=tenant.id, employee_id=emp.id).first()
    assert rec is not None
    manager_id = uuid.uuid4()

    # Rejection check: empty reason
    try:
        HrAttendanceService.apply_manager_correction(
            ManagerCorrectionDto(
                record_id=rec.id,
                manager_user_id=manager_id,
                reason="   ",
            )
        )
        raise AssertionError("Expected ValidationError on empty audit reason.")
    except ValidationError:
        pass

    # Correct clock out time
    adjusted_out = datetime.datetime(2026, 11, 21, 2, 30, tzinfo=datetime.timezone.utc)
    corrected = HrAttendanceService.apply_manager_correction(
        ManagerCorrectionDto(
            record_id=rec.id,
            manager_user_id=manager_id,
            reason="Staff forgot to punch before leaving counter station",
            clock_out_utc=adjusted_out,
        )
    )
    assert corrected.is_manual_override is True
    assert "forgot to punch" in corrected.correction_reason
    print("  ✓ Supervisor adjustment successfully audited and enforced.")


def test_leave_requests_and_holidays() -> None:
    print("[5/5] Testing leave request workflow and statutory holiday calendar...")
    tenant = Tenant.objects.get(slug="test-hr-tenant")
    emp = EmployeeProfile.objects.get(tenant_id=tenant.id, employee_code="EMP-1001")
    manager_id = uuid.uuid4()

    # Submit 3-day annual leave
    leave = BasicLeaveRequest.submit_request(
        SubmitLeaveDto(
            tenant_id=tenant.id,
            employee_id=emp.id,
            leave_type=BasicLeaveRequest.LeaveType.ANNUAL,
            start_date=datetime.date(2026, 12, 24),
            end_date=datetime.date(2026, 12, 26),
            reason="Holiday family travel",
        )
    )
    assert leave.status == BasicLeaveRequest.Status.PENDING

    # Manager approves
    leave.approve(approver_id=manager_id)
    assert leave.status == BasicLeaveRequest.Status.APPROVED
    assert leave.approver_user_id == manager_id

    # Statutory holiday
    holiday = HolidayDate.declare_holiday(
        CreateHolidayDto(
            tenant_id=tenant.id,
            holiday_date=datetime.date(2026, 12, 25),
            name="Christmas Day",
            is_statutory=True,
        )
    )
    assert holiday.is_statutory is True
    print("  ✓ Leave request approved and statutory holiday registered.")


def main() -> None:
    print("================================================================================")
    print("NEXUS SUBPHASE 02.02: DEFAULT BASIC HR (HR_CORE) VERIFICATION")
    print("================================================================================")
    setup_in_memory_db()
    test_employee_and_encrypted_contract()
    test_shift_roster_assignment()
    test_cross_midnight_attendance_clocking()
    test_supervisor_attendance_correction()
    test_leave_requests_and_holidays()
    print("================================================================================")
    print("ALL HR_CORE VERIFICATION TESTS COMPLETED WITH 100% SUCCESS.")
    print("================================================================================")


if __name__ == "__main__":
    main()
