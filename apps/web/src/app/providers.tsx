"use client";

import { QueryCache, QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState, type ReactNode } from "react";

export function Providers({ children }: { children: ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 30_000,
            retry: (failureCount, error) => {
              if (
                error &&
                typeof error === "object" &&
                "status" in error &&
                (error as { status: number }).status === 401
              ) {
                return false;
              }
              return failureCount < 1;
            },
          },
        },
        queryCache: new QueryCache({
          onError: (error) => {
            if (
              error &&
              typeof error === "object" &&
              "status" in error &&
              (error as { status: number }).status === 401
            ) {
              queryClient.setQueryData(["session"], null);
            }
          },
        }),
      })
  );
  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}
