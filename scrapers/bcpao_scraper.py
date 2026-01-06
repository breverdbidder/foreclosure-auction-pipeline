"""
BCPAO (Brevard County Property Appraiser) Scraper
Enriches foreclosure records with property details from BCPAO API
"""

import httpx
import logging
import time
import random
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class BCPAOScraper:
    """Enriches records with BCPAO property data"""
    
    SEARCH_URL = "https://www.bcpao.us/api/v1/search"
    DETAIL_URL = "https://www.bcpao.us/api/v1/account"
    
    # Brevard County cities with compound names
    COMPOUND_CITIES = {
        "PALM BAY": ["PALM", "BAY"],
        "MERRITT ISLAND": ["MERRITT", "ISLAND"],
        "COCOA BEACH": ["COCOA", "BEACH"],
        "SATELLITE BEACH": ["SATELLITE", "BEACH"],
        "CAPE CANAVERAL": ["CAPE", "CANAVERAL"],
        "MELBOURNE BEACH": ["MELBOURNE", "BEACH"],
    }
    
    ZIP_TO_CITY = {
        "32907": "PALM BAY",
        "32952": "MERRITT ISLAND",
        "32931": "COCOA BEACH",
        "32937": "SATELLITE BEACH",
        "32920": "CAPE CANAVERAL",
        "32951": "MELBOURNE BEACH",
        "32903": "MELBOURNE",
        "32754": "MIMS",
        "32796": "TITUSVILLE",
        "32780": "TITUSVILLE",
        "32940": "MELBOURNE",
    }
    
    def __init__(self):
        self.client = httpx.Client(
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'},
            timeout=15
        )
    
    def enrich_record(self, court_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich court record with BCPAO property data
        
        Args:
            court_record: Court records from CourtRecordsScraper
        
        Returns:
            Enriched record with 32 fields
        """
        # Extract defendant name from case title
        title = court_record.get('case_title', '')
        parts = title.split('VS')
        defendant_full = parts[1].strip() if len(parts) > 1 else ''
        
        # Get last name for search
        defendant_parts = defendant_full.split()
        last_name = defendant_parts[-1] if defendant_parts else ''
        last_name = last_name.replace('</td>', '').strip()
        
        # Search BCPAO
        property_data = self._search_bcpao(last_name)
        
        if property_data:
            # Get detail data
            property_id = property_data.get('propertyID', '')
            detail_data = self._get_property_details(property_id) if property_id else None
            
            # Extract fields
            site_address = property_data.get('siteAddress', '')
            zip_code = site_address.split()[-1] if site_address else ''
            street, city, _ = self._parse_address(site_address, zip_code)
            
            # Extract property details
            details = self._extract_details(detail_data)
            
            # Build 32-field record
            record = {
                # Property Information (7 fields)
                "street_address": street,
                "city": city,
                "state": "FL",
                "zip": zip_code,
                "county": "Brevard",
                "parcel_number": property_data.get('parcelID', ''),
                "property_type": property_data.get('landUseCode', '').strip(),
                
                # Property Details (4 fields)
                "bedrooms": details['bedrooms'],
                "total_baths": details['total_baths'],
                "area_sqft": details['area_sqft'],
                "lot_size": details['lot_size'],
                
                # Ownership (3 fields)
                "owner_name": defendant_full,
                "owner_occupied": 0,
                "vacant_flag": 1 if "VACANT" in property_data.get('landUseCode', '').upper() else 0,
                
                # Valuation (4 fields)
                "market_value": details['market_value'],
                "land_value": details['land_value'],
                "estimated_value": details['market_value'],
                "confidence_rating": 50,
                
                # Sale History (3 fields)
                "previous_sale_price": details['previous_sale_price'],
                "last_sale_date": details['last_sale_date'],
                "previous_sale_type": details['previous_sale_type'],
                
                # Auction Info (4 fields)
                "case_number": court_record.get('case_number', ''),
                "sale_type": court_record.get('sale_type', 'Foreclosure'),
                "auction_status": court_record.get('auction_status', 'Upcoming'),
                "auction_date": court_record.get('auction_date', ''),
                
                # Lien Info (2 fields)
                "total_liens": 0,
                "total_lien_amount": 0,
                
                # Auction Results (3 fields)
                "winning_bidder_name": None,
                "winning_bid": 0,
                "win_type": None
            }
            
            return record
        
        # Return minimal record if BCPAO lookup fails
        return self._create_minimal_record(court_record, defendant_full)
    
    def _search_bcpao(self, owner_name: str) -> Optional[Dict[str, Any]]:
        """Search BCPAO by owner name"""
        try:
            response = self.client.get(
                self.SEARCH_URL,
                params={'owner': owner_name}
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    return data[0]
            
            return None
        except Exception as e:
            logger.warning(f"BCPAO search failed for {owner_name}: {e}")
            return None
    
    def _get_property_details(self, property_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed property information"""
        try:
            response = self.client.get(f"{self.DETAIL_URL}/{property_id}")
            
            if response.status_code == 200:
                time.sleep(random.uniform(0.2, 0.5))
                return response.json()
            
            return None
        except Exception as e:
            logger.warning(f"BCPAO detail lookup failed for {property_id}: {e}")
            return None
    
    def _parse_address(self, address_str: str, zip_code: str = "") -> tuple:
        """Parse address with compound city name handling"""
        if not address_str or address_str == "UNKNOWN":
            return "", "", ""
        
        parts = address_str.split()
        
        # Try compound cities
        for compound_city, city_parts in self.COMPOUND_CITIES.items():
            city_part_indices = []
            for i, part in enumerate(parts):
                if part in city_parts:
                    city_part_indices.append(i)
            
            if len(city_part_indices) == len(city_parts):
                if city_part_indices == list(range(city_part_indices[0], city_part_indices[0] + len(city_parts))):
                    street = " ".join(parts[:city_part_indices[0]])
                    return street, compound_city, zip_code
        
        # Use zip code mapping
        if zip_code and zip_code in self.ZIP_TO_CITY:
            city = self.ZIP_TO_CITY[zip_code]
            for word in city.split():
                if word in parts:
                    parts.remove(word)
            street = " ".join(parts)
            return street, city, zip_code
        
        return " ".join(parts[:-1]), parts[-1] if parts else "", zip_code
    
    def _extract_details(self, detail: Optional[Dict]) -> Dict[str, Any]:
        """Extract property details from BCPAO detail response"""
        result = {
            "bedrooms": 0,
            "total_baths": 0,
            "area_sqft": 0,
            "lot_size": 0,
            "land_value": 0,
            "market_value": 0,
            "previous_sale_price": 0,
            "last_sale_date": "",
            "previous_sale_type": ""
        }
        
        if not detail:
            return result
        
        # Extract buildings info
        if detail.get('buildings'):
            for building in detail['buildings']:
                if building.get('bldgSequence') == 1:
                    result['bedrooms'] = int(building.get('bedrooms', 0)) or 0
                    result['total_baths'] = float(building.get('baths', 0)) or 0
                    result['area_sqft'] = int(building.get('units', 0)) or 0
        
        # Extract lot size
        if detail.get('landInfo'):
            for land in detail['landInfo']:
                try:
                    acreage = float(land.get('acreage', 0))
                    result['lot_size'] = int(acreage * 43560)
                except:
                    pass
        
        # Extract market value
        market_val_str = detail.get('marketValue', '')
        if market_val_str:
            try:
                result['market_value'] = int(float(market_val_str.replace('$', '').replace(',', '')))
            except:
                pass
        
        # Extract land value
        if detail.get('valueSummary'):
            for value in detail['valueSummary']:
                if value.get('rollYear') == 2025:
                    result['land_value'] = int(value.get('assessedVal', 0)) or 0
                    break
        
        # Extract sales history
        if detail.get('salesHistory'):
            for sale in detail['salesHistory']:
                if sale.get('qualified'):
                    result['previous_sale_price'] = int(sale.get('salePrice', 0)) or 0
                    try:
                        sale_date = sale.get('saleDate', '')
                        if sale_date:
                            result['last_sale_date'] = sale_date.split('T')[0]
                    except:
                        pass
                    result['previous_sale_type'] = sale.get('deedDesc', '')
                    break
        
        return result
    
    def _create_minimal_record(self, court_record: Dict, defendant_name: str) -> Dict[str, Any]:
        """Create minimal record when BCPAO lookup fails"""
        return {
            "street_address": "",
            "city": "",
            "state": "FL",
            "zip": "",
            "county": "Brevard",
            "parcel_number": "",
            "property_type": "",
            "bedrooms": 0,
            "total_baths": 0,
            "area_sqft": 0,
            "lot_size": 0,
            "owner_name": defendant_name,
            "owner_occupied": 0,
            "vacant_flag": 0,
            "market_value": 0,
            "land_value": 0,
            "estimated_value": 0,
            "confidence_rating": 0,
            "previous_sale_price": 0,
            "last_sale_date": "",
            "previous_sale_type": "",
            "case_number": court_record.get('case_number', ''),
            "sale_type": court_record.get('sale_type', 'Foreclosure'),
            "auction_status": court_record.get('auction_status', 'Upcoming'),
            "auction_date": court_record.get('auction_date', ''),
            "total_liens": 0,
            "total_lien_amount": 0,
            "winning_bidder_name": None,
            "winning_bid": 0,
            "win_type": None
        }
    
    def __del__(self):
        self.client.close()
