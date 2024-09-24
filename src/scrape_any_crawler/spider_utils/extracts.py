import re


def extract_uuid(url: str) -> str:
    """
    Extracts a UUID from the given URL.

    Parameters:
    url (str): The URL containing the UUID.

    Returns:
    str: The extracted UUID, or None if no UUID is found.
    """
    # Regular expression pattern to match UUIDs (8-4-4-4-12 format)
    pattern = r'[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}'

    # Search for the UUID in the URL
    match = re.search(pattern, url)

    # Return the UUID if found, otherwise return None
    return match.group(0) if match else None


def extract_product_codes_from_list(description_list):
    # Define a regular expression pattern to match "Product Code: <number>"
    pattern = r"Product Code:\s*(\d+)"

    # Iterate over each description in the list
    for description in description_list:
        # Search for the pattern in the current description
        match = re.search(pattern, description)
        if match:
            # Return the first found product code
            return match.group(1)

    # Return None if no product code is found
    return None


def extract_id_from_url(url):
    # Define a regular expression pattern to match the ID in the file name
    pattern = r'_([a-zA-Z0-9]+)\.[a-z]+$'
    
    # Search for the pattern in the URL
    match = re.search(pattern, url)
    
    # If a match is found, return the ID, else return None
    if match:
        return match.group(1)
    return None

def find_first_id(images_list):
    # Iterate over each image URL in the list
    for url in images_list:
        id_value = extract_id_from_url(url)
        if id_value:
            return id_value  # Return the ID as a string
    
    # Return None if no ID is found
    return None


if __name__ == "__main__":
   # Example usage
    images_list = [
        "https://www.aldi.us/fileadmin/fm-dam/Products/Categories/Snacks/Chips_Crackers_and_Popcorn/51797-simply-nature-organic-blue-corn-tortilla-chips-detail.jpg",
        "https://www.aldi.us/fileadmin/fm-dam/Products/Categories/Snacks/Chips_Crackers_and_Popcorn/51797-simply-nature-organic-multigrain-tortilla-chips-detail.jpg",
        "https://www.aldi.us/fileadmin/_processed_/5/2/csm_51797-simply-nature-organic-blue-corn-tortilla-chips-detail_e75769e5dd.jpg",
        "https://www.aldi.us/fileadmin/_processed_/c/8/csm_51797-simply-nature-organic-multigrain-tortilla-chips-detail_d32ddf106d.jpg"
    ]
    id_value = find_first_id(images_list)
    print(f"Extracted ID: {id_value}")
