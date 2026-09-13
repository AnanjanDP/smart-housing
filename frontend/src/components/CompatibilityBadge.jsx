import React from 'react';
import { Sparkles } from 'lucide-react';

export const CompatibilityBadge = ({ score = 92 }) => {
  return (
    <div className="badge badge-high">
      <Sparkles size={14} />
      <span>{score}% Compatibility Match</span>
    </div>
  );
};
