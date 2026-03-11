"use client";

import { useMemo, useState } from "react";
import { twMerge } from 'tailwind-merge';
import { clsx } from 'clsx';

interface Deck {
  deck_id: number;
  title: string;
  description: string;
  category: string;
}

interface DeckBrowserProps {
  decks: Deck[];
  loading: boolean;
  error: string | null;
  onSelect: (deck: Deck) => void;
}

export default function DeckBrowser({ decks, loading, error, onSelect }: DeckBrowserProps) {
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    const term = search.toLowerCase();
    return decks.filter((d) => d.title.toLowerCase().includes(term) || d.category.toLowerCase().includes(term));
  }, [search, decks]);

  if (loading) return <p className="text-muted">Loading decks…</p>;
  if (error) return <p className="text-red-600">Error: {error}</p>;
  if (decks.length === 0) return <p className="text-muted">No decks available.</p>;

  return (
    <div className="flex flex-col gap-4">
      <input
        type="text"
        placeholder="Search decks…"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="px-3 py-2 border border-border rounded-md focus:outline-none focus:border-primary"
      />
      {filtered.length === 0 ? (
        <p className="text-muted">No decks match your search.</p>
      ) : (
        <ul className="grid gap-4">
          {filtered.map((deck) => (
            <li
              key={deck.deck_id}
              className={twMerge(
                'p-4 bg-card rounded-lg shadow hover:shadow-md cursor-pointer transition',
                'border border-border'
              )}
              onClick={() => onSelect(deck)}
            >
              <h3 className="font-semibold text-foreground">{deck.title}</h3>
              <p className="text-sm text-foreground/70">{deck.description}</p>
              <span className="text-xs text-accent uppercase mt-1 block">{deck.category}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
