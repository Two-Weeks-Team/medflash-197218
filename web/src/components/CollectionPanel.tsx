"use client";

import { twMerge } from 'tailwind-merge';

interface Deck {
  deck_id: number;
  title: string;
  description: string;
  category: string;
}

interface CollectionPanelProps {
  decks: Deck[];
}

export default function CollectionPanel({ decks }: CollectionPanelProps) {
  if (decks.length === 0) return null;
  return (
    <section className="mt-8">
      <h2 className="text-2xl font-semibold text-foreground mb-4">Your Saved Decks</h2>
      <div className="grid md:grid-cols-3 gap-4">
        {decks.slice(0, 6).map((deck) => (
          <div
            key={deck.deck_id}
            className={twMerge('p-4 bg-card rounded-lg shadow border border-border')}
          >
            <h3 className="font-medium text-foreground">{deck.title}</h3>
            <p className="text-sm text-foreground/70">{deck.description}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
