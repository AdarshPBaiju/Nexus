import React from 'react';
import { BaseFormController } from './BaseFormController';

export interface NexusFormProps<TValues extends Record<string, unknown>> {
  readonly controller: BaseFormController<TValues>;
  readonly onSubmit?: (values: TValues) => void;
  readonly className?: string;
  readonly children: React.ReactNode;
}

export function NexusForm<TValues extends Record<string, unknown>>({
  controller,
  onSubmit,
  className = '',
  children,
}: NexusFormProps<TValues>): React.JSX.Element {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (onSubmit) {
      onSubmit(controller.formValues as TValues);
    } else {
      controller.submit();
    }
  };

  return (
    <form onSubmit={handleSubmit} className={className} noValidate>
      {children}
    </form>
  );
}
