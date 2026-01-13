"""
One-time script to get YouTube API refresh token
Run this locally, not on Railway
"""
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json

# YouTube API scopes
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_refresh_token():
    """Get refresh token from OAuth flow"""
    print("Starting OAuth flow...")
    print("A browser window will open. Please authorize the application.")
    
    # Get credentials from environment or user input
    client_id = input("Enter your Client ID: ").strip()
    client_secret = input("Enter your Client Secret: ").strip()
    
    # Create OAuth flow
    flow = InstalledAppFlow.from_client_config(
        {
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost"]
            }
        },
        SCOPES
    )
    
    # Run OAuth flow
    creds = flow.run_local_server(port=0)
    
    # Get refresh token
    refresh_token = creds.refresh_token
    
    print("\n" + "="*50)
    print("SUCCESS! Your refresh token is:")
    print("="*50)
    print(refresh_token)
    print("="*50)
    print("\nSave this token and add it to Railway as YOUTUBE_REFRESH_TOKEN")
    
    return refresh_token

if __name__ == '__main__':
    get_refresh_token()

