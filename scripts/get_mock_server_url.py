#!/usr/bin/env python3
"""
CLI tool to get the Postman mock server URL
Automatically discovers collections with mock servers
"""
import os
import sys
import requests
import argparse
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

def get_all_collections(api_key):
    """Get all collections from Postman"""
    headers = {"X-Api-Key": api_key}
    collections_url = "https://api.getpostman.com/collections"
    
    response = requests.get(collections_url, headers=headers)
    response.raise_for_status()
    
    return response.json()["collections"]

def get_all_mock_servers(api_key):
    """Get all mock servers from Postman"""
    headers = {"X-Api-Key": api_key}
    mocks_url = "https://api.getpostman.com/mocks"
    
    response = requests.get(mocks_url, headers=headers)
    response.raise_for_status()
    
    return response.json()["mocks"]

def find_collections_with_mocks(api_key):
    """Find all collections that have associated mock servers"""
    collections = get_all_collections(api_key)
    mocks = get_all_mock_servers(api_key)
    
    # Create a map of collection UID to collection info
    collection_map = {col["uid"]: col for col in collections}
    
    # Find collections with mock servers
    collections_with_mocks = []
    
    for mock in mocks:
        collection_uid = mock.get("collection")
        if collection_uid and collection_uid in collection_map:
            collection = collection_map[collection_uid]
            collections_with_mocks.append({
                "collection_name": collection["name"],
                "collection_uid": collection["uid"],
                "mock_name": mock["name"],
                "mock_url": mock["mockUrl"],
                "mock_id": mock["id"],
                "environment": mock.get("environment", "N/A")
            })
    
    return collections_with_mocks

def select_workspace_interactive():
    """Let user select between personal and team workspace"""
    print("\nSelect Postman workspace:")
    print("1. Personal workspace")
    print("2. Team workspace")
    
    while True:
        try:
            choice = input("\nEnter choice (1-2): ")
            if choice == "1":
                return "personal"
            elif choice == "2":
                return "team"
            else:
                print("Invalid choice. Please enter 1 or 2.")
        except (ValueError, EOFError, KeyboardInterrupt):
            print("\nCancelled.")
            return None

def select_mock_interactive(collections_with_mocks):
    """Let user select a mock server if multiple are found"""
    if len(collections_with_mocks) == 0:
        print("No collections with mock servers found.")
        return None
    
    if len(collections_with_mocks) == 1:
        # Only one mock server, use it automatically
        return collections_with_mocks[0]
    
    # Multiple mock servers found, let user choose
    print(f"\nFound {len(collections_with_mocks)} collections with mock servers:\n")
    
    for i, item in enumerate(collections_with_mocks, 1):
        print(f"{i}. Collection: {item['collection_name']}")
        print(f"   Mock: {item['mock_name']}")
        print(f"   URL: {item['mock_url']}")
        print()
    
    while True:
        try:
            choice = input(f"Select mock server (1-{len(collections_with_mocks)}): ")
            index = int(choice) - 1
            if 0 <= index < len(collections_with_mocks):
                return collections_with_mocks[index]
            else:
                print("Invalid choice. Please try again.")
        except (ValueError, EOFError, KeyboardInterrupt):
            print("\nCancelled.")
            return None

def main():
    parser = argparse.ArgumentParser(
        description="Get Postman mock server URL - automatically discovers collections with mocks"
    )
    parser.add_argument(
        "--api-key",
        help="Postman API key (or set POSTMAN_API_KEY_PERSONAL/TEAM env var)",
        default=None
    )
    parser.add_argument(
        "--workspace",
        choices=["personal", "team"],
        default=None,
        help="Use personal or team workspace (interactive if not specified)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Show all collections with mock servers (no interactive selection)"
    )
    parser.add_argument(
        "--url-only",
        action="store_true",
        help="Output only the mock server URL"
    )
    
    args = parser.parse_args()
    
    # If workspace not specified via command line, ask interactively
    if args.workspace is None and not args.all:
        args.workspace = select_workspace_interactive()
        if args.workspace is None:
            sys.exit(1)
    elif args.workspace is None:
        # For --all, default to personal to avoid interactive prompt
        args.workspace = "personal"
    
    # Determine API key based on workspace
    if not args.api_key:
        if args.workspace == "team":
            args.api_key = os.environ.get("POSTMAN_API_KEY_TEAM")
            if not args.api_key:
                print("Error: Team Postman API key required")
                print("Set POSTMAN_API_KEY_TEAM environment variable or use --api-key")
                sys.exit(1)
        else:
            args.api_key = os.environ.get("POSTMAN_API_KEY_PERSONAL")
            if not args.api_key:
                print("Error: Personal Postman API key required")
                print("Set POSTMAN_API_KEY_PERSONAL environment variable or use --api-key")
                sys.exit(1)
    
    try:
        # Find all collections with mock servers
        collections_with_mocks = find_collections_with_mocks(args.api_key)
        
        if not collections_with_mocks:
            print(f"No collections with mock servers found in your {args.workspace} Postman workspace.")
            sys.exit(1)
        
        if args.all:
            # Show all without selection
            if args.json:
                print(json.dumps(collections_with_mocks, indent=2))
            else:
                for item in collections_with_mocks:
                    print(f"Collection: {item['collection_name']}")
                    print(f"Mock: {item['mock_name']}")
                    print(f"URL: {item['mock_url']}")
                    print("-" * 50)
        else:
            # Interactive selection or auto-select if only one
            selected = select_mock_interactive(collections_with_mocks)
            
            if selected:
                if args.url_only:
                    print(selected['mock_url'])
                elif args.json:
                    print(json.dumps(selected, indent=2))
                else:
                    print(f"\nSelected Mock Server ({args.workspace} workspace):")
                    print(f"Collection: {selected['collection_name']}")
                    print(f"Mock: {selected['mock_name']}")
                    print(f"URL: {selected['mock_url']}")
            else:
                sys.exit(1)
                
    except requests.exceptions.RequestException as e:
        print(f"Error accessing Postman API: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()