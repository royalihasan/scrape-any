from bs4 import BeautifulSoup


def clean_html(html_content):
    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Define the tags to remove
    unwanted_tags = ['head', 'hr', 'br', 'link', 'style', 'meta',
                     'script', 'noscript', 'button', 'header', 'footer', 'nav']

    # Remove all unwanted tags
    for tag in unwanted_tags:
        for match in soup.find_all(tag):
            match.decompose()  # Completely remove the tag and its content

    # Remove all attributes from all tags, except for <a> and <img>
    for tag in soup.find_all(True):  # Find all tags
        if tag.name == 'a':
            # Keep only the 'href' attribute for <a>
            tag.attrs = {key: value for key,
                         value in tag.attrs.items() if key == 'href'}
        elif tag.name == 'img':
            # Keep only the 'src' and 'alt' attributes for <img>
            tag.attrs = {key: value for key, value in tag.attrs.items() if key in [
                'src', 'alt']}
        else:
            # Remove all attributes for other tags
            tag.attrs = {}

    return str(soup)


if __name__ == "__main__":
    # Read the HTML content from the local file
    with open('test.html', 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Clean the HTML content
    cleaned_html = clean_html(html_content)

    # Save the cleaned HTML to a new file
    with open('cleaned_file.html', 'w', encoding='utf-8') as file:
        file.write(cleaned_html)

    print("HTML cleaned and saved to 'cleaned_file.html")
