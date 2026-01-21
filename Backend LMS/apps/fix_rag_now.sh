#!/bin/bash
# ============================================
# ONE-COMMAND FIX SCRIPT
# Run this: bash fix_rag_now.sh
# ============================================

echo "=================================="
echo "FIXING YOUR RAG SYSTEM NOW"
echo "=================================="

# Step 1: Backup current files
echo ""
echo "Step 1: Backing up current files..."
cp apps/rag_system/services/database_connector.py apps/rag_system/services/database_connector.py.backup 2>/dev/null || true
cp apps/rag_system/services/groq_service.py apps/rag_system/services/groq_service.py.backup 2>/dev/null || true
echo "✅ Backup complete"

# Step 2: Replace files
echo ""
echo "Step 2: Replacing with fixed files..."
cp database_connector_FINAL.py apps/rag_system/services/database_connector.py
cp groq_service_ULTRAFIX.py apps/rag_system/services/groq_service.py
echo "✅ Files replaced"

# Step 3: Initialize vector store
echo ""
echo "Step 3: Initializing vector store (this takes 1-2 minutes)..."
python manage.py initialize_rag_vectorstore --refresh --test

# Step 4: Test
echo ""
echo "Step 4: Testing with route query..."
echo ""
curl -X POST http://localhost:8000/api/rag/chat/query/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "what are the routes", "use_cache": false}' \
  2>/dev/null | python -m json.tool

echo ""
echo "=================================="
echo "✅ FIX COMPLETE!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Check the response above"
echo "2. It should show route details (not placeholders)"
echo "3. Test more queries via API"
echo ""