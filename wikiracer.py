import requests
import time
import re
import random

base_url = "https://en.wikipedia.org"
main_page = "https://en.wikipedia.org/wiki/Main_Page"

class Node:
    """
    Class to store information about article and which articles it links to/from
    """
    def __init__(self, val, neighbors=[]):
        self.val = val
        self.neighbors = neighbors
        self.parent = None

def print_path(node, connecting_node=None):
    """
    Function that prints path from start url to end url

    Inputs:
    - Node: Object
    - Connecting_node: If we went 2 layers deep in the right tree, we need to have a connecting node that's in the 1st layer

    Output:
    Prints information about path and saves path to .txt file
    """
    path = [end_node.val]
    # Check if we went 2 layers deep on right tree
    if went_a_little_deeper:
        path.append(connecting_node.val)
    # Appends node url and node parent url and so on
    path.append(node.val)
    while node.parent is not None:
        path.append(node.parent.val)
        node = node.parent
    # Reverse path list
    path.reverse()
    end_time = time.perf_counter()
    print("\n")
    print(f"Found path in {end_time-start_time:.5f} seconds!")
    print(f"Path from article {start_url} to {end_url} has {len(path)-1} degrees of separation.\n")
    print(path)
    exit()
    
def find_urls(html_string, base_url):
	"""
	Function that takes a html-string as input and returns a list of all
	urls found in the text
	"""
	search_term = r"<a[^>]+href=[\"']?([^\"' #>;]+)"
	"""
	Explanation of search term:

	The regex finds all strings in html-document that starts with the html-tag
	<a, has a link (refered to by href)
	- "<a[^>]+" matches strings starting with <a not followed by >.
	- "href=[\"' matches on href= possibly folloed by a " or '
	- [^\"' >#] matches on any characters that arent ", ', (whitespace), #
	Only the part inside the parentheses is returned. If a link starts with #,
	nothing is returned. If a link has # somewhere in it, only the part before
	# is returned
	"""
	# Find all links in html-string
	urls = re.findall(search_term, html_string)
	# Add https: or base_url to start of link if link starts with / or //
	for i, url in enumerate(urls):
		if url[0:2] == "//":
			urls[i] = "https:" + url
		elif url[0] == "/":
			urls[i] = base_url + url

	return urls

def find_articles(html_string, base_url, en_only=False):
	"""
	Function that takes a html-string as input, finds all urls in the text,
	and returns of all urls that points to a wikipedia article
	"""
	# Find all urls from html-string
	urls = find_urls(html_string, base_url)
	if en_only:
		search_term = re.compile(r"^(https:\/\/en.wikipedia.org/wiki/)[^:;]+$")
	else:
		search_term = re.compile(r"^(https:\/\/[\w-].+wikipedia.org/wiki/)[^:;]+$")
	"""
	Explanation of search term:

	The regex finds all strings in the html-string that starts with 
	"https://" + language. + "wikipedia.org", that doesn't contain the symbols
	":" or ";" afterwards. 
	"""

	# Find all articles from list of urls
	articles = list(filter(search_term.match, urls))

	return articles

def filter_articles(parent_node, articles):
    """
    Function that filters articles and checks if any articles are part of path from start url to end url

    Inputs:
    - parent_node: Object
    - articles: list of articles either linking to or from the parent_node.val article.

    Output:
    List of nodes, representing the neighbor/children nodes of parent node
    """

    # List to store nodes
    res = []
    print(f"Filtering articles found on {parent_node.val}")
    
    # Check if we went 1 or 2 layers deep in right tree, and check for any common articles
    if went_a_little_deeper:
        any_common_articles = list(set(articles).intersection(articles_linking_to_articles_linking_to_end_node))
    else:
        any_common_articles = list(set(articles).intersection(articles_linking_to_end_node))

    # If any common article was found between articles and 1st or 2nd layer articles, we should stop looking for a path
    if any_common_articles:
        if went_a_little_deeper:
            # If we're in layer 2
            for child in end_node.neighbors:
                # Find the node(s) with an url in the any_common_articles list
                connecting_list = list(set(any_common_articles).intersection([node.val for node in child.neighbors]))
                if len(connecting_list) >= 1:
                    article = random.choice(any_common_articles)
                    # Make node
                    node = Node(article)
                    # Set node parent
                    node.parent = parent_node
                    # Print path between left and right tree
                    print_path(node, connecting_node=child)
        else:
            # If we're in layer 1
            article = random.choice(any_common_articles)
            # Make node
            node = Node(article)
            # Set node parent
            node.parent = parent_node
            # Print path between left and right tree
            print_path(node)       
    for article in articles:
        # Filter out duplicate articles, and make sure that the article starts with https://en.wikipedia.org/wiki/
        if not article in res and not article in already_checked and article.startswith("https://en.wikipedia.org/wiki/"):
            # Make node
            node = Node(article)
            # Add article to list of already checked articles
            already_checked.append(article)
            # Set node parent
            node.parent = parent_node
            # Add node to list
            res.append(node)
    print(f"Checked {len(already_checked)} of articles in total")
    return res

def links_to(node):
    """
    Function that finds all article links on a wikipedia article

    Input:
    - Node: Object

    Returns:
    List of nodes representing neighbor/children of input node
    """
    S = requests.Session()
    # Get url from node
    url = node.val
    print(f"Fetching articles from {url}")
    # Make request
    R = S.get(url=url)
    # Find articles in html document
    articles = find_articles(R.text, base_url=base_url, en_only=True)
    # Check if end_url is in articles (special case handling for 1 degree of separation, for some reason)
    if end_url in articles:
        print_path(start_node)
    # Filter articles
    filtered = filter_articles(node, articles)
    return filtered

