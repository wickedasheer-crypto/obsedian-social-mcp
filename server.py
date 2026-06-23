import os
import json
import requests
from datetime import datetime
from fastmcp import FastMCP
from tavily import TavilyClient

mcp = FastMCP("ObsedianSocialManager")

COMPANY_PROFILE = {
    "name": "OBSEDIAN",
    "website": "https://obsedian.in",
    "tagline": "India's Boldest Digital Studio",
    "description": "OBSEDIAN is India's boldest digital studio specialising in CGI, XR, Sales Pipeline Automation, and Growth Marketing for Indian SMEs.",
    "industry": "Technology",
}

def get_tavily_client():
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY environment variable not set")
    return TavilyClient(api_key=api_key)

@mcp.tool()
def search_internet(query: str) -> str:
    """Search the internet for a given query and return a detailed markdown summary."""
    try:
        client = get_tavily_client()
        result = client.search(query=query, max_results=5)
        
        # Format the search results nicely
        formatted_results = []
        for i, res in enumerate(result.get("results", []), 1):
            title = res.get("title", "No Title")
            url = res.get("url", "#")
            content = res.get("content", "")
            formatted_results.append(f"### {i}. [{title}]({url})\n\n{content}\n")
        
        return "\n".join(formatted_results) if formatted_results else "No results found."
    except Exception as e:
        return f"Error searching the internet: {str(e)}"

@mcp.tool()
def generate_trending_topics(num_posts: int = 5) -> list[str]:
    """Generate trending topics for OBSEDIAN based on its profile."""
    topics = [
        "CGI 3D visualization marketing trends",
        "extended reality XR business India",
        "sales pipeline automation SMEs",
        "growth marketing Indian startups 2025",
        "AI digital marketing branding"
    ][:num_posts]
    return topics

@mcp.tool()
def draft_social_media_post(topic: str, platform: str) -> str:
    """Draft a social media post on a given topic for a specific platform."""
    now = datetime.now().strftime("%B %d, %Y")
    
    prompt = f"Write a professional social media post for {platform}.\nTopic: {topic}\nDate: {now}\nUse the company profile of {COMPANY_PROFILE['name']}: {COMPANY_PROFILE['description']}. Tone: Bold, innovative, energetic."
    
    # Simulating simple rule-based drafts for demo purposes since we don't have LLM API here.
    if platform.lower() == "linkedin":
        draft = f"Let's talk about {topic}! OBSEDIAN ({COMPANY_PROFILE['website']}) is leading the wave in this space. As {COMPANY_PROFILE['tagline']}, we believe in pushing boundaries. {COMPANY_PROFILE['description']}\n\n#GrowthMarketing #CGI #SME #Automation"
    elif platform.lower() == "twitter" or platform.lower() == "x":
        draft = f"Topic: {topic} is shaping 2025. OBSEDIAN is here for it: {COMPANY_PROFILE['description'][:100]}... {COMPANY_PROFILE['website']} #Bold"
    else:
        draft = f"Draft for {platform} on {topic}: Innovation at OBSEDIAN."
        
    return draft
