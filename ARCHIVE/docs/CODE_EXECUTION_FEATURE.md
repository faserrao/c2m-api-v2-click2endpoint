# Code Execution Feature Documentation

## Overview

Click2Endpoint now includes the ability to execute the generated Python code directly from the UI and see the results without leaving the application. This feature streamlines the API testing workflow by providing immediate feedback on API calls.

## Features

### 1. **Run Code Button**
- Located in the Python tab after code generation
- Appears only after generating the complete Python script
- Executes the code in a secure subprocess with a 30-second timeout

### 2. **Progress Tracking**
Real-time progress updates during execution:
- "Starting execution..." (10%)
- "Revoking existing tokens..." (20%)
- "Obtaining long-term token..." (40%)
- "Exchanging for short-term token..." (60%)
- "Making API request..." (80%)
- "Execution complete!" (100%)

### 3. **Result Display**
Results are shown in three tabs:

#### 🎯 Summary Tab
- Parsed authentication tokens (masked for security)
- API response in formatted JSON
- Any warnings or errors encountered
- Key metrics like Job ID and Status (if available)

#### 📜 Full Output Tab
- Complete console output from the execution
- Shows all HTTP requests and responses
- Useful for debugging

#### 🔍 Raw Data Tab
- Raw execution result as JSON
- Includes stdout, stderr, return code
- Parsed output structure

## Architecture

### Code Executor Module (`code_executor.py`)

```python
class CodeExecutor:
    """Handles execution of generated API code"""
    
    def execute_python_code(self, code: str, mock_url: str) -> Dict[str, any]:
        """Execute Python code in subprocess and return results"""
    
    def _parse_output(self, stdout: str, stderr: str) -> Dict[str, any]:
        """Parse execution output to extract key information"""
    
    def format_execution_result(self, result: Dict[str, any]) -> str:
        """Format results for display in UI"""
```

### Key Components:

1. **Subprocess Execution**
   - Runs code in isolated subprocess
   - 30-second timeout prevents hanging
   - Captures both stdout and stderr

2. **Output Parsing**
   - Extracts authentication tokens
   - Parses JSON API responses
   - Identifies errors and warnings

3. **Mock Server Integration**
   - Automatically injects mock server URL
   - Replaces production URL with mock URL

## Usage

### Basic Workflow:

1. **Select endpoint** through Q&A flow
2. **Enter parameters** for the API call
3. **Generate code** by clicking "Generate Complete Python Script"
4. **Execute code** by clicking "▶️ Run Code"
5. **View results** in the execution results section

### Example Output:

```
🔐 Authentication Tokens Obtained:
- long_term: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
- short_term: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

📥 API Response:
{
  "jobId": "job-12345",
  "status": "accepted",
  "message": "Job successfully submitted",
  "createdAt": "2024-01-15T10:30:00Z"
}
```

## Security Considerations

1. **Subprocess Isolation**
   - Code runs in separate process
   - Cannot affect main application
   - Limited to 30-second execution

2. **Token Masking**
   - Full tokens shown in output (for testing)
   - Could be enhanced to mask sensitive data

3. **Mock Server Only**
   - Executes against mock server by default
   - Prevents accidental production calls

## Error Handling

The executor handles various error scenarios:

- **Timeout**: Stops execution after 30 seconds
- **Syntax Errors**: Shows Python error messages
- **API Errors**: Displays HTTP error responses
- **Network Issues**: Shows connection errors

## Testing the Feature

1. Start the application:
   ```bash
   streamlit run streamlit_app/app_hardcoded_v1.py
   ```

2. Complete a simple flow:
   - Document type: Single
   - Template: No
   - Recipients: Explicit
   - Enter minimal parameters

3. Generate and run:
   - Click "Generate Complete Python Script"
   - Click "▶️ Run Code"
   - View results in the three tabs

## Future Enhancements

1. **JavaScript Execution**
   - Add Node.js subprocess execution
   - Support for async/await patterns

2. **cURL Execution**
   - Direct shell command execution
   - Parse cURL output

3. **Result History**
   - Store execution history
   - Compare multiple runs

4. **Advanced Features**
   - Variable injection for credentials
   - Environment selection (dev/staging/prod)
   - Response validation

## Troubleshooting

### Common Issues:

1. **"No Python code found to execute"**
   - Generate the complete Python script first
   - Don't just view the preview

2. **Timeout errors**
   - Check network connectivity
   - Verify mock server is accessible

3. **Import errors**
   - Ensure `requests` package is installed
   - Check Python environment

### Debug Mode:

To see detailed execution logs:
```python
# In code_executor.py
result = subprocess.run(
    [sys.executable, "-v", temp_file],  # Add -v for verbose
    ...
)
```

## Implementation Notes

- Uses Python's `subprocess` module for safe execution
- Temporary files are created and cleaned up automatically
- Progress updates use Streamlit's native progress bar
- Results are parsed in real-time from stdout

This feature significantly improves the developer experience by providing immediate feedback on API calls without the need to copy code to another environment!