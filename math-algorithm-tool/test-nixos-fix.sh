#!/usr/bin/env bash
# Test script to verify the NixOS Tauri Bus Error fix

set -e

echo "=== NixOS Tauri Fix Verification Script ==="
echo

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to check test result
check_test() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $1"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} $1"
        ((TESTS_FAILED++))
    fi
}

# Function to warn about potential issues
warn_test() {
    echo -e "${YELLOW}⚠${NC} $1"
}

echo "Step 1: Checking for required packages..."
echo

# Check if we're in a nix environment
if [ -z "$IN_NIX_SHELL" ]; then
    warn_test "Not running in nix-shell. Some checks may fail."
else
    check_test "Running in nix-shell" "Nix environment detected"
fi
# Check if required packages are available
for pkg in webkitgtk_4_1 gtk3 gsettings-desktop-schemas hicolor-icon-theme; do
    if nix-shell -p $pkg --run "true" 2>/dev/null; then
        check_test "Package $pkg is available"
    else
        echo "Package $pkg is not available"
        ((TESTS_FAILED++))
    fi
done

echo
echo "Step 2: Checking environment variables..."
echo

# Check if XDG_DATA_DIRS is set
if [ -n "$XDG_DATA_DIRS" ]; then
    check_test "XDG_DATA_DIRS is set"
    
    # Check if it contains required paths
    if echo "$XDG_DATA_DIRS" | grep -q "gsettings-desktop-schemas"; then
        check_test "XDG_DATA_DIRS contains gsettings-desktop-schemas"
    else
        warn_test "XDG_DATA_DIRS does not contain gsettings-desktop-schemas"
        ((TESTS_FAILED++))
    fi
    
    if echo "$XDG_DATA_DIRS" | grep -q "gtk3"; then
        check_test "XDG_DATA_DIRS contains gtk3 schemas"
    else
        warn_test "XDG_DATA_DIRS does not contain gtk3 schemas"
        ((TESTS_FAILED++))
    fi
else
    warn_test "XDG_DATA_DIRS is NOT set (CRITICAL!)"
    ((TESTS_FAILED++))
fi

# Check if LD_LIBRARY_PATH is set
if [ -n "$LD_LIBRARY_PATH" ]; then
    check_test "LD_LIBRARY_PATH is set"
    
    # Check if it contains required libraries
    if echo "$LD_LIBRARY_PATH" | grep -q "gtk3"; then
        check_test "LD_LIBRARY_PATH contains gtk3"
    else
        warn_test "LD_LIBRARY_PATH does not contain gtk3"
        ((TESTS_FAILED++))
    fi
    
    if echo "$LD_LIBRARY_PATH" | grep -q "webkitgtk"; then
        check_test "LD_LIBRARY_PATH contains webkitgtk"
    else
        warn_test "LD_LIBRARY_PATH does not contain webkitgtk"
        ((TESTS_FAILED++))
    fi
else
    warn_test "LD_LIBRARY_PATH is NOT set (CRITICAL!)"
    ((TESTS_FAILED++))
fi

# Check if GTK_THEME is set
if [ -n "$GTK_THEME" ]; then
    check_test "GTK_THEME is set to $GTK_THEME"
else
    warn_test "GTK_THEME is not set"
fi

echo
echo "Step 3: Testing GTK schema accessibility..."
echo

# Test if GTK can find schemas
if command -v gsettings &>/dev/null; then
    if gsettings list-schemas &>/dev/null; then
        check_test "gsettings can list schemas"
    else
        warn_test "gsettings cannot list schemas"
        ((TESTS_FAILED++))
    fi
else
    warn_test "gsettings command not found"
fi

# Test if GTK theme can be loaded
if command -v gtk-launch &>/dev/null; then
    if gtk-launch --help &>/dev/null; then
        check_test "gtk-launch runs correctly"
    else
        warn_test "gtk-launch has issues (might not find schemas)"
        ((TESTS_FAILED++))
    fi
else
    warn_test "gtk-launch command not found"
fi

echo
echo "Step 4: Testing Tauri build environment..."
echo

# Check if Rust is available
if command -v rustc &>/dev/null; then
    check_test "Rust compiler (rustc) is available"
    
    RUST_VERSION=$(rustc --version)
    echo "  Rust version: $RUST_VERSION"
else
    warn_test "Rust compiler (rustc) not found"
    ((TESTS_FAILED++))
fi

# Check if Cargo is available
if command -v cargo &>/dev/null; then
    check_test "Cargo is available"
else
    warn_test "Cargo not found"
    ((TESTS_FAILED++))
fi

# Check if pkg-config can find gtk3
if command -v pkg-config &>/dev/null; then
    if pkg-config --exists gtk+-3.0; then
        GTK_VERSION=$(pkg-config --modversion gtk+-3.0)
        check_test "pkg-config can find GTK3 (version $GTK_VERSION)"
    else
        warn_test "pkg-config cannot find GTK3"
        ((TESTS_FAILED++))
    fi
    
    if pkg-config --exists webkitgtk-6.0; then
        WEBKIT_VERSION=$(pkg-config --modversion webkitgtk-6.0)
        check_test "pkg-config can find WebKitGTK (version $WEBKIT_VERSION)"
    else
        warn_test "pkg-config cannot find webkitgtk-6.0"
        ((TESTS_FAILED++))
    fi
else
    warn_test "pkg-config not found"
    ((TESTS_FAILED++))
fi

echo
echo "Step 5: Running a quick Tauri frontend check..."
echo

# Check if Node.js is available
if command -v node &>/dev/null; then
    check_test "Node.js is available"
    NODE_VERSION=$(node --version)
    echo "  Node.js version: $NODE_VERSION"
else
    warn_test "Node.js not found"
    ((TESTS_FAILED++))
fi

# Check if npm is available
if command -v npm &>/dev/null; then
    check_test "npm is available"
else
    warn_test "npm not found"
    ((TESTS_FAILED++))
fi

# Check if vite is available
if npx vite --version &>/dev/null 2>&1; then
    check_test "Vite is available"
    VITE_VERSION=$(npx vite --version | head -n1)
    echo "  Vite version: $VITE_VERSION"
else
    warn_test "Vite not available or not found"
    ((TESTS_FAILED++))
fi

echo
echo "Step 6: Testing Nix store paths..."
echo

# Test if we can resolve Nix store paths
for pkg in webkitgtk_4_1 gtk3; do
    PKG_PATH=$(nix-build --no-out-link "<nixpkgs>" -A "$pkg" 2>/dev/null | head -n1 || echo "ERROR")
    if [ "$PKG_PATH" != "ERROR" ]; then
        check_test "Nix store path for $pkg: exists"
    else
        warn_test "Could not resolve Nix store path for $pkg"
        ((TESTS_FAILED++))
    fi
done

echo
echo "=== Test Summary ==="
echo -e "Tests passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests failed: ${RED}$TESTS_FAILED${NC}"
echo

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed! Your NixOS environment is ready for Tauri development.${NC}"
    exit 0
elif [ $TESTS_FAILED -lt 5 ]; then
    echo -e "${YELLOW}✓ Most tests passed. Check warnings above, but you can probably still develop.${NC}"
    exit 0
else
    echo -e "${RED}✗ Multiple tests failed. Please review errors and fix your environment.${NC}"
    exit 1
fi
