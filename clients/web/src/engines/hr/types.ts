/**
 * types.ts - Core domain models and DTOs for HR, Staff Directory & ESS Portal.
 */

export type ContractType = 'FULL_TIME' | 'PART_TIME' | 'CASUAL' | 'SEASONAL';
export type ClockInMethod = 'WEB' | 'PIN' | 'QR' | 'BIOMETRIC';
export type LeaveType = 'ANNUAL' | 'SICK' | 'UNPAID';
export type LeaveStatus = 'PENDING' | 'APPROVED' | 'REJECTED';

export interface EmployeeDto {
  readonly id: string;
  readonly employeeCode: string;
  readonly firstName: string;
  readonly lastName: string;
  readonly department: string;
  readonly designation: string;
  readonly reportingManagerId?: string | null;
  readonly isActive: boolean;
}

export interface ContractDto {
  readonly id: string;
  readonly employeeId: string;
  readonly contractType: ContractType;
  readonly maskedSalary: string;
  readonly currency: string;
  readonly validFrom: string;
  readonly validUntil?: string | null;
  readonly isCurrent: boolean;
}

export interface AttendanceRecordDto {
  readonly id: string;
  readonly employeeId: string;
  readonly branchId: string;
  readonly businessDate: string;
  readonly clockInUtc: string;
  readonly clockOutUtc?: string | null;
  readonly clockInMethod: ClockInMethod;
  readonly isManualOverride: boolean;
  readonly correctionReason?: string;
}

export interface LeaveRequestDto {
  readonly id: string;
  readonly employeeId: string;
  readonly leaveType: LeaveType;
  readonly startDate: string;
  readonly endDate: string;
  readonly status: LeaveStatus;
  readonly reason?: string;
}
