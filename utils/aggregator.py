"""
Data Aggregation and Validation
Combines data from multiple sources and validates against schema
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class DataAggregator:
    """Aggregates and validates foreclosure data"""
    
    # Required fields that must be present
    REQUIRED_FIELDS = [
        'case_number',
        'auction_date',
        'auction_status',
        'sale_type',
        'state',
        'county',
        'owner_name',
        'property_type'
    ]
    
    # All 32 fields in schema
    ALL_FIELDS = [
        'street_address', 'city', 'state', 'zip', 'county', 'parcel_number', 'property_type',
        'bedrooms', 'total_baths', 'area_sqft', 'lot_size',
        'owner_name', 'owner_occupied', 'vacant_flag',
        'market_value', 'land_value', 'estimated_value', 'confidence_rating',
        'previous_sale_price', 'last_sale_date', 'previous_sale_type',
        'case_number', 'sale_type', 'auction_status', 'auction_date',
        'total_liens', 'total_lien_amount',
        'winning_bidder_name', 'winning_bid', 'win_type'
    ]
    
    def aggregate(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Aggregate records and ensure all have 32 fields
        
        Args:
            records: List of enriched records
        
        Returns:
            List of validated records with all 32 fields
        """
        aggregated = []
        
        for record in records:
            # Ensure all fields present
            for field in self.ALL_FIELDS:
                if field not in record:
                    record[field] = None if field.endswith('_name') or field.endswith('_type') else 0
            
            aggregated.append(record)
        
        logger.info(f"Aggregated {len(aggregated)} records")
        return aggregated
    
    def generate_metadata(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate metadata about the dataset
        
        Args:
            records: List of validated records
        
        Returns:
            Metadata dictionary
        """
        metadata = {
            'total_records': len(records),
            'field_population_rate': self._calculate_field_population(records),
            'status_breakdown': self._get_status_breakdown(records),
            'property_type_breakdown': self._get_property_type_breakdown(records),
            'value_summary': self._get_value_summary(records),
            'required_fields_compliance': self._check_required_fields(records)
        }
        
        return metadata
    
    def _calculate_field_population(self, records: List[Dict]) -> float:
        """Calculate percentage of populated fields"""
        if not records:
            return 0.0
        
        total_fields = len(records) * len(self.ALL_FIELDS)
        populated = sum(
            1 for record in records
            for value in record.values()
            if value not in (None, 0, "", [])
        )
        
        return (populated / total_fields * 100) if total_fields > 0 else 0.0
    
    def _get_status_breakdown(self, records: List[Dict]) -> Dict[str, int]:
        """Get breakdown by auction status"""
        breakdown = {}
        for record in records:
            status = record.get('auction_status', 'Unknown')
            breakdown[status] = breakdown.get(status, 0) + 1
        return breakdown
    
    def _get_property_type_breakdown(self, records: List[Dict]) -> Dict[str, int]:
        """Get breakdown by property type"""
        breakdown = {}
        for record in records:
            ptype = record.get('property_type', 'Unknown')
            breakdown[ptype] = breakdown.get(ptype, 0) + 1
        return breakdown
    
    def _get_value_summary(self, records: List[Dict]) -> Dict[str, Any]:
        """Get summary of property values"""
        values = [r.get('market_value', 0) for r in records if r.get('market_value')]
        
        if not values:
            return {
                'total': 0,
                'average': 0,
                'min': 0,
                'max': 0
            }
        
        return {
            'total': sum(values),
            'average': sum(values) // len(values),
            'min': min(values),
            'max': max(values)
        }
    
    def _check_required_fields(self, records: List[Dict]) -> Dict[str, Any]:
        """Check compliance with required fields"""
        compliance = {}
        
        for field in self.REQUIRED_FIELDS:
            populated = sum(
                1 for record in records
                if record.get(field) not in (None, 0, "")
            )
            compliance[field] = {
                'populated': populated,
                'total': len(records),
                'rate': (populated / len(records) * 100) if records else 0
            }
        
        return compliance
