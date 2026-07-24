"use client";

import { Locus } from "@/components/locus";
import { useDocumentUpload } from "./useDocumentUpload";

export function DocumentEmptyState() {
  const { fileInputRef, triggerUpload, handleFileChange } = useDocumentUpload();

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
        onSelect={triggerUpload}
      />
    </section>
  );
}
