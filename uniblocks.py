import unicodedata
import requests

def fetch_unicode_blocks(url):
    response = requests.get(url)
    response.raise_for_status()  # Raise an error if the request failed
    lines = response.text.split('\n')
    blocks = []
    for line in lines:
        if line.startswith('#') or line.strip() == '':
            continue  # Skip comments and empty lines
        range_part, block_name = line.strip().split('; ')
        start, end = range_part.split('..')
        blocks.append((int(start, 16), int(end, 16), block_name))
    return blocks

def is_printable(char):
    category = unicodedata.category(char)
    return not category.startswith('C') and not category in ['Zl', 'Zp']

def print_block_characters(start, end, block_name):
    print(f"Printing block: {block_name} (U+{start:04X} to U+{end:04X})")
    for code_point in range(start, end + 1):
        char = chr(code_point)
        if is_printable(char):
            try:
                print(char, end=' ')
            except UnicodeEncodeError:
                pass  # Skip characters that cannot be encoded by the terminal
    input()

def main(url):
    blocks = fetch_unicode_blocks(url)
    for start, end, block_name in blocks:
        print_block_characters(start, end, block_name)

if __name__ == "__main__":
    url = 'http://www.unicode.org/Public/UNIDATA/Blocks.txt'
    main(url)
