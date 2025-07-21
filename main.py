import os
import re
import sys
import requests

LINEAR_API_KEY = os.getenv("LINEAR_API_KEY")
LINEAR_LABEL = os.getenv("LINEAR_LABEL")
BRANCH_NAME = os.getenv("BRANCH_NAME")
PR_TITLE = os.getenv("PR_TITLE")
LINEAR_API_URL = f"https://api.linear.app/graphql"
headers = {
    "Authorization": LINEAR_API_KEY,
    "Content-Type": "application/json"
}

"""
1. check if linear id is valid.
2. graph ql se add label to the linear
"""
def extract_linear_id(pr_title):
    """Extract Linear issue ID from the PR title (e.g., 'Fix bug ABC-123')"""
    match = re.search(r"[A-Z]+-\d+", pr_title)
    return match.group(0) if match else None

def is_valid_issue(issue_id, headers):
    query = f"""
    query {{
        issue(id: "{issue_id}") {{
            id
            title
        }}
    }}
    """
    response = requests.post(LINEAR_API_URL, json={"query": query}, headers=headers)
    response.raise_for_status()
    data = response.json()
    issue = data.get("data", {}).get("issue")
    if issue:
        print(f"✅ Valid issue found: {issue['title']}")
        return issue["id"]  # Return internal UUID
    return None


def run_query(query, headers):
    try:
        response = requests.post(LINEAR_API_URL, json={"query": query}, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Network or HTTP error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

def get_label_id(label_name, headers):
    labels = []
    has_next_page = True
    after_cursor = None

    while has_next_page:
        after_clause = f', after: "{after_cursor}"' if after_cursor else ""
        query = f"""
        query {{
            issueLabels(first: 50{after_clause}) {{
                nodes {{
                    id
                    name
                }}
                pageInfo {{
                    hasNextPage
                    endCursor
                }}
            }}
        }}
        """
        result = run_query(query, headers)
        data = result.get("data", {}).get("issueLabels", {})
        nodes = data.get("nodes", [])
        labels.extend(nodes)

        # Update pagination info
        page_info = data.get("pageInfo", {})
        has_next_page = page_info.get("hasNextPage", False)
        after_cursor = page_info.get("endCursor")

    # Search for label
    for label in labels:
        if label["name"].lower() == label_name.lower():
            return label["id"]

    return None


def add_label_to_issue(issue_id, label_id, headers):
    query = """
    mutation IssueAddLabel($id: String!, $labelId: String!) {
      issueAddLabel(id: $id, labelId: $labelId) {
        success
      }
    }
    """
    variables = {
        "id": issue_id,
        "labelId": label_id
    }
    try:
        response = requests.post(LINEAR_API_URL, json={"query": query, "variables": variables}, headers=headers)
        response.raise_for_status()
        result = response.json()
        return result.get("data", {}).get("issueAddLabel", {}).get("success", False)
    except requests.exceptions.RequestException as e:
        print(f"❌ Network or HTTP error: {e}")
        print(f"🔍 Response: {e.response.text if hasattr(e, 'response') else ''}")
        sys.exit(1)

def main():
    try:
        print(f"🔍 Branch name: {BRANCH_NAME}")
        print(f"🔍 Extracting Linear ID from PR title: {PR_TITLE}")
        print(f"Linear label: {LINEAR_LABEL}")

        # Check if branch starts with 'codex/'
        if not BRANCH_NAME or not BRANCH_NAME.startswith(("codex/", "cursor/")):
            print("ℹ️ Branch name does not start with 'codex/' or 'cursor/'. Skipping label addition.")
            return

        LINEAR_ID = extract_linear_id(PR_TITLE)
        if not LINEAR_API_KEY or not LINEAR_ID:
            print("❌ Missing required input(s).")
            sys.exit(1)

        headers = {
            "Authorization": LINEAR_API_KEY,
            "Content-Type": "application/json"
        }

        # Validate issue
        issue_uuid = is_valid_issue(LINEAR_ID, headers)
        if not issue_uuid:
            print(f"❌ Invalid Linear issue ID: {LINEAR_ID}")
            sys.exit(1)

        if LINEAR_LABEL == 'codex':
            label = "Executed by Codex"
        label_id = get_label_id(label, headers)
        print(label_id)
        if not label_id:
            print(f"❌ Label '{label}' not found.")
            sys.exit(1)

        print(f"🧾 Label ID: {label_id}")
        print(f"🧾 Issue UUID: {issue_uuid}")

        success = add_label_to_issue(issue_uuid, label_id, headers)
        if success:
            print(f"✅ Label '{label}' added to issue {LINEAR_ID}")
        else:
            print("❌ Failed to add label to the issue.")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
