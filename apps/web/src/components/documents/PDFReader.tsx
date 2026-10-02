/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";

import { useEffect, useState, useCallback, useRef, useMemo } from "react";
import { Document, Page, pdfjs } from "react-pdf";
import "react-pdf/dist/esm/Page/AnnotationLayer.css";
import "react-pdf/dist/esm/Page/TextLayer.css";
import { Virtuoso, VirtuosoHandle } from "react-virtuoso";
import { 
  ChevronLeft, ChevronRight, ZoomIn, ZoomOut, Maximize, Minimize, 
  Search, List, X, Loader2, FileText
} from "lucide-react";
import { useDocuments } from "@/app/workspace/environments/documents/DocumentsContext";
import { SelectionActionMenu, type SelectionContext } from "./SelectionActionMenu";

// Initialize PDF.js worker locally using Next.js/Webpack 5 native URL support
pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.mjs',
  import.meta.url,
).toString();

interface PDFReaderProps {
  documentId: string;
}

interface OutlineNode {
  title: string;
  bold: boolean;
  italic: boolean;
  color: Uint8ClampedArray;
  dest: string | any[] | null;
  items: OutlineNode[];
}

export function PDFReader({ documentId }: PDFReaderProps) {
  const { state: docsState } = useDocuments();
  const documentInfo = docsState.documents.data?.find(d => d.id === documentId);
  const pages = documentInfo?.pages || [];

  const [pdfInstance, setPdfInstance] = useState<any>(null);
  const [numPages, setNumPages] = useState<number | null>(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [pageInput, setPageInput] = useState("1");
  const [scale, setScale] = useState(1.2);
  const [error, setError] = useState<Error | null>(null);
  const [selectionMenu, setSelectionMenu] = useState<SelectionContext | null>(null);
  
  // Outline
  const [outline, setOutline] = useState<OutlineNode[] | null>(null);
  const [isOutlineOpen, setIsOutlineOpen] = useState(false);
  
  // Search
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchInput, setSearchInput] = useState("");
  const [searchResults, setSearchResults] = useState<{ pageNumber: number, indexOnPage: number }[]>([]);
  const [activeSearchIndex, setActiveSearchIndex] = useState(-1);
  
  const containerRef = useRef<HTMLDivElement>(null);
  const virtuosoRef = useRef<VirtuosoHandle>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);

  // Document Switching Reset
  useEffect(() => {
    setNumPages(null);
    setPageNumber(1);
    setPageInput("1");
    setError(null);
    setSelectionMenu(null);
    setOutline(null);
    setIsOutlineOpen(false);
    setIsSearchOpen(false);
    setSearchQuery("");
    setSearchInput("");
    setSearchResults([]);
    setActiveSearchIndex(-1);
    setPdfInstance(null);
  }, [documentId]);

  const onDocumentLoadSuccess = async (pdf: any) => {
    setPdfInstance(pdf);
    setNumPages(pdf.numPages);
    setPageNumber(1);
    setPageInput("1");
    setError(null);
    try {
      const outlineData = await pdf.getOutline();
      setOutline(outlineData || null);
    } catch (e) {
      console.warn("Failed to load outline", e);
    }
  };

  const onDocumentLoadError = (err: Error) => {
    setError(err);
  };

  // Zoom
  const handleZoomIn = () => setScale((s) => Math.min(s + 0.2, 3.0));
  const handleZoomOut = () => setScale((s) => Math.max(s - 0.2, 0.5));
  const handleFitWidth = () => {
    if (containerRef.current) {
      // 600 is standard width, remove outline drawer width if open
      const availableWidth = containerRef.current.clientWidth - (isOutlineOpen ? 300 : 0) - 48;
      const newScale = availableWidth / 600;
      setScale(Math.max(0.5, Math.min(newScale, 3.0)));
    }
  };
  const handleFitPage = () => {
    if (containerRef.current) {
      const newScale = (containerRef.current.clientHeight - 48) / 800;
      setScale(Math.max(0.5, Math.min(newScale, 3.0)));
    }
  };

  // Navigation
  const handlePageChange = (visibleItemIndex: number) => {
    const newPage = visibleItemIndex + 1;
    setPageNumber(newPage);
    setPageInput(newPage.toString());
  };

  const jumpToPage = (target: number) => {
    if (!numPages || target < 1 || target > numPages) return;
    virtuosoRef.current?.scrollToIndex({ index: target - 1, align: 'start' });
  };

  const handlePageSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const target = parseInt(pageInput, 10);
    if (!isNaN(target)) {
      jumpToPage(target);
    } else {
      setPageInput(pageNumber.toString());
    }
  };

  // Outline Navigation
  const handleOutlineClick = async (dest: string | any[] | null) => {
    if (!pdfInstance || !dest) return;
    try {
      let destArray = dest;
      if (typeof dest === 'string') {
        destArray = await pdfInstance.getDestination(dest);
      }
      if (Array.isArray(destArray) && destArray.length > 0) {
        const pageIndex = await pdfInstance.getPageIndex(destArray[0]);
        if (pageIndex !== undefined) {
          jumpToPage(pageIndex + 1);
        }
      }
    } catch (e) {
      console.warn("Failed to navigate to outline destination", e);
    }
  };

  // Search
  useEffect(() => {
    if (!searchQuery || searchQuery.length < 2) {
      setSearchResults([]);
      setActiveSearchIndex(-1);
      return;
    }
    
    // Exact text search across structured pages
    const matches: { pageNumber: number, indexOnPage: number }[] = [];
    pages.forEach(p => {
      const pageText = p.blocks.map(b => b.text).join("\n");
      const regex = new RegExp(searchQuery.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi');
      let match;
      let indexOnPage = 0;
      while ((match = regex.exec(pageText)) !== null) {
        matches.push({ pageNumber: p.page_number, indexOnPage });
        indexOnPage++;
      }
    });
    
    setSearchResults(matches);
    if (matches.length > 0) {
      setActiveSearchIndex(0);
      jumpToPage(matches[0].pageNumber);
    } else {
      setActiveSearchIndex(-1);
    }
  }, [searchQuery, pages]);

  const handleNextMatch = () => {
    if (searchResults.length === 0) return;
    const nextIdx = (activeSearchIndex + 1) % searchResults.length;
    setActiveSearchIndex(nextIdx);
    jumpToPage(searchResults[nextIdx].pageNumber);
  };

  const handlePrevMatch = () => {
    if (searchResults.length === 0) return;
    const prevIdx = activeSearchIndex <= 0 ? searchResults.length - 1 : activeSearchIndex - 1;
    setActiveSearchIndex(prevIdx);
    jumpToPage(searchResults[prevIdx].pageNumber);
  };

  const customTextRenderer = useCallback((textItem: { str: string }) => {
    const escapeHtml = (unsafe: string) => {
      return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
    };

    if (!searchQuery || searchQuery.length < 2) {
      // Must return safe string since react-pdf might use innerHTML if we return markup elsewhere
      return escapeHtml(textItem.str);
    }
    
    const pattern = searchQuery.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(`(${pattern})`, 'gi');
    
    const splitText = textItem.str.split(regex);
    if (splitText.length <= 1) return escapeHtml(textItem.str);
    
    return splitText.map((part: string) => {
      const escaped = escapeHtml(part);
      return part.toLowerCase() === searchQuery.toLowerCase() 
        ? `<mark class="bg-yellow-300 text-black px-[1px] rounded-sm shadow-sm">${escaped}</mark>`
        : escaped;
    }).join('');
  }, [searchQuery]);

  // Keyboard Shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        if (isSearchOpen) setIsSearchOpen(false);
        if (isOutlineOpen) setIsOutlineOpen(false);
        if (selectionMenu) {
          window.getSelection()?.removeAllRanges();
          setSelectionMenu(null);
        }
      }
      if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
        e.preventDefault();
        setIsSearchOpen(true);
        setTimeout(() => searchInputRef.current?.focus(), 50);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isSearchOpen, isOutlineOpen, selectionMenu]);

  const handleSelectionPointerUp = useCallback(() => {
    setTimeout(() => {
      const selection = window.getSelection();
      if (!selection || selection.isCollapsed) return;
      
      let text = selection.toString().trim();
      if (text.length < 3) return;
      
      const getPageElement = (node: Node | null) => {
        let current = node;
        while (current && current !== window.document.body) {
          if (current instanceof HTMLElement && current.classList.contains('react-pdf__Page')) {
            return current;
          }
          current = current.parentNode;
        }
        return null;
      };

      const anchorPageElem = getPageElement(selection.anchorNode);
      const focusPageElem = getPageElement(selection.focusNode);
      const anchorPageStr = anchorPageElem?.getAttribute('data-page-number');
      const focusPageStr = focusPageElem?.getAttribute('data-page-number');
      
      if (!anchorPageStr || !focusPageStr) {
        setSelectionMenu(null);
        return;
      }
      if (anchorPageStr !== focusPageStr) {
        selection.removeAllRanges();
        setSelectionMenu(null);
        return;
      }

      const pageNum = parseInt(anchorPageStr, 10);
      if (text.length > 6000) {
        text = text.substring(0, 3000) + "\n\n...[TRUNCATED BY SYSTEM]...\n\n" + text.substring(text.length - 2900);
      }

      let surroundingContext = undefined;
      const structuredPage = pages.find(p => p.page_number === pageNum);
      if (structuredPage) {
        const firstWord = text.split(" ").find(w => w.length > 3) || text.split(" ")[0];
        if (firstWord) {
          const matchingBlockIdx = structuredPage.blocks.findIndex(b => b.text.includes(firstWord));
          if (matchingBlockIdx !== -1) {
            const startIdx = Math.max(0, matchingBlockIdx - 1);
            const endIdx = Math.min(structuredPage.blocks.length, matchingBlockIdx + 2);
            let contextText = structuredPage.blocks.slice(startIdx, endIdx).map(b => b.text).join("\n\n");
            
            if (contextText.length > 12000) {
              contextText = contextText.substring(0, 12000) + "\n...[CONTEXT TRUNCATED BY SYSTEM]";
            }
            surroundingContext = contextText;
          }
        }
      }

      if (selection.rangeCount > 0) {
        const range = selection.getRangeAt(0);
        const rect = range.getBoundingClientRect();
        const containerRect = containerRef.current?.getBoundingClientRect();
        if (containerRect) {
          setSelectionMenu({
            documentId,
            pageNumber: pageNum,
            selectedText: text,
            surroundingContext,
            x: rect.left - containerRect.left + (rect.width / 2),
            y: rect.top - containerRect.top - 10,
            timestamp: Date.now()
          });
        }
      }
    }, 50);
  }, [documentId, pages]);

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-8 text-center bg-gray-50/50 rounded-lg">
        <div className="w-16 h-16 bg-red-50 text-red-500 rounded-full flex items-center justify-center mb-4">
          <X className="w-8 h-8" />
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-1">Failed to load document</h3>
        <p className="text-gray-500 text-sm max-w-md">
          {error.message.includes("403") 
            ? "You don't have permission to view this document." 
            : error.message.includes("404")
            ? "The document file could not be found."
            : "There was a problem loading the PDF file."}
        </p>
      </div>
    );
  }

  const renderOutlineNode = (node: OutlineNode, idx: number, depth: number = 0) => {
    return (
      <div key={`${node.title}-${idx}`} className="w-full">
        <button 
          onClick={() => handleOutlineClick(node.dest)}
          className="w-full text-left py-1.5 px-3 hover:bg-gray-100 rounded text-sm transition-colors"
          style={{ paddingLeft: `${depth * 12 + 12}px` }}
        >
          <span className={`block truncate ${node.bold ? 'font-semibold' : ''} ${node.italic ? 'italic' : ''} text-gray-700`}>
            {node.title}
          </span>
        </button>
        {node.items && node.items.length > 0 && (
          <div className="border-l border-gray-200 ml-3">
            {node.items.map((child, childIdx) => renderOutlineNode(child, childIdx, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full bg-[#f3f4f6]" ref={containerRef}>
      {/* Toolbar */}
      <div className="flex-none flex flex-wrap items-center justify-between px-4 py-2.5 bg-white border-b border-gray-200 shadow-sm z-20 gap-2 relative">
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setIsOutlineOpen(!isOutlineOpen)}
            className={`p-2 rounded-md transition-colors ${isOutlineOpen ? 'bg-accent/10 text-accent' : 'text-gray-500 hover:text-gray-900 hover:bg-gray-100'}`}
            title="Table of Contents"
            aria-label="Table of Contents"
            aria-expanded={isOutlineOpen}
          >
            <List className="w-4 h-4" />
          </button>
          
          <div className="hidden sm:flex items-center">
            <span className="font-serif text-sm font-medium text-gray-800 truncate max-w-[200px] lg:max-w-[300px]" title={documentInfo?.title}>
              {documentInfo?.title || "Document"}
            </span>
          </div>
        </div>

        {/* Center: Pagination */}
        <div className="flex items-center space-x-1 sm:space-x-2 bg-gray-50 px-2 sm:px-3 py-1.5 rounded-md border border-gray-200">
          <button 
            onClick={() => jumpToPage(pageNumber - 1)} 
            disabled={pageNumber <= 1}
            className="p-1 text-gray-500 hover:text-gray-900 disabled:opacity-30 disabled:hover:text-gray-500"
            aria-label="Previous Page"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          
          <form onSubmit={handlePageSubmit} className="flex items-center space-x-2">
            <input 
              type="text" 
              value={pageInput}
              onChange={(e) => setPageInput(e.target.value)}
              onBlur={() => setPageInput(pageNumber.toString())}
              className="w-10 text-center bg-white border border-gray-300 rounded text-sm py-0.5 font-medium text-gray-900 focus:outline-none focus:ring-1 focus:ring-accent"
              aria-label="Page number"
            />
            <span className="text-sm text-gray-500 font-medium">of {numPages || "-"}</span>
          </form>

          <button 
            onClick={() => jumpToPage(pageNumber + 1)} 
            disabled={!numPages || pageNumber >= numPages}
            className="p-1 text-gray-500 hover:text-gray-900 disabled:opacity-30 disabled:hover:text-gray-500"
            aria-label="Next Page"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
        
        {/* Right Controls */}
        <div className="flex items-center space-x-1">
          <div className="hidden md:flex items-center space-x-1">
            <button onClick={handleZoomOut} className="p-2 text-gray-500 hover:text-gray-900 hover:bg-gray-100 rounded-md" aria-label="Zoom Out"><ZoomOut className="w-4 h-4" /></button>
            <span className="text-sm font-medium text-gray-700 w-12 text-center select-none">{Math.round(scale * 100)}%</span>
            <button onClick={handleZoomIn} className="p-2 text-gray-500 hover:text-gray-900 hover:bg-gray-100 rounded-md" aria-label="Zoom In"><ZoomIn className="w-4 h-4" /></button>
            <div className="w-px h-4 bg-gray-300 mx-1" />
            <button onClick={handleFitWidth} className="p-2 text-gray-500 hover:text-gray-900 hover:bg-gray-100 rounded-md" aria-label="Fit Width"><Maximize className="w-4 h-4" /></button>
            <button onClick={handleFitPage} className="p-2 text-gray-500 hover:text-gray-900 hover:bg-gray-100 rounded-md" aria-label="Fit Page"><Minimize className="w-4 h-4" /></button>
            <div className="w-px h-4 bg-gray-300 mx-1" />
          </div>

          <button 
            onClick={() => {
              setIsSearchOpen(!isSearchOpen);
              if (!isSearchOpen) setTimeout(() => searchInputRef.current?.focus(), 50);
            }}
            className={`p-2 rounded-md transition-colors ${isSearchOpen ? 'bg-accent/10 text-accent' : 'text-gray-500 hover:text-gray-900 hover:bg-gray-100'}`}
            aria-label="Search"
            aria-expanded={isSearchOpen}
          >
            <Search className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Search Bar Popover */}
      {isSearchOpen && (
        <div className="absolute top-[60px] right-4 bg-white border border-gray-200 shadow-xl rounded-lg p-2 z-30 flex items-center space-x-2 animate-in fade-in slide-in-from-top-2">
          <Search className="w-4 h-4 text-gray-400 ml-2" />
          <input
            ref={searchInputRef}
            type="text"
            placeholder="Find in document..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                if (searchInput !== searchQuery) {
                  setSearchQuery(searchInput);
                } else {
                  handleNextMatch();
                }
              }
            }}
            className="border-none focus:ring-0 text-sm w-48 bg-transparent py-1.5 px-2"
          />
          {searchQuery && searchQuery === searchInput && (
            <span className="text-xs text-gray-500 font-medium whitespace-nowrap min-w-[50px] text-center">
              {searchResults.length > 0 ? `${activeSearchIndex + 1} of ${searchResults.length}` : '0 of 0'}
            </span>
          )}
          <div className="flex border-l border-gray-200 pl-2 space-x-1">
            <button 
              onClick={handlePrevMatch}
              disabled={searchResults.length === 0}
              className="p-1.5 text-gray-500 hover:bg-gray-100 rounded disabled:opacity-30"
              aria-label="Previous Match"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button 
              onClick={handleNextMatch}
              disabled={searchResults.length === 0}
              className="p-1.5 text-gray-500 hover:bg-gray-100 rounded disabled:opacity-30"
              aria-label="Next Match"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
            <button 
              onClick={() => {
                setIsSearchOpen(false);
                setSearchQuery("");
                setSearchInput("");
                setSearchResults([]);
              }}
              className="p-1.5 text-gray-500 hover:bg-gray-100 hover:text-red-600 rounded ml-1"
              aria-label="Close Search"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Main Layout Area */}
      <div className="flex-1 flex overflow-hidden relative">
        
        {/* Outline Drawer */}
        {isOutlineOpen && (
          <div className="w-72 flex-none bg-white border-r border-gray-200 overflow-y-auto z-10 shadow-[4px_0_12px_rgba(0,0,0,0.02)]">
            <div className="p-4 border-b border-gray-100 bg-gray-50/50 sticky top-0 backdrop-blur flex justify-between items-center">
              <h3 className="font-semibold text-gray-700 text-sm uppercase tracking-wider">Contents</h3>
              <button onClick={() => setIsOutlineOpen(false)} className="md:hidden p-1 text-gray-400 hover:text-gray-600">
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="p-2">
              {outline === null ? (
                <div className="py-8 px-4 text-center text-gray-500 text-sm flex flex-col items-center">
                  <Loader2 className="w-5 h-5 animate-spin text-gray-300 mb-2" />
                  <span>Loading outline...</span>
                </div>
              ) : outline.length === 0 ? (
                <div className="py-12 px-4 text-center text-gray-500 flex flex-col items-center">
                  <FileText className="w-8 h-8 text-gray-300 mb-3" />
                  <p className="text-sm font-medium text-gray-600">No outline available</p>
                  <p className="text-xs text-gray-400 mt-1">This PDF does not contain a table of contents.</p>
                </div>
              ) : (
                outline.map((node, idx) => renderOutlineNode(node, idx))
              )}
            </div>
          </div>
        )}

        {/* Document Viewport */}
        <div 
          data-testid="document-viewport"
          className="flex-1 relative overflow-hidden" 
          onPointerUp={handleSelectionPointerUp}
        >
          {selectionMenu && (
            <SelectionActionMenu 
              key={selectionMenu.timestamp}
              selection={selectionMenu} 
              onClose={() => setSelectionMenu(null)} 
            />
          )}
          <Document
            file={`/api/v1/documents/${documentId}/file`}
            options={{ withCredentials: true }}
            onLoadSuccess={onDocumentLoadSuccess}
            onLoadError={onDocumentLoadError}
            loading={
              <div className="absolute inset-0 flex items-center justify-center bg-[#f3f4f6]">
                <div className="flex flex-col items-center space-y-4">
                  <div className="w-8 h-8 border-4 border-accent border-t-transparent rounded-full animate-spin" />
                  <p className="text-gray-500 font-medium">Opening paper...</p>
                </div>
              </div>
            }
            className="h-full"
          >
            {numPages ? (
              <Virtuoso
                ref={virtuosoRef}
                style={{ height: '100%' }}
                totalCount={numPages}
                overscan={3} // Keep pages in DOM above/below for smooth scrolling
                rangeChanged={(range) => handlePageChange(range.startIndex)}
                itemContent={(index) => (
                  <div className="flex justify-center py-4 px-2 sm:px-8">
                    <div 
                      className="bg-white shadow-lg overflow-hidden transition-all duration-200 ring-1 ring-black/5"
                      style={{
                        boxShadow: '0 8px 16px -4px rgba(0, 0, 0, 0.05), 0 4px 8px -4px rgba(0, 0, 0, 0.05)',
                      }}
                    >
                      <Page
                        pageNumber={index + 1}
                        scale={scale}
                        loading={
                          <div 
                            className="flex items-center justify-center bg-gray-50"
                            style={{ width: 600 * scale, height: 800 * scale }}
                          >
                            <div className="w-6 h-6 border-2 border-gray-300 border-t-gray-600 rounded-full animate-spin" />
                          </div>
                        }
                        renderAnnotationLayer={true}
                        renderTextLayer={true}
                        customTextRenderer={customTextRenderer}
                      />
                    </div>
                  </div>
                )}
              />
            ) : null}
          </Document>
        </div>
      </div>
    </div>
  );
}
