#!/bin/bash
# trsh - Initial Project Setup
# Run this script in your empty project directory

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🗑️  trsh - Complete Project Setup${NC}"
echo "================================================"
echo ""

# Step 1: Create project structure
echo -e "${YELLOW}Step 1: Creating project structure...${NC}"
mkdir -p docs
mkdir -p tests
mkdir -p .github/workflows

echo -e "${GREEN}✓${NC} Project structure created"
echo ""

# Step 2: Check conda
echo -e "${YELLOW}Step 2: Checking conda installation...${NC}"
if ! command -v conda &> /dev/null; then
    echo "Error: Conda not found. Please install Miniconda first."
    echo "Visit: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi
echo -e "${GREEN}✓${NC} Conda found: $(conda --version)"
echo ""

# Step 3: Create conda environment
echo -e "${YELLOW}Step 3: Creating conda environment 'trsh'...${NC}"
if conda env list | grep -q "^trsh "; then
    echo "Environment 'trsh' already exists. Removing..."
    conda env remove -n trsh -y
fi

conda create -n trsh python=3.11 -y
echo -e "${GREEN}✓${NC} Environment created"
echo ""

# Step 4: Activate and install dependencies
echo -e "${YELLOW}Step 4: Installing development dependencies...${NC}"
eval "$(conda shell.bash hook)"
conda activate trsh

conda install -y \
    pytest \
    pytest-cov \
    black \
    pylint \
    mypy

pip install --upgrade pip
pip install rich

echo -e "${GREEN}✓${NC} Dependencies installed"
echo ""

# Step 5: Initialize git
echo -e "${YELLOW}Step 5: Initializing git repository...${NC}"
if [ ! -d .git ]; then
    git init
    git branch -M main
    echo -e "${GREEN}✓${NC} Git repository initialized"
else
    echo "Git repository already exists"
fi
echo ""

# Step 6: Create initial files
echo -e "${YELLOW}Step 6: Creating placeholder files...${NC}"

# Create empty Python file
touch trsh.py

# Create test file
touch test_trsh.py

# Create README
cat > README.md << 'EOF'
# 🗑️ trsh - Delete with Confidence, Restore with Ease

Work in progress...
EOF

echo -e "${GREEN}✓${NC} Initial files created"
echo ""

# Summary
echo "================================================"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo ""
echo "Project structure:"
echo "  trsh/"
echo "  ├── trsh.py           (empty - ready for code)"
echo "  ├── test_trsh.py      (empty - ready for tests)"
echo "  ├── README.md         (placeholder)"
echo "  ├── docs/             (documentation)"
echo "  ├── tests/            (test files)"
echo "  └── .github/          (CI/CD workflows)"
echo ""
echo "Next steps:"
echo "  1. Copy the artifacts I'll provide into the respective files"
echo "  2. Run: conda activate trsh"
echo "  3. Run: python trsh.py --help"
echo "  4. Run: python test_trsh.py"
echo ""
echo "Environment 'trsh' is ready!"
echo "Activate with: ${BLUE}conda activate trsh${NC}"
echo ""