def links_from(node, check_empty=False):
    """
    Function that finds all articles links that link to a specific wikipedia article.

    Has special handling in case no articles are linking to an article.

    Inputs:
    - node: Object
    - check_empty: In rare cases, the end article has no other articles linking to it. This needs special handling

    Returns:
    List of articles linking to node.val
    """
    S = requests.Session()
    # Wikipedia api url
    api_url = "https://en.wikipedia.org/w/api.php"

    # Extract article title from url
    title = node.val.split("/wiki/")[1]

    PARAMS = {
        "action": "query",
        "titles": title,
        "prop": "linkshere", 
        "format": "json",
        "lhlimit": "max"
    }
    print(f"Fetching links from {node.val}")
    # Converting response to json (dict)
    R = S.get(url=api_url, params=PARAMS).json()
    # Find pageid of article
    num = list(R["query"]["pages"].keys())[0]

    def keep_going(response):
        """
        Sometimes more than 500 articles are linking to an article.
        This function handles those instances
        """
        # Find new lhcontinue ID
        lhcontinue = response["continue"]["lhcontinue"]
        # Set lhcontinue params for next request
        PARAMS["lhcontinue"] = lhcontinue
        # Get up to 500 more results
        more = S.get(url=api_url, params=PARAMS).json()
        # Append articles to list of articles linking to article
        for item in more["query"]["pages"][num]["linkshere"]:
            R["query"]["pages"][num]["linkshere"].append(item)
        # Repeat recursively until no lhcontinue ID is found
        if "continue" in more.keys():
            keep_going(more)
    
    # Handling if more than 500 articles linking to article
    if "continue" in R.keys():
        keep_going(R)

    # Empty list for storing article urls
    pages = []
    # List of symbols we don't want in our links
    bad_symbols = ["#", ":"]

    # Check if any article links here
    try:
        # Get title of articles linking to node
        for _dict in R["query"]["pages"][num]["linkshere"]:
            # Replace whitespace with underscore, so we can use title in a link
            title = re.sub(r"\s", r"_", _dict["title"])
            # Remove articles containing # and :
            if list(set(bad_symbols).intersection(title)):
                continue
            # Create link from title
            title = "https://en.wikipedia.org/wiki/" + title
            # Check if title is already checked
            if title in already_checked:
                continue


            pages.append(title)
        # Filter articles and convert them to nodes
        filtered = filter_articles(node, pages)
        return filtered
    except KeyError:
        # If no article links to end_url
        if check_empty:
            if not pages:
                print(f"No articles linking to {end_url}. Exiting..")
                exit()
        # If no article links here, return empty list
        return []

def level1(node):
    """
    Function that takes an article (represented as a node) and returns all links from that article
    """
    links = links_to(node)
    return links

def go_further(neighbor_list):
    """
    Function that generates an additional layer of nodes in a tree structure,
    which is used to find the path.

    This function is called recursively until a path is found.
    """
    links = []
    for neighbor in neighbor_list:
        more_links = level1(neighbor)
        links += more_links
    go_further(links)

if __name__ == "__main__":
    # Get start and end url based on user input
    print("Would you like to")
    print("(1) Run the links from the assignment, or")
    print("(2) Supply your own links?")
    answer = input("Please select 1 or 2: ")
    if answer == "1":
        start_url = "https://en.wikipedia.org/wiki/Nobel_Prize"
        end_url = "https://en.wikipedia.org/wiki/Array_data_structure"
    elif answer == "2":
        start_url = input("Start article: ")
        end_url = input("End article: ")
    else:
        print("Not a valid response. Exiting..")
        exit()
    # Include or exclude main page based on user input
    print("Include wikipedia main page as part of path?")
    include_main = input("y/n: ")
    if include_main.lower() == "y":
        already_checked = [main_page]
    elif include_main.lower() == "n":
        already_checked = []
    else:
        print("Not a valid response. Exiting..")
        exit()
    # Handling if start and end url are the same
    if start_url == end_url:
        print("Start and end url is the same, and has 0 degrees of separation")
        exit()
    # Start timer
    start_time = time.perf_counter()
    # Create start node from start url, representing left tree root node
    start_node = Node(start_url)
    # Create end node from end url, representing right tree root node
    end_node = Node(end_url)
    # Add start url to list of already checked links
    already_checked.append(start_url)
    # Boolean representing if we're in first (False) layer or second (True) layer on right tree
    went_a_little_deeper = False
    # List that will hold articles linking to end node
    articles_linking_to_end_node = []
    # Setting end node neighbors
    end_node.neighbors = links_from(end_node, check_empty=True)
    # List of articles linking to end node
    articles_linking_to_end_node = [node.val for node in end_node.neighbors]
    # In certain cases there are "few" articles linking to the end url. 
    # In that case, we want to generate a second layer of nodes in the right tree, to speed up the pathfinding process
    if len(articles_linking_to_end_node) < 500:
        # Changing variable since we are now in 2nd layer
        went_a_little_deeper = True
        # List of articles in 2nd layer
        articles_linking_to_articles_linking_to_end_node = []
        # Looping over all children of end node, finding articles linking to each child
        for node in end_node.neighbors:
            node.neighbors = links_from(node)
            # Add articles to list of articles in 2nd layer
            articles_linking_to_articles_linking_to_end_node += [neighbor.val for neighbor in node.neighbors]

    # Find links in first layer of left tree
    links = level1(start_node)
    # Find links in deeper levels of left tree until a path is found.
    # Not called if path was found from first layer.
    go_further(links)
