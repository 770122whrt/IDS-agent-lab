"""
Natural Language to IDS XML Converter

This script converts natural language text back to IDS XML through the ids-algo pipeline.

Flow:
1. Read natural language text (from IDS description)
2. Call ids-algo pipeline to process
3. Convert JSON output to IDS XML
4. Save and validate the result

Usage:
    python -m ids_converter.text_to_ids --input <input.txt> --output <output.ids> [--lang en|zh|both]

Environment:
    Requires OPENROUTER_API_KEY environment variable for the pipeline
"""

import asyncio
import json
import logging
import os
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Load environment variables from .env-pipeline before importing pipeline
_env_file = Path(__file__).parent.parent / "ids-algo" / ".env-pipeline"
if _env_file.exists():
    # Use python-dotenv to load the file
    try:
        from dotenv import load_dotenv
        load_dotenv(_env_file)
    except ImportError:
        # Fallback: manually load the file
        with open(_env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Remove quotes if present
                    value = value.strip('"').strip("'")
                    os.environ.setdefault(key.strip(), value)

# Converter imports (these don't require API key)
from .converter import convert_json_to_ids_xml, IDSToXMLConverter, XSDValidationError, IDSConversionError

# Parser import (for comparison)
from .ids_parser import IDSParser


# Lazy import for pipeline (requires API key)
_pipeline_module = None

def _get_pipeline():
    """Lazy load the pipeline module."""
    global _pipeline_module
    if _pipeline_module is None:
        # Add ids-algo to path
        ids_algo_path = Path(__file__).parent.parent / "ids-algo"
        if str(ids_algo_path) not in sys.path:
            sys.path.insert(0, str(ids_algo_path))
        from pipeline import run_ids_pipeline
        _pipeline_module = run_ids_pipeline
    return _pipeline_module


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("TextToIDS")


# =============================================================================
# Text Processing Utilities
# =============================================================================

def extract_english_text(text: str) -> str:
    """
    Extract the English portion from bilingual text.

    The text typically has a separator "=== English Version ==="
    """
    separator = "=== English Version ==="
    if separator in text:
        parts = text.split(separator)
        if len(parts) >= 2:
            return parts[1].strip()

    # No separator found, return original
    return text.strip()


def split_specifications(text: str) -> List[Tuple[str, str]]:
    """
    Split text into individual specifications for batch processing.

    Returns list of (spec_name, spec_text) tuples.

    Specification headers are in format:
    - 【Specification N】Name (English)
    - 【规范 N】名称 (Chinese)
    """
    specs = []
    lines = text.split('\n')

    current_name = None
    current_lines = []

    for line in lines:
        stripped = line.strip()

        # Detect specification header
        # English: 【Specification 1】Project
        # Chinese: 【规范 1】Project
        is_spec_header = False

        if stripped.startswith('【') and '】' in stripped:
            # Check if it's a specification header (not other bracketed content)
            bracket_content = stripped[1:stripped.index('】')]
            # Specification headers contain "Specification" or "规范" followed by a number
            if 'Specification' in bracket_content or '规范' in bracket_content:
                is_spec_header = True

        if is_spec_header:
            # Save previous spec if exists
            if current_name and current_lines:
                specs.append((current_name, '\n'.join(current_lines)))

            # Extract name from header
            # Format: 【Specification 1】Project -> name = "Project"
            try:
                close_bracket = stripped.index('】')
                current_name = stripped[close_bracket + 1:].strip()
            except (ValueError, IndexError):
                current_name = stripped

            current_lines = [line]
        elif current_name:
            current_lines.append(line)

    # Add last spec
    if current_name and current_lines:
        specs.append((current_name, '\n'.join(current_lines)))

    return specs


# =============================================================================
# Main Conversion Class
# =============================================================================

class TextToIDSConverter:
    """
    Convert natural language text to IDS XML.
    """

    def __init__(self, xsd_path: Optional[str] = None):
        """
        Initialize converter.

        Args:
            xsd_path: Path to IDS XSD schema file
        """
        self.xsd_path = xsd_path or Path(__file__).parent / "ids.xsd"
        self.xml_converter = IDSToXMLConverter(xsd_path=str(self.xsd_path))
        self.parser = IDSParser()

    async def convert_text(
        self,
        text: str,
        title: Optional[str] = None,
        language: str = "en",
        batch_mode: bool = False
    ) -> Tuple[Dict[str, Any], str]:
        """
        Convert natural language text to IDS XML.

        Args:
            text: Natural language text describing IDS specifications
            title: Optional title for the IDS file
            language: Language of input text ("en", "zh", or "both")
            batch_mode: If True, process each specification separately

        Returns:
            Tuple of (pipeline_json_result, ids_xml_string)
        """
        # Extract English text if needed
        if language == "en" or language == "both":
            processed_text = extract_english_text(text) if language == "both" else text
        else:
            processed_text = text

        logger.info(f"Processing text ({len(processed_text)} characters)...")

        if batch_mode:
            return await self._convert_batch(processed_text, title)
        else:
            return await self._convert_single(processed_text, title)

    async def _convert_single(
        self,
        text: str,
        title: Optional[str] = None
    ) -> Tuple[Dict[str, Any], str]:
        """Convert entire text as single input to pipeline."""
        # Run pipeline (lazy import)
        run_ids_pipeline = _get_pipeline()
        logger.info("Running IDS pipeline...")
        result_json = await run_ids_pipeline(text)

        # Convert to XML
        logger.info("Converting JSON to IDS XML...")
        xml_str = self.xml_converter.convert(
            result_json,
            title=title or "Generated IDS Specification",
            copyright="Generated by IDS-Agent Pipeline",
            version="1.0"
        )

        return result_json, xml_str

    async def _convert_batch(
        self,
        text: str,
        title: Optional[str] = None
    ) -> Tuple[Dict[str, Any], str]:
        """Process each specification separately and merge results."""
        run_ids_pipeline = _get_pipeline()
        specs = split_specifications(text)

        if not specs:
            logger.warning("No specifications found, falling back to single mode")
            return await self._convert_single(text, title)

        logger.info(f"Found {len(specs)} specifications, processing in batch mode...")

        all_results = []

        for i, (spec_name, spec_text) in enumerate(specs, 1):
            logger.info(f"Processing specification {i}/{len(specs)}: {spec_name}")
            try:
                result = await run_ids_pipeline(spec_text)
                if result.get("specifications"):
                    all_results.extend(result["specifications"])
            except Exception as e:
                logger.error(f"Failed to process specification '{spec_name}': {e}")
                continue

        # Merge all specifications into single JSON
        merged_json = {
            "specifications": all_results
        }

        # Convert to XML
        logger.info("Converting merged JSON to IDS XML...")
        xml_str = self.xml_converter.convert(
            merged_json,
            title=title or "Generated IDS Specification",
            copyright="Generated by IDS-Agent Pipeline",
            version="1.0"
        )

        return merged_json, xml_str

    def validate_xml(self, xml_str: str) -> bool:
        """
        Validate IDS XML against XSD schema.

        Args:
            xml_str: XML string to validate

        Returns:
            True if valid
        """
        from lxml import etree

        # Parse XML
        try:
            root = etree.fromstring(xml_str.encode('utf-8'))
        except etree.XMLSyntaxError as e:
            logger.error(f"XML syntax error: {e}")
            return False

        # Validate against schema
        schema = self.xml_converter._load_schema()
        if not schema.validate(root):
            for error in schema.error_log:
                logger.error(f"XSD validation error at line {error.line}: {error.message}")
            return False

        return True

    def compare_with_original(
        self,
        original_ids_path: str,
        generated_xml: str
    ) -> Dict[str, Any]:
        """
        Compare generated IDS with original IDS file.

        Args:
            original_ids_path: Path to original IDS file
            generated_xml: Generated IDS XML string

        Returns:
            Comparison report dictionary
        """
        # Parse original
        original_data = self.parser.parse_file(original_ids_path)
        original_specs = original_data.get("specifications", [])

        # Parse generated
        generated_data = self.parser.parse(generated_xml)
        generated_specs = generated_data.get("specifications", [])

        report = {
            "original_file": str(original_ids_path),
            "original_spec_count": len(original_specs),
            "generated_spec_count": len(generated_specs),
            "spec_difference": len(original_specs) - len(generated_specs),
            "original_spec_names": [s.get("name", "Unknown") for s in original_specs],
            "generated_spec_names": [s.get("name", "Unknown") for s in generated_specs],
        }

        return report


# =============================================================================
# CLI Entry Point
# =============================================================================

async def main_async():
    """Main async entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert natural language text to IDS XML"
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Input text file path (natural language description)"
    )
    parser.add_argument(
        "--output", "-o",
        required=True,
        help="Output IDS XML file path"
    )
    parser.add_argument(
        "--json-output", "-j",
        help="Optional path to save pipeline JSON result"
    )
    parser.add_argument(
        "--lang", "-l",
        choices=["en", "zh", "both"],
        default="en",
        help="Input language (default: en)"
    )
    parser.add_argument(
        "--title", "-t",
        default=None,
        help="IDS file title (default: auto-detect from first spec)"
    )
    parser.add_argument(
        "--original", "-r",
        default=None,
        help="Optional original IDS file for comparison"
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Process each specification separately (for large inputs)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Check API key
    if not os.getenv("OPENROUTER_API_KEY"):
        logger.error("OPENROUTER_API_KEY environment variable not set!")
        logger.error("Please set it before running:")
        logger.error("  export OPENROUTER_API_KEY='your-api-key'")
        sys.exit(1)

    # Read input file
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        sys.exit(1)

    logger.info(f"Reading input file: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Convert
    converter = TextToIDSConverter()

    try:
        result_json, xml_str = await converter.convert_text(
            text,
            title=args.title,
            language=args.lang,
            batch_mode=args.batch
        )

        # Save JSON result
        if args.json_output:
            logger.info(f"Saving pipeline JSON to: {args.json_output}")
            with open(args.json_output, 'w', encoding='utf-8') as f:
                json.dump(result_json, f, indent=2, ensure_ascii=False)

        # Save XML
        output_path = Path(args.output)
        logger.info(f"Saving IDS XML to: {output_path}")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(xml_str)

        # Validate
        logger.info("Validating generated XML...")
        if converter.validate_xml(xml_str):
            logger.info("XML validation passed!")
        else:
            logger.warning("XML validation failed!")

        # Compare with original
        if args.original:
            logger.info(f"Comparing with original: {args.original}")
            report = converter.compare_with_original(args.original, xml_str)

            print("\n" + "=" * 60)
            print("Comparison Report")
            print("=" * 60)
            print(f"Original specifications: {report['original_spec_count']}")
            print(f"Generated specifications: {report['generated_spec_count']}")
            print(f"Difference: {report['spec_difference']}")
            print()
            print("Original spec names:")
            for name in report['original_spec_names']:
                print(f"  - {name}")
            print()
            print("Generated spec names:")
            for name in report['generated_spec_names']:
                print(f"  - {name}")

            # Save comparison report
            report_path = output_path.parent / "comparison_report.json"
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"Comparison report saved to: {report_path}")

        print("\n" + "=" * 60)
        print("Conversion Complete!")
        print("=" * 60)
        print(f"Output: {output_path}")
        print(f"Specifications generated: {len(result_json.get('specifications', []))}")

    except XSDValidationError as e:
        logger.error(f"XSD validation failed: {e}")
        sys.exit(1)
    except IDSConversionError as e:
        logger.error(f"Conversion error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """CLI entry point."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()