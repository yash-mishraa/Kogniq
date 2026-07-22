"use client";

import { motion } from "framer-motion";
import { type ReactNode } from "react";

export interface ReadingSurfaceProps {
  title: string;
  layoutId?: string;
  content?: ReactNode;
}

export function ReadingSurface({ title, layoutId, content }: ReadingSurfaceProps) {
  return (
    <motion.article
      layout
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
      className="flex-1 flex flex-col bg-white overflow-y-auto px-16 lg:px-32 py-24"
      style={{
        boxShadow: "-12px 0 32px rgba(0, 0, 0, 0.02)",
      }}
    >
      <div className="max-w-[680px] mx-auto w-full">
        <motion.h1 
          layoutId={layoutId}
          className="text-4xl font-serif text-ink mb-12 tracking-tight leading-[1.15]"
        >
          {title}
        </motion.h1>
        
        <div className="prose prose-lg prose-ink max-w-none">
          {content ? (
            <div className="text-ink/80 leading-relaxed space-y-8">
              {content}
            </div>
          ) : (
            <div className="space-y-12 animate-pulse-slow">
              {/* Mock Editorial Abstract */}
              <div className="space-y-4">
                <div className="h-4 bg-black/5 rounded w-full" />
                <div className="h-4 bg-black/5 rounded w-11/12" />
                <div className="h-4 bg-black/5 rounded w-4/5" />
              </div>
              
              {/* Mock Section 1 */}
              <div className="space-y-6">
                <div className="h-6 bg-black/10 rounded w-1/3 mb-8" />
                <div className="h-4 bg-black/5 rounded w-full" />
                <div className="h-4 bg-black/5 rounded w-full" />
                <div className="h-4 bg-black/5 rounded w-10/12" />
              </div>

              {/* Mock Section 2 */}
              <div className="space-y-6">
                <div className="h-6 bg-black/10 rounded w-1/4 mb-8" />
                <div className="h-4 bg-black/5 rounded w-11/12" />
                <div className="h-4 bg-black/5 rounded w-full" />
                <div className="h-4 bg-black/5 rounded w-3/4" />
              </div>
            </div>
          )}
        </div>
      </div>
    </motion.article>
  );
}
