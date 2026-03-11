"use client";

import { useEffect, useState } from "react";
import Hero from '@/components/Hero';
import DeckBrowser from '@/components/DeckBrowser';
import FlashCard from '@/components/FlashCard';
import InsightPanel from '@/components/InsightPanel';
import StatsStrip from '@/components/StatsStrip';
import CollectionPanel from '@/components/CollectionPanel';
import StatePanel from '@/components/StatePanel';
import { fetchDecks, fetchProgress, startStudySession, submitAnswer } from '@/lib/api';

interface Deck {
  deck_id: number;
  title: string;
  description: string;
  category: string;
}

export default function HomePage() {
  const [decks, setDecks] = useState<Deck[]>([]);
  const [loadingDecks, setLoadingDecks] = useState(true);
  const [deckError, setDeckError] = useState<string | null>(null);

  const [selectedDeck, setSelectedDeck] = useState<Deck | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [currentCard, setCurrentCard] = useState<{ term: string; definition: string } | null>(null);
  const [studyLoading, setStudyLoading] = useState(false);
  const [studyError, setStudyError] = useState<string | null>(null);

  const [progress, setProgress] = useState<{ total_cards: number; correct_answers: number; progress_percent: number } | null>(null);

  // Load decks on mount
  useEffect(() => {
    fetchDecks()
      .then((data) => {
        setDecks(data);
        setLoadingDecks(false);
      })
      .catch((e) => {
        setDeckError(e.message);
        setLoadingDecks(false);
      });
    fetchProgress()
      .then(setProgress)
      .catch(() => {});
  }, []);

  const handleStartStudy = async (deck: Deck) => {
    setStudyLoading(true);
    setStudyError(null);
    try {
      const { session_id, card } = await startStudySession(deck.deck_id);
      setSelectedDeck(deck);
      setSessionId(session_id);
      setCurrentCard(card);
    } catch (e: any) {
      setStudyError(e.message);
    } finally {
      setStudyLoading(false);
    }
  };

  const handleAnswer = async (difficulty: string) => {
    if (!sessionId) return;
    setStudyLoading(true);
    try {
      const { next_card } = await submitAnswer(sessionId, difficulty);
      setCurrentCard(next_card);
      // refresh progress
      const newProg = await fetchProgress();
      setProgress(newProg);
    } catch (e: any) {
      setStudyError(e.message);
    } finally {
      setStudyLoading(false);
    }
  };

  return (
    <main className="flex-1 flex flex-col gap-8 p-6 max-w-5xl mx-auto">
      <Hero onStart={() => decks[0] && handleStartStudy(decks[0])} />
      <StatsStrip progress={progress} />
      <section className="grid md:grid-cols-2 gap-6">
        <div className="flex flex-col gap-4">
          <h2 className="text-2xl font-semibold text-foreground">Explore Decks</h2>
          <DeckBrowser
            decks={decks}
            loading={loadingDecks}
            error={deckError}
            onSelect={handleStartStudy}
          />
        </div>
        <div className="flex flex-col gap-4">
          <h2 className="text-2xl font-semibold text-foreground">Study Session</h2>
          {studyLoading && <StatePanel state="loading" />}
          {studyError && <StatePanel state="error" message={studyError} />}
          {currentCard && sessionId && (
            <>
              <FlashCard card={currentCard} onAnswer={handleAnswer} />
              <InsightPanel card={currentCard} />
            </>
          )}
          {!currentCard && !studyLoading && <StatePanel state="empty" message="Select a deck to begin studying." />}
        </div>
      </section>
      <CollectionPanel decks={decks} />
    </main>
  );
}
