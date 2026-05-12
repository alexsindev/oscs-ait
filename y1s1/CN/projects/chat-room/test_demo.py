#!/usr/bin/env python3
"""
Test script for Chat Room Application
Tests basic functionality of the server and client
"""

import subprocess
import time
import signal
import os
import sys

def run_test():
    """Run basic functionality test"""
    print("=== Chat Room Application Test ===\n")
    
    # Start server
    print("1. Starting server...")
    server_process = subprocess.Popen(
        [sys.executable, "server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Give server time to start
    time.sleep(2)
    
    # Check if server is running
    if server_process.poll() is not None:
        print("❌ Server failed to start")
        stdout, stderr = server_process.communicate()
        print(f"STDOUT: {stdout}")
        print(f"STDERR: {stderr}")
        return False
    
    print("✅ Server started successfully")
    
    try:
        # Test client connection (manual for now)
        print("\n2. Manual Test Required:")
        print("   - Open another terminal")
        print("   - Run: python3 client.py")
        print("   - Enter username: testuser")
        print("   - Type some messages")
        print("   - Use /users command")
        print("   - Open a third terminal and connect another client")
        print("   - Test private messaging with /msg command")
        print("   - Use /quit to disconnect cleanly")
        
        print("\n3. Server is running. Press Ctrl+C to stop the test.")
        
        # Keep server running for manual testing
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n\n4. Stopping server...")
        
    finally:
        # Clean up server process
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
            print("✅ Server stopped cleanly")
        except subprocess.TimeoutExpired:
            server_process.kill()
            print("⚠️  Server killed forcefully")
    
    return True

def check_files():
    """Check if all required files exist"""
    required_files = [
        "server.py",
        "client.py",
        "PROJECT_PROPOSAL.md",
        "PROTOCOL_SPECIFICATION.md",
        "README.md"
    ]
    
    print("Checking required files:")
    all_exist = True
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - Missing!")
            all_exist = False
    
    return all_exist

def main():
    """Main test function"""
    print("Chat Room Application - Test Suite")
    print("=" * 40)
    
    # Check files
    if not check_files():
        print("\n❌ Some required files are missing!")
        return False
    
    print("\n✅ All required files present")
    
    # Run functionality test
    print("\nStarting functionality test...")
    success = run_test()
    
    if success:
        print("\n✅ Test completed successfully!")
        print("\nTo create a proper demo:")
        print("1. Record terminal sessions showing:")
        print("   - Server starting")
        print("   - Multiple clients connecting")
        print("   - Public chat messages")
        print("   - Private messages")
        print("   - User list commands")
        print("   - Graceful disconnections")
        print("2. Show error handling (duplicate username, etc.)")
        print("3. Demonstrate protocol logging on server side")
        return True
    else:
        print("\n❌ Test failed!")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)