import os
import requests
from fastmcp import FastMCP
from tavily import TavilyClient

mcp = FastMCP("ObsedianSocialManager")


@mcp.tool()
def create_post(text: str) -> dict:
    """Publish a text post to LinkedIn on behalf of the personal profile."""
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
        return {"error": f"Cannot resolve LinkedIn profile: {me.text[:200]}"}
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
    return {"status": "error", "code": r.status_code, "detail": r.text[:300]}


@mcp.tool()
def generate_posts(num: int = 3) -> list:
    """Generate branded OBSEDIAN posts using Tavily news search."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return [{"error": "TAVILY_API_KEY not set"}]
    tavily = TavilyClient(api_key=api_key)
    topics = [
        "CGI 3D marketing trends 2025",
        "XR augmented reality business India",
        "growth marketing digital studio",
        "AI visual content creation",
        "immersive brand experiences",
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
                    f"ðŸš€ OBSEDIAN | {t.title()}\n\n"
                    f"{insight}\n\n"
                    f"We're India's boldest digital studio â€” CGI, XR & Growth Marketing.\n"
                    f"ðŸŒ https://obsedian.in\n"
                    f"#OBSEDIAN #DigitalStudio #CGI #XR #GrowthMarketing"
                ),
                "status": "draft",
            })
        except Exception as e:
            posts.append({"topic": t, "error": str(e)})
    return posts


@mcp.tool()
def create_company_page_post(text: str, org_urn: str) -> dict:
    """Publish a post on behalf of an OBSEDIAN LinkedIn Company Page."""
    access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
    if not access_token:
        return {"error": "LINKEDIN_ACCESS_TOKEN not set"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }
    payload = {
        "author": org_urn,
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
    return {"status": "error", "code": r.status_code, "detail": r.text[:300]}


if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))
    mcp.run(transport="sse", host="0.0.0.0", port=port)
