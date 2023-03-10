import os
import shutil
import requests
from functions.adfly import adfly_bypass, decrypt_url
import sys
from bs4 import BeautifulSoup
import re
from tqdm import tqdm

def main(product_code):

    if len(product_code) != 7:
        print(" It seems that provided argument isn't valid product code")
        print()
        sys.exit(1)

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0'}

    response = requests.get(f"http://cellomania.com/ffu/product_codes/{product_code}.html", headers=headers)

    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a')

    for i, link in enumerate(links):
        links[i] = link['href']
    links = [link for link in links if "twitter" not in link]

    if "Invalid Product Code" in response.text or not len(links) > 0:
        print(" Cellomania wasn't able to find firmware using provided product code")
        print()
        sys.exit(0)

    print()

    print(" Found firmware for provided product code. Please wait, processing your request, this might take a minute.")
    print()

    name = re.search("<img src=.*><p><b>Product code: .*</b><br />(.+)<br />.*<br />.*<br />.*<br />.*</p>", response.text)
    if name:
        name = name.group(1)
    rmcode = re.search("<img src=.*><p><b>Product code: .*</b><br />.*<br />(.+)<br />.*<br />.*<br />.*</p>", response.text)
    if rmcode:
        rmcode = rmcode.group(1)
    system = re.search("<img src=.*><p><b>Product code: .*</b><br />.*<br />.*<br />(.+)<br />(.+)<br />.*</p>", response.text)
    if system:
        system = system.group(1)
    variant = re.search("<img src=.*><p><b>Product code: .*</b><br />.*<br />.*<br />.*<br />(.+)<br />.*</p>", response.text)
    if variant:
        variant = variant.group(1)
    version = re.search("<img src=.*><p><b>Product code: .*</b><br />.*<br />.*<br />.*<br />.*<br />(.+)</p>", response.text)
    if version:
        version = version.group(1)
    

    fixed_links_nums = {}
    fixed_links = []
    filenames = {}
    block_size = 1024
    

    for i, link in enumerate(links, start=1):
        output = adfly_bypass(url=link)
        if output['error'] == True:
            print(f" Processing \'{link}\' failed!")
            print()
            continue
        fixed_links_nums[str(i)] = (output['bypassed_url'])
        fixed_links.append(output['bypassed_url'])

    for link in fixed_links_nums.values():
        filename = re.search("/([^/]*)\?", link).group(1)
        filenames[link] = filename

    print(f" Product code: {product_code}")
    if name:
        print(f" Model: {name}")
    if rmcode:
        print(f" Code: {rmcode}")
    if system:
        print(f" OS: {system}")
    if variant:
        print(f" Variant: {variant}")
    if version:
        print(f" Version: {version}")
    print()

    for i, file in zip(fixed_links_nums.keys(), filenames.values()):
        print(f" {i}. {file}")

    print()

    while True:
        ask = input(" Which files do you want to download? Type numbers by comma or a / all to download everything or 0 to exit.\n ")
        print()
        if ask != 0:
            if os.path.isfile(product_code):
                os.remove(product_code)
            if os.path.isdir(product_code):
                shutil.rmtree(product_code)
            os.mkdir(product_code)
            os.chdir(product_code)

        if ask.lower() in ["a", "all"]:
            for link in fixed_links:
                response = requests.get(link, headers=headers, stream=True)
                total_size_in_bytes= int(response.headers.get('content-length', 0))
                progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
                filename = filenames[link]
                with open(filename, "wb") as f:
                    for data in response.iter_content(block_size):
                        progress_bar.update(len(data))
                        f.write(data)
                progress_bar.close()
                print(f" Saved {filename}.")
                print()
            print(" Saved everything.")
            print()
            sys.exit(0)
        elif ask == "0":
            sys.exit(0)
        else:
            todl = ask.split(" ")
            todl = list(set(todl))
            if not all(i in fixed_links_nums.keys() for i in todl):
                print(" One of the numbers is wrong.")
                print()
                continue
            else:
                break

    for i in todl:
        link = fixed_links_nums[i]
        filename = filenames[link]
        response = requests.get(link, headers=headers, stream=True)
        total_size_in_bytes= int(response.headers.get('content-length', 0))
        progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
        with open(filename, "wb") as f:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                f.write(data)
            progress_bar.close()
        print(f" Saved {filename}.")
        print()

if __name__ == "__main__":
    if not len(sys.argv) > 1:
        print(" Provide product code as the first argument!!")
        print()
        sys.exit(1)
    product_code = sys.argv[1]
    try: 
        main(product_code)
    except KeyboardInterrupt: 
        print()
        print(" KeyboardInterrupt, exiting.")
        sys.exit(0)