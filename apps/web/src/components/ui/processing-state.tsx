import React from "react";
import { Loader2 } from "lucide-react";

interface ProcessingStateProps {
  status: string;
}

export function ProcessingState({ status }: ProcessingStateProps) {
  const getMessage = () => {
    switch (status) {
      case "Uploaded":
        return "Uploading your document...";
      case "Extracting":
      case "Normalizing":
      case "Chunking":
        return "Reading and processing your document...";
      case "Persisted":
        return "Building your document search index...";
      case "Failed":
        return "We couldn't finish processing this document.";
      default:
        return "Processing your document...";
    }
  };

  if (status === "Failed") {
    return (
      <div className="flex flex-col flex-1 items-center justify-center w-full h-full text-foreground/60 space-y-4">
        <div className="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center text-red-600">
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </div>
        <p className="text-lg">{getMessage()}</p>
        <p className="text-sm">Please try uploading it again or check the format.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col flex-1 items-center justify-center w-full h-full text-foreground/60 space-y-4">
      <Loader2 className="w-8 h-8 animate-spin text-accent" />
      <p className="text-lg animate-pulse">{getMessage()}</p>
      <p className="text-sm">This usually takes around 1-2 minutes depending on document length.</p>
    </div>
  );
}
