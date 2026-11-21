export interface NexusControlProps<T> {
  readonly value: T;
  readonly onChange: (next: T) => void;
  readonly labelKey?: string;
  readonly placeholderKey?: string;
  readonly descriptionKey?: string;
  readonly errorKey?: string;
  readonly isDisabled?: boolean;
  readonly isReadOnly?: boolean;
  readonly isRequired?: boolean;
  readonly size?: 'sm' | 'md' | 'lg';
  readonly testId?: string;
}
