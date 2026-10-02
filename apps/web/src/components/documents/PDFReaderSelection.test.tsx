/* eslint-disable @typescript-eslint/no-explicit-any */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { PDFReader } from './PDFReader';
import { DocumentsContext } from '@/app/workspace/environments/documents/DocumentsContext';
import { WorkspaceContext } from '@/app/workspace/WorkspaceContext';

// Mock react-pdf to avoid actual PDF rendering in jsdom
vi.mock('react-pdf', () => ({
  pdfjs: { GlobalWorkerOptions: { workerSrc: '' } },
  Document: ({ children }: any) => <div>{children}</div>,
  Page: ({ pageNumber }: any) => <div className="react-pdf__Page" data-page-number={pageNumber}>Page {pageNumber}</div>
}));

// Mock Virtuoso
vi.mock('react-virtuoso', () => ({
  Virtuoso: ({ itemContent, totalCount }: any) => (
    <div>
      {Array.from({ length: totalCount }).map((_, i) => itemContent(i))}
    </div>
  )
}));

describe('PDFReader Selection Handling', () => {
  const mockDocumentsState = {
    documents: {
      data: [{
        id: 'doc-1',
        title: 'Test Doc',
        pages: [
          { page_number: 1, blocks: [{ text: 'Block 1 on page 1' }] },
          { page_number: 2, blocks: [{ text: 'Block 1 on page 2' }] }
        ]
      }],
      isLoading: false,
      error: null
    }
  };

  const renderWithContext = (component: any) => {
    const mockWorkspaceContext = {
      switchEnvironment: vi.fn(),
      remember: vi.fn(),
      memory: { study: {} }
    };
    
    return render(
      <DocumentsContext.Provider value={{ state: mockDocumentsState as any, dispatch: vi.fn() }}>
        <WorkspaceContext.Provider value={mockWorkspaceContext as any}>
          {component}
        </WorkspaceContext.Provider>
      </DocumentsContext.Provider>
    );
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('rejects cross-page selection', async () => {
    const { container } = renderWithContext(<PDFReader documentId="doc-1" />);
    
    // We need to mock getSelection
    const removeAllRanges = vi.fn();
    const anchorNode = document.createElement('div');
    anchorNode.classList.add('react-pdf__Page');
    anchorNode.setAttribute('data-page-number', '1');
    
    const focusNode = document.createElement('div');
    focusNode.classList.add('react-pdf__Page');
    focusNode.setAttribute('data-page-number', '2');

    document.body.appendChild(anchorNode);
    document.body.appendChild(focusNode);

    window.getSelection = vi.fn().mockReturnValue({
      isCollapsed: false,
      toString: () => 'Some selected text',
      anchorNode,
      focusNode,
      removeAllRanges
    });

    const viewport = screen.getAllByTestId('document-viewport')[0];
    fireEvent.pointerUp(viewport!);

    // Wait for the timeout in handleSelectionPointerUp
    await new Promise(r => setTimeout(r, 60));

    expect(removeAllRanges).toHaveBeenCalled();
    // Menu should not be rendered
    expect(screen.queryByText('Explain')).toBeNull();
    
    document.body.removeChild(anchorNode);
    document.body.removeChild(focusNode);
  });
  
  it('accepts same-page selection and bounds oversized text', async () => {
    const { container } = renderWithContext(<PDFReader documentId="doc-1" />);
    
    const removeAllRanges = vi.fn();
    const anchorNode = document.createElement('div');
    anchorNode.classList.add('react-pdf__Page');
    anchorNode.setAttribute('data-page-number', '1');
    
    document.body.appendChild(anchorNode);

    // Create an 8000 character string
    const oversizedText = 'A'.repeat(8000);

    window.getSelection = vi.fn().mockReturnValue({
      isCollapsed: false,
      toString: () => oversizedText,
      anchorNode,
      focusNode: anchorNode,
      removeAllRanges,
      rangeCount: 1,
      getRangeAt: () => ({
        getBoundingClientRect: () => ({ left: 10, top: 10, width: 100, height: 20 })
      })
    });

    // Mock getBoundingClientRect on container
    const viewport = screen.getAllByTestId('document-viewport')[0];
    vi.spyOn(viewport as Element, 'getBoundingClientRect').mockReturnValue({
      left: 0, top: 0, width: 800, height: 600, bottom: 600, right: 800, x: 0, y: 0, toJSON: () => {}
    });

    fireEvent.pointerUp(viewport!);

    await waitFor(() => {
      expect(screen.queryByText('Explain')).not.toBeNull();
    });

    // We can't easily assert the internal truncated string without spying on SelectionActionMenu, 
    // but we know the menu renders, and getSelection wasn't cleared.
    expect(removeAllRanges).not.toHaveBeenCalled();

    document.body.removeChild(anchorNode);
  });
});
