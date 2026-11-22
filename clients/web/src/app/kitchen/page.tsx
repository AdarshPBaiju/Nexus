'use client';

import React, { useState } from 'react';
import { Navbar } from '../components/Navbar';
import { KdsTouchCanvas } from '../../engines/kitchen/KdsTouchCanvas';
import type { KdsStationType, KdsTicketDto } from '../../engines/kitchen/kds.types';

const INITIAL_TICKETS: KdsTicketDto[] = [
  {
    id: 'TKT-101',
    orderToken: '#042',
    stationType: 'BARISTA',
    status: 'IN_PREP',
    slaSeconds: 300,
    elapsedSeconds: 180,
    diningType: 'DINE_IN',
    lines: [
      {
        id: 'LINE-1',
        itemName: 'Oat Flat White',
        quantity: 2,
        modifierNotes: ['Extra Hot', 'No Sugar'],
        allergenFlags: [],
        isCompleted: false,
      },
      {
        id: 'LINE-2',
        itemName: 'Iced Matcha Latte',
        quantity: 1,
        modifierNotes: ['Almond Milk'],
        allergenFlags: [],
        isCompleted: false,
      },
    ],
  },
  {
    id: 'TKT-102',
    orderToken: '#043',
    stationType: 'BARISTA',
    status: 'NEW',
    slaSeconds: 300,
    elapsedSeconds: 60,
    diningType: 'TAKEAWAY',
    lines: [
      {
        id: 'LINE-3',
        itemName: 'Single Origin Pour-over (Ethiopia)',
        quantity: 1,
        modifierNotes: ['V60 Medium Grind'],
        allergenFlags: [],
        isCompleted: false,
      },
    ],
  },
  {
    id: 'TKT-103',
    orderToken: '#044',
    stationType: 'HOT_KITCHEN',
    status: 'IN_PREP',
    slaSeconds: 360,
    elapsedSeconds: 240,
    diningType: 'DINE_IN',
    lines: [
      {
        id: 'LINE-4',
        itemName: 'Avocado Sourdough Toast',
        quantity: 1,
        modifierNotes: ['Poached Egg', 'Chili Flakes'],
        allergenFlags: ['EGGS', 'GLUTEN'],
        isCompleted: false,
      },
    ],
  },
];

export default function KitchenPage(): React.JSX.Element {
  const [tickets, setTickets] = useState<KdsTicketDto[]>(INITIAL_TICKETS);
  const [activeStation, setActiveStation] = useState<KdsStationType>('BARISTA');

  const handleBump = (ticketId: string) => {
    setTickets((prev) =>
      prev.map((t) => (t.id === ticketId ? { ...t, status: 'SERVED' } : t))
    );
  };

  const handleRecall = () => {
    setTickets(INITIAL_TICKETS);
  };

  return (
    <>
      <Navbar />
      <div style={{ flex: 1, height: 'calc(100vh - 60px)' }}>
        <KdsTouchCanvas
          tickets={tickets}
          activeStation={activeStation}
          onStationChange={setActiveStation}
          onBumpTicket={handleBump}
          onRecallTicket={handleRecall}
        />
      </div>
    </>
  );
}
