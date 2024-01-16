from bs4 import BeautifulSoup

def get_tech_content(id: int, html_file, base_url) -> dict:
  content = dict()
  soup = BeautifulSoup(html_file, 'lxml')

  box = soup.find_all('div', class_= 'u-shadow-v11 rounded g-pa-30')
  if len(box) < 2:
    print('\terror - redirect')
    return {}
  else:
    box1 = box[0]
    box2 = box[1]
  # contains: name, rating, industry, website, company description, company size, point of 
  # contact
  # contains: deliverable description and work time 
  list_group_items = box1.find_all('li', class_= 'list-group-item')
  print(f"Len {len(list_group_items)}")
  if len(list_group_items) < 13:
    print('\terror - not tech')
    return {}
  proj_desc = box1.find('p', class_='margin-bottom-40')
  if len(proj_desc) == 0:
    print('\terror - not tech')
    return {}
  if len(box2) < 2:
    print('\terror - not tech')
    return {}
  start_date = box2.find_all('div', class_='col-xs-6')
  start_date = start_date[1].text.strip()
  if not("2024" in start_date):
    print('\tWrong year')
    return {}

  content['name'] = f"{list_group_items[0].find('div', class_='col-xs-8').text.strip()}"
  # content['start_date'] = f"{start_date}"
  content['industry'] = f"{list_group_items[1].find('div', class_='col-xs-8').text.strip()}" 
  content['url'] = f'{base_url}{id}'
  content['website'] = f"{list_group_items[2].find('div', class_='col-xs-8').text.strip()}"
  content['company_description'] = f"{list_group_items[3].find('div', class_='col-xs-8').text.strip()}"
  content['project_description'] = f"{proj_desc.text.strip()}"
  content['deliverable_description'] = f"{list_group_items[6].find('div', class_='col-xs-8').text.strip()}" 
  content['work_time'] = f"{list_group_items[8].find('div', class_='col-xs-8').text.strip()}"
  content['new_or_existing'] = f"{list_group_items[9].find('div', class_='col-xs-8').text.strip()}" 
  content['deliverable_type'] = f"{list_group_items[10].find('div', class_='col-xs-8').text.strip()}" 
  content['work_type'] = f"{list_group_items[11].find('div', class_='col-xs-8').text.strip()}" 
  content['tech_stack'] = f"{list_group_items[12].find('div', class_='col-xs-8').text.strip()}" 
  print()
  return content
