import unittest
from unittest.mock import Mock, patch
import sys
import os
import json

# Add the parent directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from foundation.federation.gateway import FederationGateway
from foundation.federation.manager import FederationManager
from foundation.federation.query import QueryBuilder
from foundation.federation.models import FederatedEntity, DataSource
from foundation.federation.sync import SyncManager


class TestDataFederation(unittest.TestCase):
    """
    Integration tests for the data federation system, verifying that
    components work together to enable cross-agency data sharing.
    """
    
    def setUp(self):
        """Set up the test environment."""
        # Create mock data sources
        self.cdc_source = Mock(spec=DataSource)
        self.cdc_source.id = "cdc"
        self.cdc_source.name = "CDC"
        self.cdc_source.url = "https://api.cdc.gov"
        
        self.usda_source = Mock(spec=DataSource)
        self.usda_source.id = "usda"
        self.usda_source.name = "USDA"
        self.usda_source.url = "https://api.usda.gov"
        
        # Configure mock responses
        self.cdc_source.query.return_value = [
            {"id": "case1", "location": "New York", "date": "2023-05-01", "type": "human"},
            {"id": "case2", "location": "California", "date": "2023-05-02", "type": "human"}
        ]
        
        self.usda_source.query.return_value = [
            {"id": "case3", "location": "Iowa", "date": "2023-05-01", "type": "poultry"},
            {"id": "case4", "location": "Wisconsin", "date": "2023-05-03", "type": "wild_bird"}
        ]
        
        # Initialize federation components
        self.data_sources = {"cdc": self.cdc_source, "usda": self.usda_source}
        self.federation_manager = FederationManager(self.data_sources)
        self.gateway = FederationGateway(self.federation_manager)
        self.query_builder = QueryBuilder()
        self.sync_manager = SyncManager(self.federation_manager)

    def test_federation_query_across_data_sources(self):
        """
        Test querying data across multiple federated data sources.
        Verifies that the query builder, federation manager, and gateway
        work together to collect and merge data from different sources.
        """
        # Build a query for bird flu cases across all data sources
        query = self.query_builder.select(["id", "location", "date", "type"]) \
            .where(date_from="2023-05-01", date_to="2023-05-03") \
            .build()
            
        # Execute the query through the federation gateway
        results = self.gateway.execute_query(query)
        
        # Verify query was executed against all data sources
        self.cdc_source.query.assert_called_once()
        self.usda_source.query.assert_called_once()
        
        # Verify results were merged correctly
        self.assertEqual(len(results), 4)  # All records from both sources
        
        # Verify source attribution in results
        sources = set(result.get("_source", "") for result in results)
        self.assertTrue("cdc" in sources or "usda" in sources)
        
        # Verify all required fields are present
        for result in results:
            self.assertIn("id", result)
            self.assertIn("location", result)
            self.assertIn("date", result)
            self.assertIn("type", result)

    def test_federation_filtered_query(self):
        """
        Test querying with filters that apply across federated data sources.
        """
        # Build a query for only poultry and wild bird cases
        query = self.query_builder.select(["id", "location", "date", "type"]) \
            .where(type=["poultry", "wild_bird"]) \
            .build()
            
        # Execute the query
        results = self.gateway.execute_query(query)
        
        # Verify filtering works correctly
        self.assertEqual(len(results), 2)  # Only the USDA records match
        
        # All results should be poultry or wild_bird type
        for result in results:
            self.assertIn(result.get("type"), ["poultry", "wild_bird"])

    @patch("foundation.federation.sync.SyncManager._perform_sync")
    def test_data_synchronization(self, mock_sync):
        """
        Test the data synchronization process between federated data sources.
        """
        # Configure mock
        mock_sync.return_value = {
            "cdc": {"status": "success", "records_processed": 10},
            "usda": {"status": "success", "records_processed": 15}
        }
        
        # Run synchronization
        sync_result = self.sync_manager.synchronize(
            entity_type="avian_influenza_case",
            sync_mode="incremental",
            date_from="2023-05-01"
        )
        
        # Verify sync was called with correct parameters
        mock_sync.assert_called_once()
        call_args = mock_sync.call_args[0]
        self.assertEqual(call_args[0], "avian_influenza_case")
        self.assertEqual(call_args[1], "incremental")
        
        # Verify sync results are returned correctly
        self.assertIn("cdc", sync_result)
        self.assertIn("usda", sync_result)
        self.assertEqual(sync_result["cdc"]["status"], "success")
        self.assertEqual(sync_result["usda"]["status"], "success")

    def test_federation_governance(self):
        """
        Test the federation governance rules are properly applied during queries.
        """
        # Mock the governance check method
        with patch("foundation.federation.governance.check_access_permission") as mock_check:
            mock_check.return_value = {
                "cdc": True,  # Allow access to CDC
                "usda": False  # Deny access to USDA
            }
            
            # Create query
            query = self.query_builder.select(["id", "location", "date", "type"]).build()
            
            # Execute with governance checks (with user context)
            results = self.gateway.execute_query(
                query, 
                user_id="test_user",
                apply_governance=True
            )
            
            # Verify only CDC data is returned (USDA filtered by governance)
            self.assertEqual(len(results), 2)
            
            # Verify all results are from CDC
            for result in results:
                self.assertEqual(result.get("_source"), "cdc")
                
            # Verify CDC source was queried but USDA was not
            self.cdc_source.query.assert_called_once()
            self.usda_source.query.assert_not_called()


if __name__ == "__main__":
    unittest.main()