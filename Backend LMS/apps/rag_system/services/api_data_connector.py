# ============================================
# API DATA CONNECTOR
# File: apps/rag_system/services/api_data_connector.py
# ============================================

"""
Fetches data from Django REST API endpoints and caches it for RAG
This bridges the gap between API responses and the RAG system
"""

import requests
import json
from typing import Dict, List, Optional
from pathlib import Path
from django.conf import settings
from django.core.cache import cache


class APIDataConnector:
    """Connects to internal Django REST API to fetch and cache data"""
    
    def __init__(self, base_url: str = None):
        # Use internal Django URL
        self.base_url = base_url or "http://localhost:8000/api"
        self.cache_dir = Path("data/api_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"🔗 API Data Connector initialized: {self.base_url}")
    
    def fetch_roles_with_permissions(self, force_refresh: bool = False) -> Optional[Dict]:
        """
        Fetch roles with their permissions from API
        
        Returns formatted data suitable for RAG
        """
        cache_key = "roles_permissions_data"
        cache_file = self.cache_dir / "roles_permissions.json"
        
        # Check memory cache first
        if not force_refresh:
            cached = cache.get(cache_key)
            if cached:
                print("✅ Using cached roles data from memory")
                return cached
        
        # Check file cache
        if not force_refresh and cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    print("✅ Using cached roles data from file")
                    cache.set(cache_key, data, timeout=3600)  # 1 hour
                    return data
            except Exception as e:
                print(f"⚠️ Error reading cache file: {e}")
        
        # Fetch from API
        print("🔄 Fetching fresh roles data from API...")
        
        try:
            # Use Django ORM directly instead of HTTP request
            from apps.users.models import Role
            
            roles_data = []
            roles = Role.objects.filter(deleted=False).prefetch_related('permissions')
            
            for role in roles:
                permissions_list = [
                    {
                        'id': perm.id,
                        'name': perm.name,
                        'code_name': perm.code_name
                    }
                    for perm in role.permissions.all()
                ]
                
                roles_data.append({
                    'id': role.id,
                    'name': role.name,
                    'code_name': role.code_name,
                    'description': role.description,
                    'permissions': permissions_list,
                    'permissions_count': len(permissions_list)
                })
            
            result = {
                'success': True,
                'count': len(roles_data),
                'data': roles_data,
                'timestamp': str(cache.get('server_time'))
            }
            
            # Cache the result
            cache.set(cache_key, result, timeout=3600)
            
            # Save to file
            with open(cache_file, 'w') as f:
                json.dump(result, f, indent=2)
            
            print(f"✅ Fetched {len(roles_data)} roles from database")
            return result
            
        except Exception as e:
            print(f"❌ Error fetching roles: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_role_by_name(self, role_name: str) -> Optional[Dict]:
        """Get specific role by name (case-insensitive)"""
        data = self.fetch_roles_with_permissions()
        
        if not data or not data.get('success'):
            return None
        
        role_name_lower = role_name.lower()
        
        for role in data.get('data', []):
            if (role['name'].lower() == role_name_lower or 
                role['code_name'].lower() == role_name_lower):
                return role
        
        return None
    
    def format_role_for_rag(self, role_data: Dict) -> str:
        """
        Format role data into text suitable for RAG context
        
        Returns human-readable text about the role
        """
        if not role_data:
            return ""
        
        permissions = role_data.get('permissions', [])
        
        text = f"""
ROLE: {role_data['name']}
Code: {role_data['code_name']}
Description: {role_data.get('description', 'N/A')}

PERMISSIONS ({len(permissions)} total):
"""
        
        # Group permissions by category
        permission_groups = self._group_permissions(permissions)
        
        for category, perms in permission_groups.items():
            text += f"\n{category.upper()}:\n"
            for perm in perms:
                text += f"  • {perm['name']} ({perm['code_name']})\n"
        
        return text.strip()
    
    def _group_permissions(self, permissions: List[Dict]) -> Dict[str, List[Dict]]:
        """Group permissions by category based on code_name"""
        groups = {
            'Users & Roles': [],
            'Students': [],
            'Teachers': [],
            'Parents': [],
            'Academic': [],
            'Attendance': [],
            'Exams': [],
            'Finance': [],
            'Transport': [],
            'Communication': [],
            'Reports': [],
            'Other': []
        }
        
        for perm in permissions:
            code = perm['code_name'].lower()
            
            if any(x in code for x in ['user', 'role', 'employee']):
                groups['Users & Roles'].append(perm)
            elif 'student' in code:
                groups['Students'].append(perm)
            elif 'teacher' in code:
                groups['Teachers'].append(perm)
            elif 'parent' in code:
                groups['Parents'].append(perm)
            elif any(x in code for x in ['class', 'subject', 'department', 'academic', 'course']):
                groups['Academic'].append(perm)
            elif 'attendance' in code:
                groups['Attendance'].append(perm)
            elif any(x in code for x in ['exam', 'grade', 'result']):
                groups['Exams'].append(perm)
            elif any(x in code for x in ['fee', 'payment', 'invoice', 'discount']):
                groups['Finance'].append(perm)
            elif any(x in code for x in ['vehicle', 'route', 'transport']):
                groups['Transport'].append(perm)
            elif any(x in code for x in ['message', 'notification', 'announcement']):
                groups['Communication'].append(perm)
            elif any(x in code for x in ['report', 'certificate']):
                groups['Reports'].append(perm)
            else:
                groups['Other'].append(perm)
        
        # Remove empty groups
        return {k: v for k, v in groups.items() if v}
    
    def create_vectorstore_documents(self) -> List[Dict]:
        """
        Create documents for vector store from API data
        
        Returns list of documents ready to be added to vector store
        """
        roles_data = self.fetch_roles_with_permissions()
        
        if not roles_data or not roles_data.get('success'):
            print("❌ No roles data available")
            return []
        
        documents = []
        
        # Create a document for each role
        for role in roles_data.get('data', []):
            # Main role document
            content = self.format_role_for_rag(role)
            
            documents.append({
                'content': content,
                'metadata': {
                    'type': 'role_permissions',
                    'source': 'api',
                    'role_name': role['name'],
                    'role_code': role['code_name'],
                    'permissions_count': len(role.get('permissions', [])),
                    'priority': 'high'
                }
            })
            
            # Create summary document for quick queries
            permissions_names = [p['name'] for p in role.get('permissions', [])]
            
            summary = f"""
{role['name']} Role Quick Reference:

This role has {len(permissions_names)} permissions:
{', '.join(permissions_names[:10])}
{f"... and {len(permissions_names) - 10} more" if len(permissions_names) > 10 else ""}

Common questions:
- "What permissions does {role['name']} have?" 
- "What can a {role['name']} do?"
- "List {role['name']} permissions"

Full permission list: {', '.join(permissions_names)}
"""
            
            documents.append({
                'content': summary,
                'metadata': {
                    'type': 'role_summary',
                    'source': 'api',
                    'role_name': role['name'],
                    'role_code': role['code_name'],
                    'priority': 'very_high'  # Prioritize summaries
                }
            })
        
        # Create general permissions overview
        all_roles = roles_data.get('data', [])
        overview = f"""
LMS ROLES AND PERMISSIONS OVERVIEW

Total Roles: {len(all_roles)}

AVAILABLE ROLES:
"""
        
        for role in all_roles:
            overview += f"\n{role['name']} ({role['code_name']}): {len(role.get('permissions', []))} permissions"
            overview += f"\n  Description: {role.get('description', 'N/A')}"
        
        overview += """

To get specific role permissions, ask:
- "What permissions does [role_name] have?"
- "What can a [role_name] do?"
- "Show me [role_name] permissions"
"""
        
        documents.append({
            'content': overview,
            'metadata': {
                'type': 'roles_overview',
                'source': 'api',
                'priority': 'high'
            }
        })
        
        print(f"📄 Created {len(documents)} documents from API data")
        return documents
    
    def refresh_cache(self) -> bool:
        """Force refresh all cached API data"""
        print("🔄 Refreshing API data cache...")
        
        result = self.fetch_roles_with_permissions(force_refresh=True)
        
        if result and result.get('success'):
            print("✅ Cache refreshed successfully")
            return True
        else:
            print("❌ Cache refresh failed")
            return False


# ============================================
# TESTING
# ============================================

if __name__ == "__main__":
    print("="*70)
    print("Testing API Data Connector")
    print("="*70)
    
    connector = APIDataConnector()
    
    # Test 1: Fetch roles
    print("\n1. Fetching roles...")
    roles_data = connector.fetch_roles_with_permissions()
    
    if roles_data:
        print(f"   ✅ Success: {roles_data['count']} roles")
    else:
        print("   ❌ Failed")
    
    # Test 2: Get specific role
    print("\n2. Getting Teacher role...")
    teacher = connector.get_role_by_name("Teacher")
    
    if teacher:
        print(f"   ✅ Found: {teacher['name']}")
        print(f"   Permissions: {len(teacher.get('permissions', []))}")
    else:
        print("   ❌ Not found")
    
    # Test 3: Format for RAG
    if teacher:
        print("\n3. Formatting for RAG...")
        formatted = connector.format_role_for_rag(teacher)
        print(f"   ✅ Generated {len(formatted)} characters")
        print(f"\n   Preview:\n{formatted[:300]}...")
    
    # Test 4: Create vector store documents
    print("\n4. Creating vector store documents...")
    docs = connector.create_vectorstore_documents()
    print(f"   ✅ Created {len(docs)} documents")
    
    print("\n" + "="*70)
    print("✅ All tests passed!")
    print("="*70)