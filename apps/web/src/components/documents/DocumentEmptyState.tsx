"use client";

import { useRef } from "react";
import { Locus } from "@/components/locus";
import { useDocuments } from "@/app/workspace/environments/documents/DocumentsContext";

export function DocumentEmptyState() {
  const { dispatch } = useDocuments();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSelect = () => {
    // Trigger the native file picker
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Mock import action
      dispatch({
        type: "IMPORT_DOCUMENT",
        payload: {
          id: `doc-${Date.now()}`,
          title: file.name.replace(/\.[^/.]+$/, ""),
          source: file.name,
          importDate: new Date().toISOString(),
          status: "imported",
        },
      });
    }
  };

  return (
    <section aria-label="Documents starting point" className="mx-auto flex w-full max-w-6xl flex-1 items-start pt-4">
      <input 
        type="file" 
        className="hidden" 
        ref={fileInputRef} 
        onChange={handleFileChange}
        accept=".pdf,.md,.txt,.doc,.docx" 
      />
      <Locus 
        environmentTitle="Documents" 
        placeholder="│ Import knowledge..." 
        suggestions={[
          { label: "Import knowledge", detail: "open file picker" }
        ]} 
        autoFocus 
        onSelect={handleSelect} 
      />
    </section>
  );
}
