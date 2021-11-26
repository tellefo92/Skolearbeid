import asyncio
import re
from aiohttp import ClientSession
import time

class Node:
    def __init__(self, url, parent=None):
        self.url = url
        self.parent = parent

def url_to_api(url):
    title = url.split("/wiki/")[1]
    print(title)
    return title

def print_path(node, connecting_node=None, side="left"):
    _left = []
    _right = []
    if side == "left":
        while node.parent:
            _left.append(node.url)
            node = node.parent
        _left.append(node.url)
        _left.reverse()
        while connecting_node.parent:
            _right.append(connecting_node.parent.url)
            connecting_node = connecting_node.parent
    else:
        while node.parent:
            _right.append(node.url)
            node = node.parent
        _right.append(node.url)
        while connecting_node.parent:
            _left.append(connecting_node.parent.url)
            connecting_node = connecting_node.parent
        _left.reverse()
    print(_left, _right)
    print(f"Path found in {time.perf_counter()-start:.5f} seconds:")
    path = _left + _right
    print(f"Path has {len(path)-1} degrees of separation.")
    print(f"{path[0]} -->")
    for i in range(1, len(path)-1):
        print(f"{path[i]} -->")
    print(path[-1])
    exit()
        


async def fetch_left(node, session):
        async with session.get(node.url) as response:
            html = await response.text()
            articles = set(["https://en.wikipedia.org" + a for a in re.findall(r"<a[^>]+href=[\"']?(/wiki/[^\"' #>;]+)", html) if ":" not in a])
            common = list(articles.intersection(right_layer))
            if common:
                art = Node(common[0])
                art.parent = node
                for _node in right_nodes:
                    if _node.url == common[0]:
                        print("Left side: ", art.url, _node.url)
                        print_path(art, connecting_node=_node)
            else:
                for article in list(articles):
                    if article not in previously_checked:
                        a = Node(article)
                        a.parent = node
                        left_layer.append(article)
                        left_nodes.append(a)
                        previously_checked.append(article)

async def fetch_right(node, session):
        api_url = "https://en.wikipedia.org/w/api.php"

        PARAMS = {
            "action": "query",
            "titles": url_to_api(node.url),
            "prop": "linkshere",
            "format": "json",
            "lhlimit": "500",
            "lhnamespace": "0",
            "lhprop": "title"
        }
        async with session.get(api_url, params=PARAMS) as response:
            resp = await response.json()
            print(resp)
            exit()
            num = list(resp["query"]["pages"].keys())[0]
            
            async def keep_going(r):
                # Find new lhcontinue ID
                lhcontinue = r["continue"]["lhcontinue"]
                # Set lhcontinue params for next request
                PARAMS['lhcontinue'] = lhcontinue
                async with session.get(api_url, params=PARAMS) as resp2:
                    # Get up to 500 more results
                    more = await resp2.json()
                    # Append articles to list of articles linking to article
                    for item in more["query"]["pages"][num]["linkshere"]:
                        resp["query"]["pages"][num]["linkshere"].append(item)
                    # Repeat recursively until no lhcontinue ID is found
                    if "continue" in more.keys():
                        await keep_going(more)
        
            # Handling if more than 500 articles linking to article
            if "continue" in resp.keys():
                await keep_going(resp)
            try:
                articles = set(["https://en.wikipedia.org/wiki/" + d["title"].replace(" ", "_") for d in resp["query"]["pages"][num]["linkshere"]])
            except KeyError:
                if len(right_layer) == 1:
                    print("No articles linking to end url")
                return
            common = list(articles.intersection(left_layer))
            if common:
                art = Node(common[0])
                art.parent = node
                for _node in left_nodes:
                    if _node.url == common[0]:
                        print("Right side: ", art.url, _node.url)
                        print_path(art, connecting_node=_node, side="right")
            else:
                for article in list(articles):
                    if article not in previously_checked:
                        a = Node(article)
                        a.parent = node
                        right_layer.append(article)
                        right_nodes.append(a)
                        previously_checked.append(article)

async def bound_fetch(sem, node, session, linkshere):
    async with sem:
        if linkshere:
            await fetch_right(node, session)
        else:
            await fetch_left(node, session)

async def run(nodes, linkshere=False):
    tasks = []
    sem = asyncio.Semaphore(1000)
    async with ClientSession() as session:
        for node in nodes:
            task = asyncio.ensure_future(bound_fetch(sem, node, session, linkshere=linkshere))
            tasks.append(task)
        responses = asyncio.gather(*tasks)
        await responses

def main():
    while True:
        loop = asyncio.get_event_loop()
        if len(left_nodes) <= len(right_nodes):
            future = asyncio.ensure_future(run(left_nodes))
        else:
            future = asyncio.ensure_future(run(right_nodes, linkshere=True))
        loop.run_until_complete(future)
        print(f"{len(previously_checked)} articles checked. {len(left_nodes)} nodes in left graph, {len(right_nodes)} nodes in right graph.")

if __name__ == "__main__":
    start_url = input("Start url: ")
    end_url = input("End url: ")
    left_layer = [start_url]
    right_layer = [end_url]
    left_nodes = [Node(start_url)]
    right_nodes = [Node(end_url)]
    previously_checked = []
    start = time.perf_counter()
    main()
    