export interface StaffProfile {
  readonly id: string;
  readonly name: string;
  readonly role: 'SUPERVISOR' | 'BARISTA' | 'CASHIER' | 'ADMIN';
  readonly pinHash: string;
  readonly avatarIcon: string;
  readonly title: string;
  readonly workstationId: string;
  readonly tenantSlug: string;
  readonly tenantName: string;
  readonly branchId: string;
  readonly branchName: string;
  readonly capabilities: readonly string[];
}

export interface TenantWorkspace {
  readonly id: string;
  readonly slug: string;
  readonly name: string;
  readonly branchId: string;
  readonly branchName: string;
  readonly region: string;
  readonly subdomain: string;
  readonly tier: string;
}

export const PRECONFIGURED_TENANTS: readonly TenantWorkspace[] = [
  {
    id: 'TEN-01',
    slug: 'artisan-coffee',
    name: 'Artisan Coffee Roasters',
    branchId: 'BR-LND-01',
    branchName: 'London SoHo Roastery',
    region: 'ap-south-1',
    subdomain: 'artisan-coffee.nexus-qsr.io',
    tier: 'ENTERPRISE',
  },
  {
    id: 'TEN-02',
    slug: 'nexus-flagship-cafe',
    name: 'Nexus Flagship Roastery & Café',
    branchId: 'BR-BLR-01',
    branchName: 'Indiranagar Flagship',
    region: 'ap-south-1',
    subdomain: 'nexus-flagship-cafe.nexus-qsr.io',
    tier: 'ENTERPRISE',
  },
  {
    id: 'TEN-03',
    slug: 'blue-mountain-espresso',
    name: 'Blue Mountain Espresso Bar',
    branchId: 'BR-TKO-01',
    branchName: 'Tokyo Shibuya Bar',
    region: 'ap-northeast-1',
    subdomain: 'blue-mountain.nexus-qsr.io',
    tier: 'PRO',
  },
];

export const PRECONFIGURED_STAFF: readonly StaffProfile[] = [
  {
    id: 'STF-01',
    name: 'Sarah Jenkins',
    role: 'SUPERVISOR',
    pinHash: '888df25ae35772424a560c7152a1de794440e0ea5cfee62828333a456a506e05',
    avatarIcon: '☕',
    title: 'Head Barista & Supervisor',
    workstationId: 'WS-LND-01',
    tenantSlug: 'artisan-coffee',
    tenantName: 'Artisan Coffee Roasters',
    branchId: 'BR-LND-01',
    branchName: 'London SoHo Roastery',
    capabilities: ['CAFE_QSR', 'POS_COUNTER', 'KDS_BARISTA', 'FIN_CORE', 'HR_CORE'],
  },
  {
    id: 'STF-02',
    name: 'Marcus Vance',
    role: 'BARISTA',
    pinHash: '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4',
    avatarIcon: '🍳',
    title: 'Sous Chef & Kitchen Lead',
    workstationId: 'WS-KDS-02',
    tenantSlug: 'artisan-coffee',
    tenantName: 'Artisan Coffee Roasters',
    branchId: 'BR-LND-01',
    branchName: 'London SoHo Roastery',
    capabilities: ['CAFE_QSR', 'KDS_BARISTA'],
  },
  {
    id: 'STF-03',
    name: 'Chloe Bennett',
    role: 'CASHIER',
    pinHash: '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c',
    avatarIcon: '🥐',
    title: 'Front Counter Cashier',
    workstationId: 'WS-POS-03',
    tenantSlug: 'artisan-coffee',
    tenantName: 'Artisan Coffee Roasters',
    branchId: 'BR-LND-01',
    branchName: 'London SoHo Roastery',
    capabilities: ['CAFE_QSR', 'POS_COUNTER', 'FIN_CORE'],
  },
  {
    id: 'STF-04',
    name: 'David Chen',
    role: 'ADMIN',
    pinHash: '9af15b336e6a9619928537df30b2e6a2376569fcf9d7e773eccede65606529a0',
    avatarIcon: '👔',
    title: 'General Manager & Admin',
    workstationId: 'WS-MGR-01',
    tenantSlug: 'artisan-coffee',
    tenantName: 'Artisan Coffee Roasters',
    branchId: 'BR-LND-01',
    branchName: 'London SoHo Roastery',
    capabilities: ['CAFE_QSR', 'POS_COUNTER', 'KDS_BARISTA', 'FIN_CORE', 'HR_CORE'],
  },
];

export interface UserSession {
  readonly id: string;
  readonly name: string;
  readonly role: 'SUPERVISOR' | 'BARISTA' | 'CASHIER' | 'ADMIN';
  readonly workstationId: string;
  readonly tenantSlug: string;
  readonly tenantName: string;
  readonly branchId: string;
  readonly branchName: string;
  readonly capabilities: readonly string[];
}

export interface AuthContextValue {
  readonly session: UserSession;
  readonly isAuthenticated: boolean;
  readonly isHydrated: boolean;
  readonly activeStaff: StaffProfile;
  readonly availableTenants: readonly TenantWorkspace[];
  readonly activeTenant: TenantWorkspace;
  readonly hasCapability: (cap: string) => boolean;
  readonly loginWithPin: (pin: string) => Promise<boolean>;
  readonly selectStaff: (staffId: string) => void;
  readonly lockWorkstation: () => void;
  readonly switchRole: (role: UserSession['role']) => void;
  readonly switchTenant: (slug: string) => void;
  readonly registerTenantWorkspace: (workspace: TenantWorkspace) => void;
}
