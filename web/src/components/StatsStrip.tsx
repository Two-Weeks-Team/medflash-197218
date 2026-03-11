"use client";

interface StatsStripProps {
  progress: { total_cards: number; correct_answers: number; progress_percent: number } | null;
}

export default function StatsStrip({ progress }: StatsStripProps) {
  if (!progress) return null;
  return (
    <div className="flex gap-6 text-sm text-foreground/80 bg-muted p-3 rounded-md">
      <span>Total Cards: {progress.total_cards}</span>
      <span>Correct Answers: {progress.correct_answers}</span>
      <span>Progress: {progress.progress_percent}%</span>
    </div>
  );
}
