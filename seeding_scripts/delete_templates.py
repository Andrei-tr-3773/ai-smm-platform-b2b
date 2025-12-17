#!/usr/bin/env python3
"""
Delete Templates Script

Deletes specified templates from MongoDB content_templates collection.
Useful for removing AI-generated templates with old format (items.field_name).
"""
from dotenv import load_dotenv
from utils.mongodb_utils import MongoDBClient

# Load environment
load_dotenv(override=True)

# ============================================================================
# CONFIGURE: Add template names you want to delete here
# ============================================================================
TEMPLATES_TO_DELETE = [
    "fitness_class",
    "miami_template",
    "hot_dog_template",
]
# ============================================================================


def delete_templates(template_names):
    """
    Delete templates from MongoDB by name.

    Args:
        template_names: List of template names to delete
    """
    print("🗑️  Template Deletion Script")
    print("=" * 80)

    # Connect to MongoDB
    client = MongoDBClient("content_templates")

    print(f"\n📋 Templates to delete: {len(template_names)}")
    for name in template_names:
        print(f"   - {name}")

    # Confirm deletion
    print(f"\n⚠️  WARNING: This will permanently delete {len(template_names)} templates!")
    confirmation = input("Type 'DELETE' to confirm: ")

    if confirmation != "DELETE":
        print("❌ Deletion cancelled.")
        return

    # Delete templates
    print(f"\n🗑️  Deleting templates...")
    deleted_count = 0
    not_found = []

    for name in template_names:
        result = client.collection.delete_one({"name": name})

        if result.deleted_count > 0:
            print(f"   ✅ Deleted: {name}")
            deleted_count += 1
        else:
            print(f"   ⚠️  Not found: {name}")
            not_found.append(name)

    # Summary
    print("\n" + "=" * 80)
    print(f"✅ Deleted: {deleted_count} templates")

    if not_found:
        print(f"⚠️  Not found: {len(not_found)} templates")
        for name in not_found:
            print(f"   - {name}")

    print("\n💡 Tip: You can now recreate these templates with AI Template Generator")
    print("   (they will use the correct format without 'items.' prefix)")


def list_all_templates():
    """List all templates in database (for reference)."""
    print("\n📚 All Templates in Database:")
    print("=" * 80)

    client = MongoDBClient("content_templates")
    templates = client.get_templates()

    if not templates:
        print("   (No templates found)")
        return

    for i, template in enumerate(templates, 1):
        name = template.get('name', 'Unknown')
        is_ai = template.get('metadata', {}).get('is_ai_generated', False)
        created = template.get('created_at', 'Unknown')

        ai_badge = "🤖 AI" if is_ai else "📝 Manual"
        print(f"{i:2}. {ai_badge} {name}")
        print(f"    Created: {created}")

    print(f"\n📊 Total: {len(templates)} templates")


if __name__ == "__main__":
    # Show all templates first (for reference)
    list_all_templates()

    print("\n")

    # Delete specified templates
    if TEMPLATES_TO_DELETE:
        delete_templates(TEMPLATES_TO_DELETE)
    else:
        print("⚠️  No templates specified for deletion.")
        print("   Edit TEMPLATES_TO_DELETE list in this script.")
