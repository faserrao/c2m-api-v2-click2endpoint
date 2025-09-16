# Postman API Integration

The C2M Endpoint Navigator can now fetch mock server URLs directly from your Postman account, ensuring you're always using the correct mock server.

## Setup

### 1. Get Your Postman API Key

1. Go to [Postman API Keys](https://postman.com/settings/me/api-keys)
2. Click "Generate API Key"
3. Give it a name (e.g., "C2M Endpoint Navigator")
4. Copy the API key

### 2. Configure the Integration

#### Option A: Environment Variable (Recommended)
```bash
export POSTMAN_API_KEY="your-api-key-here"
```

#### Option B: Update config.yaml
```yaml
postman:
  enabled: true
  api_key: "your-api-key-here"  # Better to use env variable
```

### 3. Enable the Integration

In `config.yaml`, set:
```yaml
postman:
  enabled: true
```

## Usage

1. Start the Endpoint Navigator
2. In the sidebar, you'll see "🔗 Postman Integration"
3. Click "Select Mock Server"
4. Choose your workspace (Personal or Team)
5. Select the C2M API mock server
6. Click "Use This Mock Server"

The app will now use the selected mock server URL for all generated SDK code.

## Features

- **Dynamic Mock Server Discovery**: Automatically finds all C2M-related mock servers
- **Workspace Support**: Switch between personal and team workspaces
- **Real-time Updates**: Always uses the current mock server URL from Postman
- **No Manual Configuration**: No need to update URLs in config files

## Security Note

Never commit your Postman API key to version control. Always use environment variables or secure secret management.