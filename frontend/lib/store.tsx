"use client";

import { createContext, useContext, useState, ReactNode } from "react";
import type { UserInput, PredictionResponse, ExplanationResponse } from "@/lib/api";

interface AppState {
  userInput: UserInput | null;
  result: PredictionResponse | null;
  explanations: Record<number, ExplanationResponse | null>;
  explanationErrors: Record<number, boolean>;
  explanationsLoading: boolean;
  setUserInput: (input: UserInput | null) => void;
  setResult: (result: PredictionResponse | null) => void;
  setExplanations: (exp: Record<number, ExplanationResponse | null>) => void;
  setExplanationErrors: (errs: Record<number, boolean>) => void;
  setExplanationsLoading: (loading: boolean) => void;
  reset: () => void;
}

const AppContext = createContext<AppState | null>(null);

export function AppProvider({ children }: { children: ReactNode }) {
  const [userInput, setUserInput] = useState<UserInput | null>(null);
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [explanations, setExplanations] = useState<Record<number, ExplanationResponse | null>>({});
  const [explanationErrors, setExplanationErrors] = useState<Record<number, boolean>>({});
  const [explanationsLoading, setExplanationsLoading] = useState(false);

  function reset() {
    setUserInput(null);
    setResult(null);
    setExplanations({});
    setExplanationErrors({});
    setExplanationsLoading(false);
  }

  return (
    <AppContext.Provider
      value={{
        userInput,
        result,
        explanations,
        explanationErrors,
        explanationsLoading,
        setUserInput,
        setResult,
        setExplanations,
        setExplanationErrors,
        setExplanationsLoading,
        reset,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useAppStore() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useAppStore must be used within AppProvider");
  return ctx;
}
