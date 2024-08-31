from markdownify import MarkdownConverter


class CustomMarkdownConverter(MarkdownConverter):
    """
    Custom MarkdownConverter to handle links and images with specific formatting.
    """

    def convert_a(self, el, text, convert_as_inline):
        """
        Convert <a> tags to Markdown links.
        """
        href = el.get('href', '')
        return f"[{text}]({href})"

    def convert_img(self, el, text, convert_as_inline):
        """
        Convert <img> tags to Markdown images with custom handling.
        """
        src = el.get('src', '')
        alt = el.get('alt', '')
        return f"![{alt}]({src})"


def convert_html_to_clean_markdown(html_content):
    """Converts HTML content to cleaned Markdown format using a custom converter."""
    try:
        # Convert HTML content to Markdown using the custom converter
        markdown_content = CustomMarkdownConverter().convert(html_content)

        # Clean the Markdown content
        cleaned_markdown_content = markdown_content.replace('\\', '')
        cleaned_markdown_content = "\n".join(
            line.strip() for line in cleaned_markdown_content.splitlines() if line.strip()
        )

        return cleaned_markdown_content

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


if __name__ == "__main__":
    # Example usage
    html_content = """
    <html>
        <head><title>Example</title></head>
        <body>
            <h1>Welcome</h1>
            <p>This is an <a href="https://example.com">example link</a>.</p>
            <img src="https://example.com/image.jpg" alt="Example Image">
        </body>
    </html>
    """
    cleaned_markdown_content = convert_html_to_clean_markdown(html_content)

    if cleaned_markdown_content is not None:
        print("Cleaned Markdown content:")
        print(cleaned_markdown_content)
    else:
        print("Failed to convert HTML to Markdown.")
