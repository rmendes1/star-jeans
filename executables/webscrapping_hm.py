

################## IMPORTS #####################
import logging
import os
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import pandas as pd
import re
import numpy as np
import sqlite3
import logging
from sqlalchemy import create_engine


############### DATA COLLECTION ##################

#creating a useragent
#parameters
def data_collection(url, header):

    # Request to URL
    page = requests.get(url, headers=header)
    logger.debug('Page Response: %s', page)

    # Beautiful soup object
    soup = BeautifulSoup(page.text, 'html.parser')

    # ===================== Product Data ============================
    products = soup.find('ul', class_='products-listing small')
    product_list = products.find_all('article', class_='hm-product-item')

    # product id
    product_id = [p.get('data-articlecode') for p in product_list]

    # product category
    product_category = [p.get('data-category') for p in product_list]

    # product name
    product_list = products.find_all('a', class_='link')
    product_name = [p.get_text() for p in product_list]

    # price
    product_list = products.find_all('span', class_='price regular')
    product_price = [p.get_text() for p in product_list]
    data = pd.DataFrame([product_id, product_category, product_name, product_price]).T

    data.columns = ['product_id', 'product_category', 'product_name', 'product_price']
    return data

######################## DATA COLLECT BY PRODUCT #################################
def data_collection_by_product(data, header):
    # empty dataframe
    df_compositions = pd.DataFrame()

    # unique columns for all products
    aux = []

    cols = ['Art. No.',
            'Composition',
            'Fit',
            'Product safety',
            'Size',
            'More sustainable materials']

    df_pattern = pd.DataFrame(columns=cols)

    for i in range(len(data)):
        # API Requests
        url = 'https://www2.hm.com/en_us/productpage.' + data.loc[i, 'product_id'] + '.html'
        logger.debug('Product: %s, URL: %s', i, url)

        page = requests.get(url, headers=header)

        # BeautifulSoup object
        soup = BeautifulSoup(page.text, 'html.parser')

        product_list = soup.find_all('a', class_='filter-option miniature active') + soup.find_all('a',
                                                                                                   class_='filter-option miniature')
        color_item = [p.get('data-color') for p in product_list]

        # product id
        product_id = [p.get('data-articlecode') for p in product_list]

        # creating data frame with product id+color name
        df_color = pd.DataFrame((product_id, color_item)).T
        df_color.columns = ['product_id', 'color_name']  # renaming columns

        for j in range(len(df_color)):
            # API Requests
            url = 'https://www2.hm.com/en_us/productpage.' + df_color.loc[j, 'product_id'] + '.html'
            logger.debug('Color: %s', url)
            page = requests.get(url, headers=header)

            # BeautifulSoup object
            soup = BeautifulSoup(page.text, 'html.parser')

            ########################  PRODUCT NAME  ###################################
            product_name = soup.find_all('h1', class_='primary product-item-headline')
            product_name = product_name[0].get_text()

            ########################  PRODUCT PRICE  ###################################
            product_price = soup.find_all('div', class_='primary-row product-item-price')
            product_price = re.findall(r'\d+\.?\d+', product_price[0].get_text())[0]

            #######################  COMPOSITION  ######################################

            product_composition_list = soup.find_all('div', class_='pdp-description-list-item')
            product_composition = [list(filter(None, p.get_text().split("\n"))) for p in product_composition_list]

            # renaming labels
            df_composition = pd.DataFrame(product_composition).T
            df_composition.columns = df_composition.iloc[0]

            # deleting first row
            df_composition = df_composition.iloc[1:].fillna(method='ffill')

            # remove pocket lining, shell and lining
            df_composition['Composition'] = df_composition['Composition'].str.replace('Pocket: ', '', regex=True)
            df_composition['Composition'] = df_composition['Composition'].str.replace('Pocket lining: ', '', regex=True)
            df_composition['Composition'] = df_composition['Composition'].str.replace('Shell: ', '', regex=True)
            df_composition['Composition'] = df_composition['Composition'].str.replace('Lining: ', '', regex=True)

            # guarantee the same number of columns
            df_composition = pd.concat([df_pattern, df_composition], axis=0)

            # rename columns
            df_composition.columns = ['product_id', 'composition', 'fit', 'product_safety', 'size', 'sustainable_materials']
            df_composition['product_name'] = product_name
            df_composition['product_price'] = product_price

            # keep new columns if they show up
            aux = aux + df_composition.columns.tolist()

            # merge df_color and df_composition
            df_composition = pd.merge(df_composition, df_color, how='left', on='product_id')

            # all products
            df_compositions = pd.concat([df_compositions, df_composition], axis=0)

    # join showroom data + details
    df_compositions['style_id'] = df_compositions['product_id'].apply(lambda x: x[:-3])
    df_compositions['color_id'] = df_compositions['product_id'].apply(lambda x: x[-3:])

    df_compositions['scrapy_datetime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    return df_compositions

############## DATA CLEANING #########################

def data_cleaning(data_product):
    #product id
    #dropping NaN values
    df_data = data_product.dropna(subset=['product_id'])

    #product_name
    df_data['product_name'] = df_data['product_name'].str.strip()
    df_data['product_name'] = df_data['product_name'].str.replace(' ', '_').str.lower()
    df_data['product_name'] = df_data['product_name'].str.replace('®', '').str.lower()


    #product_price
    df_data['product_price'] = df_data['product_price'].astype(float)

    #color name
    df_data['color_name'] = df_data['color_name'].str.replace(' ', '_').str.lower()

    #fit
    df_data['fit'] = df_data['fit'].apply(lambda x: x.replace(' ', '_').lower() if pd.notnull(x) else x)

    #size number
    df_data['size_number'] = df_data['size'].apply(lambda x: re.search('\d{3}', x).group(0) if pd.notnull(x) else x)
    #df_data['size_number'] = df_data['size_number'].apply(lambda x: re.search('\d+', x).group(0) if pd.notnull(x) else x)

    #size model
    df_data['size_model'] = df_data['size'].str.extract('(\d+/\\d+)')
    df_data['size_model'] = df_data['size_model'].apply(lambda x: x.replace('/', '_') if pd.notnull(x) else x)

    #drop duplicated cells
    #df_data = df_data.drop_duplicates()
    #(subset=['product_id', 'product_category', 'product_name', 'product_price', 'scrapy_time', 'style_id', 'color_id', 'color_name', 'Fit', 'Composition', 'size_number', 'size_model'], keep='last' )

    #reset index
    df_data = df_data.reset_index(drop = True)

    #break composition by comma
    df1 = df_data['composition'].str.split(',', expand = True).reset_index(drop = True)


    #creating new df with columns
    # cotton | polyester | spandex | elasterell
    df_ref = pd.DataFrame(index = np.arange(len(df_data)), columns = ['cotton', 'polyester', 'spandex', 'elasterell'])

    ############################### COMPOSITION #####################################

    #cotton: 0, 1
    #polyester: 0, 1
    #spandex: 1, 2
    #elasterell: 1

    # -------------- cotton --------------
    df_cotton_0 = df1.loc[df1[0].str.contains('Cotton', na = True), 0]
    df_cotton_0.name = 'cotton'
    df_cotton_1 = df1.loc[df1[1].str.contains('Cotton', na = True), 1]
    df_cotton_1.name = 'cotton'

    # combine cotton df's
    df_cotton = df_cotton_0.combine_first(df_cotton_1)

    df_ref = pd.concat([df_ref, df_cotton], axis = 1)
    df_ref = df_ref.iloc[:, ~df_ref.columns.duplicated(keep = 'last')]


    #------------ polyester ---------------
    df_polyester_0 = df1.loc[df1[0].str.contains('Polyester', na = True), 0]
    df_polyester_0.name = 'polyester'
    df_polyester_1 = df1.loc[df1[1].str.contains('Polyester', na = True), 1]
    df_polyester_1.name = 'polyester'

    df_polyester = df_polyester_0.combine_first(df_polyester_1)
    df_ref = pd.concat([df_ref, df_polyester], axis = 1)
    df_ref = df_ref.iloc[:, ~df_ref.columns.duplicated(keep = 'last')]

    #----------- spandex --------------------
    df_spandex_1 = df1.loc[df1[1].str.contains('Spandex', na = True), 1]
    df_spandex_1.name = 'spandex'
    df_spandex_2 = df1.loc[df1[2].str.contains('Spandex', na = True), 2]
    df_spandex_2.name = 'spandex'
    #from jan 10 scrapy
    #df_spandex_3 = df1.loc[df1[3].str.contains('Spandex', na = True), 3]
    #df_spandex_3.name = 'spandex'

    #df_spandex_c2 = df_spandex_1.combine_first(df_spandex_2)

    df_spandex = df_spandex_1.combine_first(df_spandex_2)

    df_ref = pd.concat([df_ref, df_spandex], axis = 1)
    df_ref = df_ref.iloc[:, ~df_ref.columns.duplicated(keep = 'last')]


    # ---------- elasterell --------------------
    df_elasterell = df1.loc[df1[1].str.contains('Elasterell', na = True), 1]
    df_elasterell.name = 'elasterell'

    df_ref = pd.concat([df_ref, df_elasterell], axis = 1)
    df_ref = df_ref.iloc[:, ~df_ref.columns.duplicated(keep = 'last')]

    #combine join with product id
    df_aux = pd.concat([df_data['product_id'].reset_index(drop = True), df_ref], axis = 1)

    #format composition data

    df_aux['cotton']     = df_aux['cotton'].apply(lambda x: int(re.search('\d+', x).group(0))/100 if pd.notnull(x) else x)
    df_aux['elasterell'] = df_aux['elasterell'].apply(lambda x: int(re.search('\d+', x).group(0))/100 if pd.notnull(x) else x)
    df_aux['spandex']    = df_aux['spandex'].apply(lambda x: int(re.search('\d+', x).group(0))/100 if pd.notnull(x) else x)
    df_aux['polyester']  = df_aux['polyester'].apply(lambda x: int(re.search('\d+', x).group(0))/100 if pd.notnull(x) else x)

    #final join
    df_aux = df_aux.groupby('product_id').max().reset_index().fillna(0)
    df_data = pd.merge(df_data, df_aux, on = 'product_id', how = 'left')

    #drop columns
    df_data = df_data.drop(columns = ['size', 'product_safety', 'sustainable_materials', 'composition'])

    df_data = df_data.drop_duplicates()

    return df_data

################ DATA INSERT #######################3
def data_insert(df_data):
    data_insert = df_data[[
        'product_id',
        'style_id',
        'color_id',
        'product_name',
        'color_name',
        'fit',
        'product_price',
        'size_number',
        'size_model',
        'cotton',
        'polyester',
        'spandex',
        'elasterell',
        'scrapy_datetime'
    ]]

    conn = create_engine('sqlite:///database_hm.sqlite')
    data_insert.to_sql('vitrine', con = conn, if_exists = 'append', index = False)

    return None

if  __name__ == '__main__':
    #logging
    path = '/home/joao/projetos/dsaodev/projcode/Logs'

    if not os.path.exists(path):
        os.makedirs(path)

    logging.basicConfig(
            filename = path + '/webscrapping_hm.log',
            level = logging.DEBUG,
            format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
            datefmt = '%Y-%m-%d %H:%M:%S'
    )

    logger = logging.getLogger('webscrapping_hm')


    # parameters and constants
    header = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'}

    # H&M site catalog URL
    url = 'https://www2.hm.com/en_us/men/products/jeans.html'
    #data collection
    data = data_collection(url, header)
    logger.info('Data collection has been done')
    #data collection by prodct
    data_product = data_collection_by_product(data, header)
    logger.info("Data collection by product has been done")
    #data cleaning
    data_product_cleaned = data_cleaning(data_product)
    logger.info("Data product cleaned has been done")
    #data insertion
    data_insert(data_product_cleaned)
    logger.info('Data insertion has been done')