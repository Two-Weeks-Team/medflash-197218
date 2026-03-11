export const API_BASE = process.env.NEXT_PUBLIC_API_URL || '';

export async function fetchDecks() {
  const res = await fetch(`${API_BASE}/api/decks`);
  if (!res.ok) throw new Error('Failed to load decks');
  return res.json();
}

export async function fetchCards(deckId: number) {
  const res = await fetch(`${API_BASE}/api/decks/${deckId}/cards`);
  if (!res.ok) throw new Error('Failed to load cards');
  return res.json();
}

export async function startStudySession(deckId: number) {
  const res = await fetch(`${API_BASE}/api/study`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ deck_id: deckId })
  });
  if (!res.ok) throw new Error('Failed to start study session');
  return res.json();
}

export async function submitAnswer(sessionId: string, difficulty: string) {
  const res = await fetch(`${API_BASE}/api/study/${sessionId}/answer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ difficulty })
  });
  if (!res.ok) throw new Error('Failed to submit answer');
  return res.json();
}

export async function fetchProgress() {
  const res = await fetch(`${API_BASE}/api/progress`);
  if (!res.ok) return null;
  return res.json();
}
