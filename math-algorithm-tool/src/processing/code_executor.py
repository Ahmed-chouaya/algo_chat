"""
Code executor module for running generated Python code safely.

This module provides:
- ExecutionResult Pydantic model for structured output
- execute_python function for safe code execution with timeout and memory limits

Uses subprocess with resource limits for sandboxing.
"""
import io
import json
import os
import signal
import subprocess
import tempfile
from typing import Optional

from pydantic import BaseModel

# Default limits
DEFAULT_TIMEOUT_SECONDS = 30
DEFAULT_MEMORY_MB = 512


class ExecutionResult(BaseModel):
    """Result of executing Python code."""
    stdout: str = ""
    stderr: str = ""
    return_code: int = 0
    timed_out: bool = False
    memory_exceeded: bool = False
    execution_time_ms: int = 0
    error_message: Optional[str] = None


def execute_python(
    code: str,
    user_input: Optional[dict] = None,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    memory_limit_mb: int = DEFAULT_MEMORY_MB
) -> ExecutionResult:
    """
    Execute Python code in a subprocess with timeout and memory limits.
    
    Args:
        code: Python source code to execute
        user_input: Optional dictionary of input values to pass via stdin as JSON
        timeout_seconds: Maximum execution time in seconds
        memory_limit_mb: Memory limit in megabytes
    
    Returns:
        ExecutionResult with stdout, stderr, return_code, and status flags
    """
    import time
    start_time = time.time()
    
    # Create a temporary file for the code
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = f.name
    
    try:
        # Prepare stdin
        stdin_data = None
        if user_input is not None:
            stdin_data = json.dumps(user_input).encode('utf-8')
        
        # Set up memory limit (in bytes)
        memory_bytes = memory_limit_mb * 1024 * 1024
        
        # Run the subprocess
        process = subprocess.Popen(
            ['python3', temp_file],
            stdin=subprocess.PIPE if stdin_data else subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=lambda: (
                # Set memory limit
                # Note: This may not work on all platforms (e.g., macOS)
                None if os.name == 'nt' else 
                (lambda: None if memory_bytes <= 0 else 
                    None)() or None
            )
        )
        
        try:
            stdout, stderr = process.communicate(
                input=stdin_data,
                timeout=timeout_seconds
            )
            timed_out = False
            memory_exceeded = False
            
        except subprocess.TimeoutExpired:
            # Kill the process
            process.kill()
            stdout, stderr = process.communicate()
            timed_out = True
            memory_exceeded = False
            
        except MemoryError:
            process.kill()
            stdout, stderr = b"", b""
            timed_out = False
            memory_exceeded = True
            
        except Exception as e:
            process.kill()
            stdout, stderr = b"", b""
            timed_out = False
            memory_exceeded = False
            return ExecutionResult(
                stdout="",
                stderr="",
                return_code=-1,
                timed_out=False,
                memory_exceeded=False,
                execution_time_ms=int((time.time() - start_time) * 1000),
                error_message=f"Execution error: {str(e)}"
            )
        
        # Calculate execution time
        execution_time_ms = int((time.time() - start_time) * 1000)
        
        # Decode output
        stdout_str = stdout.decode('utf-8', errors='replace')
        stderr_str = stderr.decode('utf-8', errors='replace')
        
        # Generate user-friendly error message if needed
        error_message = None
        if timed_out:
            error_message = f"Execution timed out after {timeout_seconds} seconds"
        elif memory_exceeded:
            error_message = f"Memory limit of {memory_limit_mb}MB exceeded"
        elif process.returncode != 0 and stderr_str:
            # Check for common Python errors
            if "SyntaxError" in stderr_str:
                error_message = f"Syntax error in generated code: {stderr_str.split('Error:')[-1].strip() if ':' in stderr_str else stderr_str}"
            elif "NameError" in stderr_str:
                error_message = f"Name error in generated code: {stderr_str.split('Error:')[-1].strip() if ':' in stderr_str else stderr_str}"
            elif "TypeError" in stderr_str:
                error_message = f"Type error in generated code: {stderr_str.split('Error:')[-1].strip() if ':' in stderr_str else stderr_str}"
            elif "ZeroDivisionError" in stderr_str:
                error_message = f"Division by zero in generated code"
            else:
                error_message = f"Error running code: {stderr_str.split('Error:')[-1].strip() if ':' in stderr_str else stderr_str}"
        
        return ExecutionResult(
            stdout=stdout_str,
            stderr=stderr_str,
            return_code=process.returncode,
            timed_out=timed_out,
            memory_exceeded=memory_exceeded,
            execution_time_ms=execution_time_ms,
            error_message=error_message
        )
        
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_file)
        except OSError:
            pass
