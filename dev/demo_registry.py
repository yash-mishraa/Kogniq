import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "content" / "src"))

from content.plugins.registry import ProcessorRegistry
from content.processors.docx import DOCXProcessor
from content.processors.markdown import MarkdownProcessor
from content.processors.pdf import PDFProcessor
from content.processors.txt import TXTProcessor


def main() -> None:
    registry = ProcessorRegistry()
    
    # Automatic registration check: The registry requires no changes to support these
    registry.register(PDFProcessor())
    registry.register(MarkdownProcessor())
    registry.register(DOCXProcessor())
    registry.register(TXTProcessor())

    print("-" * 32)
    print("Registered processors")
    for name in registry.available_processors():
        print(name)
        
    print("\n" + "-" * 32)
    print("Supported extensions")
    for ext in registry.supported_extensions():
        print(f".{ext}")
        
    print("\n" + "-" * 32)
    print("Supported MIME types")
    for mime in registry.supported_mime_types():
        print(mime)
        
    print("\n" + "-" * 32)
    print(f"Total processors: {registry.processor_count()}")
    print("-" * 32)
    
    print("\nDetailed Introspection:")
    for name in registry.available_processors():
        info = registry.processor_info(name)
        print(f"\nProcessor Name      : {info.name}")
        print(f"Version             : {info.version}")
        print(f"Supported Extensions: {', '.join(info.supported_extensions)}")
        print(f"Supported MIME Types: {', '.join(info.supported_mime_types)}")
        print(f"Description         : {info.description}")

if __name__ == "__main__":
    main()
