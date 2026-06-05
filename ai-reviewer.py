# ai_reviewer.py- agentic AI code review Bot 
# reads MR diff - sends to Claude -> posts inline comments on GitLab

import os, json, gitlab, antropic 
from antropic import Anthropic

client=  Anthropic()
gl= gitlab.Gitlab("https://gitlab.com",
 private_token=os.environ["GITLAB_API_TOKEN"]
 )

def get_mr_diff():
    """
    fetch the diff of the current merge requets
    """
    project= gl.projects.get(os.environ["CI_PROJECT_ID"])
    mr_iid= os.environ["CI_MERGE_REQUEST_IID"]
    mr= project.mergerequets.get(mr_iid)
    changes= mr.changes()
    diffs= [ ]
    for change in chnages [ "chnages"]:
        if change["new_path"].endswith(".py"):
            diffs.append({
                "file": change["new_path"],
                "diff" :change["diff"][:3000]
            })
    return mr, diffs

def review_code_with_ai(file_path, diff_content):
    """Ask Claude to review the code diff — Agentic AI with tools"""
    tools = [{
        "name": "submit_review",
        "description": "Submit a structured code review",
        "input_schema": {
            "type": "object",
            "properties": {
                "severity": {"type": "string",
                    "enum": ["critical", "warning", "info"]},
                "issues": {"type": "array", "items": {
                    "type": "object",
                    "properties": {
                        "line": {"type": "integer"},
                        "issue": {"type": "string"},
                        "suggestion": {"type": "string"}
                    }
                }},
                "summary": {"type": "string"}
            }
        }
    }]

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        tools=tools,
        messages=[{
            "role": "user",
            "content": f"""Review this Python diff for file '{file_path}'.
Check for: bugs, security issues, performance problems,
missing error handling, code style issues.

Diff:
{diff_content}

Use the submit_review tool to return structured feedback."""
        }]
    )

    for block in response.content:
        if block.type == "tool_use":
            return block.input
    return None

def post_comment_to_mr(mr, review, file_path):
    """Post the AI review as a comment on the Merge Request"""
    emoji = {"critical": "🔴", "warning": "🟡", "info": "🔵"}
    sev = review.get("severity", "info")

    comment = f"""## {emoji[sev]} AI Code Review — `{file_path}`

**Summary:** {review['summary']}

### Issues Found:
"""
    for issue in review.get("issues", []):
        comment += f"""
**Line {issue['line']}:** {issue['issue']}
> 💡 Suggestion: {issue['suggestion']}
---"""

    mr.notes.create({"body": comment})
    print(f"✅ Posted review for {file_path}")

if __name__ == "__main__":
    mr, diffs = get_mr_diff()
    if not diffs:
        print("No Python files changed. Skipping AI review.")
        exit(0)
    for item in diffs:
        review = review_code_with_ai(item["file"], item["diff"])
        if review:
            post_comment_to_mr(mr, review, item["file"])