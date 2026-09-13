import React from 'react';
import { RoommateCard } from '../components/RoommateCard';

export const RoommatesPage = () => {
  return (
    <div style={{ padding: '32px' }}>
      <h1 style={{ fontSize: '2rem', fontWeight: 800, marginBottom: '24px' }}>Compatible Roommate Finder</h1>
      <div className="grid-layout">
        <RoommateCard roommate={{ name: 'Sarah Connor', preferred_location: 'San Francisco, CA', budget_min: 1600, budget_max: 2300, sleep_schedule: 'Early Bird', score: 98 }} />
        <RoommateCard roommate={{ name: 'David Miller', preferred_location: 'Palo Alto, CA', budget_min: 1400, budget_max: 2000, sleep_schedule: 'Flexible', score: 91 }} />
        <RoommateCard roommate={{ name: 'Elena Rostova', preferred_location: 'San Jose, CA', budget_min: 1500, budget_max: 2100, sleep_schedule: 'Night Owl', score: 87 }} />
      </div>
    </div>
  );
};
