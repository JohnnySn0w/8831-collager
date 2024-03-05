import requests
from bs4 import BeautifulSoup

def scrape_gifs(base_url, pages, target_width, target_height):
    for page in range(1, pages + 1):
        url = f"{base_url}/page{page}.html"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all <img> tags, then filter by width and height attributes
        images = soup.find_all("img", width=str(target_width), height=str(target_height))
        
        for img in images:
            img_url = img['src']
            # Check if the image URL is absolute or relative
            if not img_url.startswith(('http://', 'https://')):
                img_url = f"{base_url}/{img_url}"  # Adjust based on actual URL structure
            download_gif(img_url)

def download_gif(img_url):
    response = requests.get(img_url)
    filename = img_url.split('/')[-1]
    
    # Save the GIF
    with open(f"./gifs/{filename}", 'wb') as f:
        f.write(response.content)
    print(f"Downloaded {filename}")

scrape_gifs('https://hellnet.work/8831', 59, 88, 31)
