"use client";

interface InsightPanelProps {
  card: { term: string; definition: string };
}

export default function InsightPanel({ card }: InsightPanelProps) {
  // Placeholder for AI‑generated insight – in a real app we'd call /api/ai/... here.
  return (
    <section className="mt-4 p-4 bg-muted rounded-lg shadow">
      <h3 className="font-semibold text-foreground mb-2">Did you know?</h3>
      <p className="text-foreground/80">
        The term <span className="font-medium">{card.term}</span> is commonly found in {card.definition.length > 60 ? 'clinical practice.' : 'basic textbooks.'}
      </p>
    </section>
  );
}
