import xml.etree.ElementTree as ET
import re
import pandas as pd 
from bs4 import BeautifulSoup as bs

def parse_patents(file_name):

    # open file in read mode 
    file = open(file_name, "r") 
    file_content_raw = file.read()
    file.close()
    text1 = re.compile("<\?xml version\=\"1\.0\" encoding\=\"UTF\-8\"\?>")
    file_content = text1.split(file_content_raw)
    while "" in file_content:
        file_content.remove('')

    dic = {
    'juridiction' : [],
    'pub_year' : [],
    'kind' : [],
    'app_year' : [],
    'app_type' : [],
    'prior_year' : [], 
    'prior_country' : [],
    'title' : [],
    'assignee' : [],
    'inventors' : [],
    'abstract' : [], 
    'claims' : []
    }

    for i, file in enumerate(file_content):
    #i = file_content[10]
        root = ET.fromstring(str(bs(file, 'xml')))
        if root.tag == 'us-patent-application':
            # getting country of publication from attributes of the roots 
            dic['juridiction'].append(root.attrib['country'])

            # giving name to childs of root 
            bibliographic_data_elem = root.find('us-bibliographic-data-application')
            abstract = root.find('abstract')
            #drawings = root.find('drawings')
            #description = root.find('description')
            claims = root.find("claims")

            # appending abstract to the dic
            dic['abstract'].append(abstract.find('p').text)

            # appending publication year and kind
            for i in bibliographic_data_elem.find('publication-reference').find('document-id').getchildren():
                if i.tag == 'date':
                    yyyy = i.text[0:4]
                    # mm = i.text[4:6]
                    # dd = i.text[6:8]
                    dic['pub_year'].append(int(yyyy))
                if i.tag == 'kind':
                    dic['kind'].append(i.text)

            # appending application year and application utility
            for i in bibliographic_data_elem.find('application-reference').find('document-id').getchildren():
                if i.tag == 'date':
                    yyyy = i.text[0:4]
                    # mm = i.text[4:6]
                    # dd = i.text[6:8]
                    dic['app_year'].append(int(yyyy))
            dic['app_type'].append(bibliographic_data_elem.find('application-reference').attrib['appl-type'])

            # for priority claims/ if published in other countries 
            priority_claims = bibliographic_data_elem.find('priority-claims')
            if priority_claims != None:
                for i in priority_claims.find('priority-claim').getchildren():
                    if i.tag == 'country':
                        dic['prior_country'].append(i.text)
                    if i.tag == 'date':
                        yyyy = i.text[0:4]
                        dic['prior_year'].append(int(yyyy))
                        #mm = i.text[4:6]
                        #dd = i.text[6:8]
            else:
                dic['prior_country'].append('')
                dic['prior_year'].append('')

            # adding invention title
            dic['title'].append(bibliographic_data_elem.find('invention-title').text)

            # adding assignees
            assignees = bibliographic_data_elem.find('assignees')
            if assignees != None:
                org_names = ''
                for assignee in assignees:
                    if assignee.find('orgname') != None:
                        org_name = assignee.find('orgname').text
                        org_names = org_names + org_name + ';;'
                dic['assignee'].append(org_names)
            else:
                dic['assignee'].append(None)

            # adding Inventors
            us_parties = bibliographic_data_elem.find('us-parties')
            inventors = us_parties.find('inventors').getchildren()
            inventor = ''
            #countries = []
            addressbooks = []
            for i in inventors:
                addressbooks.append(i.getchildren()[0])
            for i in addressbooks:
                name = ''
                childs = i.getchildren()
                for child in childs:
                    if child.tag == 'last-name':
                        name += child.text
                    if child.tag == 'first-name':
                        name = child.text + ' ' + name
                    #if child.tag == 'address':
                    #    countries.append(child.find('country').text)
                inventor = inventor + name + ';;'
            dic['inventors'].append(inventor)

           # adding claims
            claims_child = claims.getchildren()
            claims = ''
            for childs in claims_child:
                for child in childs:
                    for i in child:
                        if i.tag == 'claim-text':
                            if i.text != None:
                                claims += i.text + ' '
            dic['claims'].append(claims)

            # feild if invention
            # backgroung
            # details of drawing 

    df = pd.DataFrame(dic)
    return df