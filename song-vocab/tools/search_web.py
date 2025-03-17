from typing import List, Dict, Any
import requests
import urllib.parse
from bs4 import BeautifulSoup

def search_web(query: str, num_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search the web using DuckDuckGo's API directly.
    
    Parameters:
        query (str): The search query
        num_results (int, optional): Maximum number of results to return (default: 5)
        
    Returns:
        List[Dict[str, Any]]: A list of search results with title, href, and body fields
    """
    try:
        print(f"Searching for: {query}")
        
        # Encode the query for URL
        encoded_query = urllib.parse.quote(query)
        
        # DuckDuckGo API endpoint
        url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json"
        
        # Set headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
        }
        
        print(f"Making request to: {url}")
        response = requests.get(url, headers=headers)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract results
            results = []
            
            # Add abstract if available
            if data.get('Abstract'):
                results.append({
                    "title": data.get('Heading', query),
                    "href": data.get('AbstractURL', ''),
                    "body": data.get('Abstract', '')
                })
            
            # Add related topics
            for topic in data.get('RelatedTopics', [])[:num_results-len(results)]:
                if isinstance(topic, dict) and 'Text' in topic and 'FirstURL' in topic:
                    results.append({
                        "title": topic.get('Text', '').split(' - ')[0],
                        "href": topic.get('FirstURL', ''),
                        "body": topic.get('Text', '')
                    })
                elif isinstance(topic, dict) and 'Topics' in topic:
                    # Handle nested topics
                    for subtopic in topic['Topics'][:num_results-len(results)]:
                        if 'Text' in subtopic and 'FirstURL' in subtopic:
                            results.append({
                                "title": subtopic.get('Text', '').split(' - ')[0],
                                "href": subtopic.get('FirstURL', ''),
                                "body": subtopic.get('Text', '')
                            })
            
            print(f"Found {len(results)} results")
            
            # If we found results, return them
            if results:
                return results
                
            # If no results, make a second request to a search API that might have better results
            # Based on documentation at https://www.searchapi.io/docs/duckduckgo-api
            url = "https://html.duckduckgo.com/html/"
            params = {
                "q": query
            }
            
            print(f"No results from API, trying HTML endpoint")
            response = requests.post(url, data=params, headers=headers)
            
            # Parse the HTML response to extract search results
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            for result in soup.select('.result'):
                title_elem = result.select_one('.result__title')
                link_elem = result.select_one('.result__url')
                snippet_elem = result.select_one('.result__snippet')
                
                if title_elem and link_elem:
                    title = title_elem.text.strip()
                    href = link_elem.get('href', '')
                    body = snippet_elem.text.strip() if snippet_elem else ""
                    
                    results.append({
                        "title": title,
                        "href": href,
                        "body": body
                    })
            
            print(f"Found {len(results)} results from HTML endpoint")
            return results[:num_results]
        
        return []
        
    except Exception as e:
        print(f"Search error: {str(e)}")
        # Error report as a result
        return [{
            "title": "Search Error",
            "href": "",
            "body": f"Error searching for {query}: {str(e)}"
        }]
