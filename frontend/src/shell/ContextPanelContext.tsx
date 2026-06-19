import { createContext, useContext, useMemo, useState, type ReactNode } from "react";

export type RelatedOpportunity = {
  jobId: string;
  title: string;
  company: string;
  signalLabel: string;
};

export type RadarPreview = {
  jobId: string;
  title: string;
  company: string;
  source: string;
  location: string;
  signalLabel: string;
  stage: string;
  status: string;
  summary?: string;
  relatedOpportunities?: RelatedOpportunity[];
};

type ContextPanelContextValue = {
  preview: RadarPreview | null;
  setPreview: (preview: RadarPreview | null) => void;
};

const ContextPanelContext = createContext<ContextPanelContextValue | null>(null);

export function ContextPanelProvider({ children }: { children: ReactNode }) {
  const [preview, setPreview] = useState<RadarPreview | null>(null);
  const value = useMemo(() => ({ preview, setPreview }), [preview]);

  return <ContextPanelContext.Provider value={value}>{children}</ContextPanelContext.Provider>;
}

export function useContextPanel(): ContextPanelContextValue {
  const ctx = useContext(ContextPanelContext);
  if (!ctx) {
    throw new Error("useContextPanel must be used within a ContextPanelProvider");
  }
  return ctx;
}
