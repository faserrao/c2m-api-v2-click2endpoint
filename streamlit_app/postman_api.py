"""
Postman API Integration
Fetches mock server URLs dynamically from Postman
"""

import os
import requests
from typing import List, Dict, Optional, Any
import streamlit as st

class PostmanAPI:
    def __init__(self, api_key: str = None):
        """Initialize Postman API client"""
        self.api_key = api_key or os.getenv("POSTMAN_API_KEY", "")
        self.base_url = "https://api.getpostman.com"
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
    
    def get_workspaces(self) -> List[Dict[str, Any]]:
        """Get all workspaces accessible to the user"""
        if not self.api_key:
            return []
        
        try:
            response = requests.get(
                f"{self.base_url}/workspaces",
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            return data.get("workspaces", [])
        except Exception as e:
            st.error(f"Failed to fetch workspaces: {str(e)}")
            return []
    
    def get_collections(self, workspace_id: str = None) -> List[Dict[str, Any]]:
        """Get all collections, optionally filtered by workspace"""
        if not self.api_key:
            return []
        
        try:
            url = f"{self.base_url}/collections"
            if workspace_id:
                url += f"?workspace={workspace_id}"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data.get("collections", [])
        except Exception as e:
            st.error(f"Failed to fetch collections: {str(e)}")
            return []
    
    def get_mock_servers(self) -> List[Dict[str, Any]]:
        """Get all mock servers"""
        if not self.api_key:
            return []
        
        try:
            response = requests.get(
                f"{self.base_url}/mocks",
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            return data.get("mocks", [])
        except Exception as e:
            st.error(f"Failed to fetch mock servers: {str(e)}")
            return []
    
    def get_mock_server_details(self, mock_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific mock server"""
        if not self.api_key:
            return None
        
        try:
            response = requests.get(
                f"{self.base_url}/mocks/{mock_id}",
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            return data.get("mock", {})
        except Exception as e:
            st.error(f"Failed to fetch mock server details: {str(e)}")
            return None
    
    def find_c2m_mock_servers(self, collection_name: str = "C2M API v2") -> List[Dict[str, Any]]:
        """Find mock servers associated with C2M API collections"""
        mock_servers = self.get_mock_servers()
        c2m_mocks = []
        
        for mock in mock_servers:
            # Check if the mock server name contains C2M or matches collection
            if collection_name.lower() in mock.get("name", "").lower() or \
               "c2m" in mock.get("name", "").lower():
                # Add the mock URL
                mock_url = f"https://{mock.get('id', '')}.mock.pstmn.io"
                mock["url"] = mock_url
                c2m_mocks.append(mock)
        
        return c2m_mocks
    
    def select_mock_server_ui(self) -> Optional[str]:
        """Streamlit UI for selecting a mock server"""
        if not self.api_key:
            st.warning("⚠️ Postman API key not configured. Using default mock server URL.")
            return None
        
        st.markdown("### 🔍 Select Postman Mock Server")
        
        # Get workspaces
        workspaces = self.get_workspaces()
        if not workspaces:
            st.error("No workspaces found. Please check your API key.")
            return None
        
        # Workspace selection
        workspace_names = ["All Workspaces"] + [w["name"] for w in workspaces]
        selected_workspace = st.selectbox(
            "Select workspace:",
            workspace_names,
            key="postman_workspace"
        )
        
        # Get mock servers
        c2m_mocks = self.find_c2m_mock_servers()
        
        if not c2m_mocks:
            st.warning("No C2M mock servers found.")
            return None
        
        # Mock server selection
        mock_options = {}
        for mock in c2m_mocks:
            workspace_name = next((w["name"] for w in workspaces if w["id"] == mock.get("workspace")), "Unknown")
            display_name = f"{mock['name']} ({workspace_name})"
            mock_options[display_name] = mock
        
        selected_mock_name = st.selectbox(
            "Select mock server:",
            list(mock_options.keys()),
            key="postman_mock_server"
        )
        
        selected_mock = mock_options[selected_mock_name]
        
        # Display mock server details
        with st.expander("Mock Server Details"):
            st.json({
                "Name": selected_mock["name"],
                "ID": selected_mock["id"],
                "URL": selected_mock["url"],
                "Workspace": next((w["name"] for w in workspaces if w["id"] == selected_mock.get("workspace")), "Unknown"),
                "Created": selected_mock.get("createdAt", "Unknown")
            })
        
        return selected_mock["url"]