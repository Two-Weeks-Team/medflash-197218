"use client";

import { useState } from "react";
import { twMerge } from 'tailwind-merge';
import { ArrowPathIcon } from '@heroicons/react/24/outline';

interface Card {
  term: string;
  definition: string;
}

interface FlashCardProps {
  card: Card;
  onAnswer: (difficulty: string) => void;
}

export default function FlashCard({ card, onAnswer }: FlashCardProps) {
  const [flipped, setFlipped] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const handleDifficulty = async (level: string) => {
    setSubmitting(true);
    await onAnswer(level);
    setFlipped(false);
    setSubmitting(false);
  };

  return (
    <div className="flex flex-col items-center">
      <div
        className={twMerge(
          'w-80 h-48 perspective',
          'group'
        )}
        onClick={() => setFlipped(!flipped)}
      >
        <div
          className={twMerge(
            'relative h-full w-full text-center rounded-lg shadow-lg transition-transform duration-500',
            'transform-style-preserve-3d',
            flipped ? 'rotate-y-180' : ''
          )}
        >
          {/* Front */}
          <div className="absolute inset-0 backface-hidden flex items-center justify-center bg-primary text-white p-4 rounded-lg">
            <span className="text-xl font-medium">{card.term}</span>
          </div>
          {/* Back */}
          <div className="absolute inset-0 backface-hidden flex items-center justify-center bg-card text-foreground p-4 rounded-lg rotate-y-180">
            <p className="text-base">{card.definition}</p>
          </div>
        </div>
      </div>
      {flipped && (
        <div className="mt-4 flex gap-2">
          {['easy', 'medium', 'hard'].map((lvl) => (
            <button
              key={lvl}
              disabled={submitting}
              onClick={() => handleDifficulty(lvl)}
              className={twMerge(
                'px-3 py-1 rounded-md text-sm font-medium',
                lvl === 'easy' && 'bg-success text-white',
                lvl === 'medium' && 'bg-accent text-white',
                lvl === 'hard' && 'bg-warning text-white'
              )}
            >
              {lvl.charAt(0).toUpperCase() + lvl.slice(1)}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
