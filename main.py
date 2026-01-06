#!/usr/bin/env python3
"""
Brevard County Foreclosure Auction Data Pipeline
Main orchestrator for scraping and enriching foreclosure auction data
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

from scrapers.court_scraper import CourtRecordsScraper
from scrapers.bcpao_scraper import BCPAOScraper
from utils.aggregator import DataAggregator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description='Brevard County Foreclosure Auction Data Pipeline'
    )
    parser.add_argument(
        '--start-date',
        required=True,
        help='Start date for auction search (MM-DD-YYYY)'
    )
    parser.add_argument(
        '--end-date',
        required=True,
        help='End date for auction search (MM-DD-YYYY)'
    )
    parser.add_argument(
        '--output-dir',
        default='output',
        help='Output directory for JSON files'
    )
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    logger.info(f"Starting pipeline for {args.start_date} to {args.end_date}")
    
    try:
        # Step 1: Get court records
        logger.info("Step 1: Scraping court records...")
        court_scraper = CourtRecordsScraper()
        court_records = court_scraper.scrape_by_date_range(
            args.start_date,
            args.end_date
        )
        logger.info(f"Found {len(court_records)} court records")
        
        # Step 2: Enrich with BCPAO data
        logger.info("Step 2: Enriching with BCPAO property data...")
        bcpao_scraper = BCPAOScraper()
        enriched_records = []
        
        for i, record in enumerate(court_records, 1):
            logger.info(f"Processing {i}/{len(court_records)}: {record.get('case_number')}")
            enriched = bcpao_scraper.enrich_record(record)
            enriched_records.append(enriched)
        
        # Step 3: Aggregate and validate
        logger.info("Step 3: Aggregating and validating data...")
        aggregator = DataAggregator()
        final_records = aggregator.aggregate(enriched_records)
        
        # Step 4: Save output
        output_file = output_dir / 'foreclosures.json'
        with open(output_file, 'w') as f:
            json.dump(final_records, f, indent=2)
        logger.info(f"Saved {len(final_records)} records to {output_file}")
        
        # Step 5: Generate metadata
        metadata = aggregator.generate_metadata(final_records)
        metadata_file = output_dir / 'metadata.json'
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Saved metadata to {metadata_file}")
        
        logger.info("Pipeline completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
