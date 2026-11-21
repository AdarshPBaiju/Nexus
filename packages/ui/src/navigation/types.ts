export type NavigationMode =
  | 'NESTED_SIDEBAR'
  | 'DUAL_SIDEBAR'
  | 'TOP_CHILD_STRIP'
  | 'TOP_CHILD_SIDEBAR'
  | 'OPERATIONAL_MINIMAL';

export interface NavItem {
  readonly id: string;
  readonly label: string;
  readonly href: string;
  readonly icon?: string;
  readonly children?: readonly NavItem[];
}
