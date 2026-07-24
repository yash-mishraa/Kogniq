import { useRef } from "react";
import { useDocuments } from "@/app/workspace/environments/documents/DocumentsContext";
import { serviceProvider } from "@/lib/providers";

export function useDocumentUpload() {
  const { dispatch } = useDocuments();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const triggerUpload = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Optimistically show it as uploaded/extracting
      const tempId = `doc-${Date.now()}`;
      dispatch({
        type: "IMPORT_DOCUMENT",
        payload: {
          id: tempId,
          title: file.name.replace(/\.[^/.]+$/, ""),
          source: file.name,
          importDate: new Date().toISOString(),
          status: "Uploaded",
        },
      });

      // Synchronously call the backend API
      const formData = new FormData();
      formData.append("file", file);

      try {
        const data = await serviceProvider.getProvider().documents.processDocument({ file });

        dispatch({
          type: "UPDATE_STATUS",
          payload: {
            id: tempId, // Keep UI ID for now
            status: data.status,
          },
        });
      } catch (error) {
        console.error("Upload failed", error);
        dispatch({
          type: "UPDATE_STATUS",
          payload: { id: tempId, status: "Failed" },
        });
      }
    }
  };

  return { fileInputRef, triggerUpload, handleFileChange };
}
