import os
import requests
from fastmcp import FastMCP
from tavily import TavilyClient

mcp = FastMCP("ObsedianSocialManager")


@mcp.tool()
def create_post(text: str) -> dict:
    """Publish a text post to LinkedIn."""
    access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
    if not access_token:
        return {"error": "LINKEDIN_ACCESS_TOKEN not set"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }
    me = requests.get("https://api.linkedin.com/v2/me", headers=headers, timeout=10)
    if me.status_code != 200:
        return {"error": "Cannot resolve profile"}
    author = f"urn:li:person:{me.json().get('id', '')}"
    payload = {
        "author": author,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }
    r = requests.post(
        "https://api.linkedin.com/v2/ugcPosts",
        headers=headers,
        json=payload,
        timeout=15,
    )
    if r.status_code in (200, 201):
        return {"status": "success", "preview": text[:200]}
    return {"status": "error", "detail": r.text[:300]}


@mcp.tool()
def generate_posts(num: int = 3) -> list:
    """Generate branded OBSEDIAN posts using Tavily news search."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return [{"error": "TAVILY_API_KEY not set"}]
    tavily = TavilyClient(api_key=api_key)
    topics = [
        "CGI 3D marketing trends",
        "XR business India",
        "growth marketing SMEs 2025",
    ][:num]
    posts = []
    for t in topics:
        try:
            r = tavily.search(
                query=t,
                search_depth="basic",
                include_answer=True,
                max_results=2,
            )
            insight = r.get("answer", "")[:300]
            posts.append({
                "topic": t,
                "text": (
                    f"OBSEDIAN: {t.title()}\n\n"
                    f"{insight}\n\n"
                    f"https://obsedian.in\n"
                    f"#OBSEDIAN #DigitalStudio"
                ),
                "status": "draft",
            })
        except Exception as e:
            posts.append({"topic": t, "error": str(e)})
    return posts


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8001"))
    mcp.run(transport="sse", host="0.0.0.0", port=port)
