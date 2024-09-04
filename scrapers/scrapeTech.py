from bs4 import BeautifulSoup

def get_tech_content(id: int, html_file, base_url) -> dict:
    content = dict()
    soup = BeautifulSoup(html_file, 'lxml')

    # Find the main content boxes
    box = soup.find_all('div', class_='u-shadow-v11 rounded g-pa-30')
    if len(box) < 2:
        print('\terror - redirect')
        return {}
    else:
        box1 = box[0]  # Company Details
        box2 = box[1]  # Project Information
    
    if not soup.find('strong', text='Tech Consulting'):
      print('\tNot a tech consulting project')
      return {}
    project_info_list = soup.find_all('ul', class_='list-unstyled margin-bottom-40')
    if not project_info_list or len(project_info_list) < 2:
        print('\terror - insufficient project information')
        return {}

    # Extract company details from the first box
    list_group_items = box1.find_all('li', class_='list-group-item')
    if len(list_group_items) < 6:
        print('\terror - insufficient company details')
        return {}

    # Extract the project start date from the second box
    start_date = box2.find_all('div', class_='col-xs-6')[1].text.strip()
    if not("2024" in start_date):
        print('\tWrong year')
        return {}

    # Extract the relevant details from the company details box
    content['name'] = list_group_items[0].find('div', class_='col-xs-8').text.strip()
    content['industry'] = list_group_items[1].find('div', class_='col-xs-8').text.strip()
    website_link = list_group_items[2].find('div', class_='col-xs-8').a
    content['website'] = website_link['href'].strip() if website_link else 'N/A'
    content['company_description'] = list_group_items[3].find('div', class_='col-xs-8').text.strip()

    # Extract project description
    proj_desc = box1.find('p', class_='margin-bottom-40')
    if proj_desc:
        content['project_description'] = proj_desc.text.strip()
    else:
        print('\terror - no project description found')
        content['project_description'] = 'N/A'

    # Extract deliverable details from the project_info_list
    def extract_info_from_list(ul_element, label_text):
        """Helper function to extract information based on label text."""
        for li in ul_element.find_all('li', class_='list-group-item'):
            label = li.find('div', class_='col-xs-4')
            value = li.find('div', class_='col-xs-8')
            if label and label_text in label.text.strip() and value:
                return value.text.strip()
        return 'N/A'

    # Assuming the structure matches the one provided
    if len(project_info_list) >= 2:
        content['deliverable_description'] = extract_info_from_list(project_info_list[0], 'Deliverable Description')
        content['new_or_existing'] = extract_info_from_list(project_info_list[1], 'New or Existing Tech')
        content['deliverable_type'] = extract_info_from_list(project_info_list[1], 'Deliverable Type')
        content['work_type'] = extract_info_from_list(project_info_list[1], 'Work Type')
        content['tech_stack'] = extract_info_from_list(project_info_list[1], 'Technology Stack')
    else:
        print('\terror - insufficient project information')
        content['deliverable_description'] = content['new_or_existing'] = content['deliverable_type'] = content['work_type'] = content['tech_stack'] = 'N/A'

    # Add the URL for reference
    content['url'] = f'{base_url}{id}'

    return content
