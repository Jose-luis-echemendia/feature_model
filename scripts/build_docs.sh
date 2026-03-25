#!/bin/bash

set -e  # Salir si hay errores

echo "========================================="
echo "📚 Building documentation"
echo "========================================="
echo "📅 Date: $(date)"
echo ""

echo "📋 Step 1/2: Synchronizing markdown files..."
python app/sync_docs.py
if [ $? -eq 0 ]; then
    echo "✅ Markdown files synchronized"
else
    echo "❌ Synchronization failed"
    exit 1
fi
echo ""

echo "🔨 Step 2/2: Building site with Zensical..."
cd internal_docs
zensical build --clean
if [ $? -eq 0 ]; then
    echo "✅ Zensical site built successfully"
    cd ..
else
    echo "❌ MkDocs build failed"
    cd ..
    exit 1
fi
echo ""

echo "========================================="
echo "✅ Documentation compiled and ready"
echo "📂 Site location: internal_docs/site/"
echo "========================================="
