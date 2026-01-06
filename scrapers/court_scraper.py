"""
Brevard County Court Records Scraper
Extracts foreclosure auction data from Brevard County Clerk website
"""

import httpx
import logging
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class CourtRecordsScraper:
    """Scrapes foreclosure auction records from Brevard County Clerk"""
    
    BASE_URL = "http://vweb2.brevardclerk.us/Foreclosures/foreclosure_sales.html"
    
    def __init__(self):
        self.client = httpx.Client(
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'},
            timeout=30
        )
    
    def scrape_by_date_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Scrape foreclosure records for a date range
        
        Args:
            start_date: Start date (MM-DD-YYYY)
            end_date: End date (MM-DD-YYYY)
        
        Returns:
            List of case records
        """
        try:
            response = self.client.get(self.BASE_URL)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            records = []
            for row in soup.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) >= 4:
                    case_num = cells[0].get_text(strip=True)
                    case_title = cells[1].get_text(strip=True)
                    status = cells[2].get_text(strip=True)
                    date_str = cells[3].get_text(strip=True)
                    
                    # Parse date
                    try:
                        auction_date = datetime.strptime(date_str, '%m-%d-%Y')
                        start = datetime.strptime(start_date, '%m-%d-%Y')
                        end = datetime.strptime(end_date, '%m-%d-%Y')
                        
                        if start <= auction_date <= end:
                            record = {
                                'case_number': case_num,
                                'case_title': case_title,
                                'auction_status': status if status else 'Upcoming',
                                'auction_date': date_str,
                                'sale_type': 'Foreclosure'
                            }
                            records.append(record)
                    except ValueError:
                        continue
            
            logger.info(f"Found {len(records)} records for {start_date} to {end_date}")
            return records
            
        except Exception as e:
            logger.error(f"Error scraping court records: {e}")
            return []
    
    def __del__(self):
        self.client.close()
