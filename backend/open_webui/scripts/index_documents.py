#!/usr/bin/env python3
"""
CLI script for indexing policy documents.

Usage:
    python -m open_webui.scripts.index_documents --source-id <id>
    python -m open_webui.scripts.index_documents --all
    python -m open_webui.scripts.index_documents --reindex
    python -m open_webui.scripts.index_documents --create-index
"""

import argparse
import asyncio
import logging
import sys
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)


def print_banner():
    """Print script banner."""
    print("=" * 70)
    print("Policy Scanner - Document Indexing Tool")
    print("=" * 70)
    print()


def print_stats(stats):
    """
    Print indexing statistics.

    Args:
        stats: IndexingStats object
    """
    print("\n" + "=" * 70)
    print("INDEXING SUMMARY")
    print("=" * 70)
    print(f"Total documents:     {stats.total_documents}")
    print(f"Processed:           {stats.processed}")
    print(f"Successfully indexed: {stats.indexed}")
    print(f"Failed:              {stats.failed}")
    print(f"Skipped:             {stats.skipped}")
    print(f"Duration:            {stats.duration_seconds:.2f} seconds")
    print("=" * 70)

    if stats.errors:
        print(f"\nErrors ({len(stats.errors)}):")
        for i, error in enumerate(stats.errors[:10], 1):
            print(f"  {i}. Document {error['document_id']}: {error['error']}")
        if len(stats.errors) > 10:
            print(f"  ... and {len(stats.errors) - 10} more errors")


async def create_index():
    """Create and configure the Meilisearch index."""
    from open_webui.services.meilisearch_service import get_meilisearch_service

    print("Creating Meilisearch index...")
    meili = get_meilisearch_service()
    await meili.connect()

    try:
        # Check if index exists
        stats = await meili.get_stats()
        print(f"Index already exists with {stats.get('numberOfDocuments', 0)} documents")

        response = input("Do you want to recreate the index? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            return

        # Delete existing index
        print("Deleting existing index...")
        await meili.delete_index()

    except Exception as e:
        log.debug(f"Index does not exist: {e}")

    # Create new index
    print("Creating new index with configuration...")
    await meili.create_index()
    print("Index created successfully!")

    await meili.disconnect()


async def index_documents(
    source_id=None,
    reindex=False,
    max_documents=None,
    batch_size=None
):
    """
    Index documents.

    Args:
        source_id: Filter by source ID
        reindex: Force reindex of already indexed documents
        max_documents: Maximum documents to index
        batch_size: Batch size for processing
    """
    from open_webui.services.indexing_service import IndexingService

    # Create indexing service
    if batch_size:
        indexer = IndexingService(batch_size=batch_size)
    else:
        indexer = IndexingService()

    # Determine status filter
    status = "pending" if not reindex else None

    # Run indexing
    print(f"\nStarting indexing...")
    if source_id:
        print(f"  Source ID: {source_id}")
    else:
        print(f"  Source ID: all")
    print(f"  Status filter: {status or 'all (reindexing)'}")
    print(f"  Batch size: {indexer.batch_size}")
    if max_documents:
        print(f"  Max documents: {max_documents}")
    print()

    stats = await indexer.index_documents(
        source_id=source_id,
        status=status,
        force_reindex=reindex,
        max_documents=max_documents
    )

    return stats


async def get_status():
    """Get indexing status."""
    from open_webui.services.indexing_service import get_indexing_service

    indexer = get_indexing_service()
    status = await indexer.get_indexing_status()

    print("\n" + "=" * 70)
    print("INDEXING STATUS")
    print("=" * 70)
    print("\nDatabase status:")
    for state, count in status.get('database', {}).items():
        print(f"  {state.ljust(12)}: {count}")

    meili = status.get('meilisearch', {})
    if meili:
        print(f"\nMeilisearch:")
        print(f"  Documents: {meili.get('numberOfDocuments', 0)}")
        print(f"  Is indexing: {meili.get('isIndexing', False)}")

    print("=" * 70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Index policy documents into Meilisearch',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create/recreate the index
  python -m open_webui.scripts.index_documents --create-index

  # Index all pending documents
  python -m open_webui.scripts.index_documents --all

  # Index documents from specific source
  python -m open_webui.scripts.index_documents --source-id abc123

  # Force reindex of all documents
  python -m open_webui.scripts.index_documents --all --reindex

  # Index with custom batch size
  python -m open_webui.scripts.index_documents --all --batch-size 50

  # Get indexing status
  python -m open_webui.scripts.index_documents --status
        """
    )

    parser.add_argument(
        '--source-id',
        type=str,
        help='Index documents from specific source ID'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Index all documents (default: only pending)'
    )
    parser.add_argument(
        '--reindex',
        action='store_true',
        help='Force reindex of already indexed documents'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        help='Number of documents to process per batch (default: 100)'
    )
    parser.add_argument(
        '--max',
        type=int,
        help='Maximum number of documents to index'
    )
    parser.add_argument(
        '--create-index',
        action='store_true',
        help='Create/recreate the Meilisearch index'
    )
    parser.add_argument(
        '--status',
        action='store_true',
        help='Show indexing status'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Configure logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Print banner
    print_banner()

    # Run appropriate command
    try:
        if args.create_index:
            asyncio.run(create_index())
        elif args.status:
            asyncio.run(get_status())
        else:
            # Index documents
            if not args.all and not args.source_id:
                parser.error("Must specify --all or --source-id")

            stats = asyncio.run(index_documents(
                source_id=args.source_id,
                reindex=args.reindex,
                max_documents=args.max,
                batch_size=args.batch_size
            ))

            print_stats(stats)

            # Exit with error code if there were failures
            if stats.failed > 0:
                sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nIndexing interrupted by user")
        sys.exit(130)
    except Exception as e:
        log.exception(f"Indexing failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
