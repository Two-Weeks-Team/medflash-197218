"use client";

import { FC } from 'react';
import { AcademicCapIcon } from '@heroicons/react/24/outline';
import { twMerge } from 'tailwind-merge';

interface HeroProps {
  onStart: () => void;
}

const Hero: FC<HeroProps> = ({ onStart }) => {
  return (
    <section className={twMerge('flex flex-col items-center text-center py-12 bg-primary/10 rounded-xl')}>
      <AcademicCapIcon className="h-16 w-16 text-primary mb-4" />
      <h1 className="text-4xl font-bold text-foreground mb-2">MedFlash</h1>
      <p className="text-lg text-foreground/80 mb-6 max-w-2xl">
        Effortlessly master medical terminology with specialized spaced repetition and expert‑endorsed content.
      </p>
      <button
        onClick={onStart}
        className="px-6 py-3 bg-primary text-white rounded-md hover:bg-primary/90 transition"
      >
        Start Studying
      </button>
    </section>
  );
};

export default Hero;
