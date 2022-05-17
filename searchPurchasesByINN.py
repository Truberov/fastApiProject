import time
import schedule
from bs4 import BeautifulSoup
import requests
import sqlite3
import re
import traceback
from time import sleep
import sys


def getValueFromTable(tableName, cursor, connection, nameValues, query):
    cursor.execute(f'''
        SELECT {nameValues and ', '.join([f'"{name}"' for name in nameValues]) or '*'}
        FROM {tableName}
        WHERE {" AND ".join([f'"{q[0]}"=?' for q in query])}
    ''', [q[1] if not type(q[1]) == str else q[1].replace('"', '\'') for q in query])
    return cursor.fetchone()


def pasteToTable(tableName, cursor, connection, params):
    values = []
    for v in params:
        values.append((v and isinstance(v, str)) and v.replace('"', '\'') or v)
    cursor.executemany(f'''
        INSERT OR REPLACE INTO {tableName} 
        VALUES ({",".join(["?" for _ in params])})
        ''',
                       [values]
                       )
    connection.commit()


def pasteToTableByQuery(tableName, cursor, connection, params, query):
    q = getValueFromTable(tableName, cursor, connection, None, query)
    if not q:
        pasteToTable(tableName, cursor, connection, [p[1] for p in params])
    else:
        values = []
        for v in params:
            values.append((v[1] and isinstance(v[1], str)) and v[1].replace('"', '\'') or v[1])
        for number, i in enumerate(query):
            query[number] = (
                i[0] if not type(i[0]) == str else i[0].replace('"', '\''),
                i[1] if not type(i[1]) == str else i[1].replace('"', '\'')
            )
        cursor.executemany(f'''
            UPDATE {tableName} SET {', '.join([f'"{par[0]}"=?' for par in params])} 
            WHERE {" AND ".join([f'"{q[0]}"="{q[1]}"' for q in query])}
            ''',
                           [values]
                           )
        connection.commit()


def getPage(url, session, headers):
    sleep(0.2)
    try:
        resp = session.get(url=url, headers=headers, timeout=60)
        return resp
    except Exception as e:
        traceback.print_exc()
        print('Произошло исключение.')


def getInfo(infoBlocks, infoName):
    for infoBlock in infoBlocks:
        title = infoBlock.find('span', attrs={'class': 'section__title'})
        if title and infoName in title.text.strip():
            return infoBlock.find('span', attrs={'class': 'section__info'}).text.strip().split('\n')[0]


def getInfoFromSection(rowsBlockInfo, sectionName, infoName):
    for row in rowsBlockInfo:
        title = row.find('h2', attrs={'class': 'blockInfo__title'})
        if title and title.text.strip() == sectionName:
            sections = row.find_all('section', attrs={'class': 'blockInfo__section'})
            return getInfo(sections, infoName)


def getCommonInfo(blocks, infoName):
    for block in blocks:
        if block.text == infoName:
            return block.find_next_sibling().text.strip()


headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.51 Safari/537.36'
}


class PurchaseParserByINN:
    def __init__(self, dbNamePurchasesByINN=':memory:'):
        self.dbNamePurchasesByINN = dbNamePurchasesByINN
        self.connection = sqlite3.connect(dbNamePurchasesByINN)
        self.cursor = self.connection.cursor()
        self.cursor.execute('PRAGMA journal_mode = OFF')
        self.createTables()
        self.session = requests.Session()
        self.headers = headers

    def getDataForSite(self, record):
        companyNameAndLink = record.select_one('div.registry-entry__body-href')
        siteName = companyNameAndLink.text.strip()
        data = getValueFromTable(
            'site',
            self.cursor,
            self.connection,
            ['rowid'],
            [
                ['name', siteName]
            ]
        )
        if not data:
            href = companyNameAndLink.select_one('a').get('href')
            print(href)
            resp = getPage(f'https://zakupki.gov.ru{href}&tab=other', self.session, self.headers)
            if resp:
                page = BeautifulSoup(resp.content, 'html.parser')
                infoBlocks = page.select('section.blockInfo__section')
                sitelink = getInfo(infoBlocks, 'Адрес организации в сети Интернет')
                pasteToTable('site', self.cursor, self.connection, [
                    siteName,
                    sitelink,
                    ''
                ])
            else:
                pasteToTable('site', self.cursor, self.connection, [
                    siteName,
                    '',
                    ''
                ])
            data = getValueFromTable(
                'site',
                self.cursor,
                self.connection,
                ['rowid', ],
                [
                    ['name', siteName]
                ]
            )

        print(data)
        return data[0]

    def getDataForContractFiles(self, record):
        contractLinkAndCode = record.select_one('div.registry-entry__header-mid__number a')
        href = contractLinkAndCode.get('href')
        contractCode = contractLinkAndCode.text.strip('\n №\t')
        print(contractCode)
        resp = getPage(f'https://zakupki.gov.ru{href}', self.session, self.headers)
        if resp:
            page = BeautifulSoup(resp.content, 'html.parser')
            infoBlocks = page.select('section.blockInfo__section')
            purchaseID = getInfo(infoBlocks, 'Идентификационный код закупки (ИКЗ)')
            print(f'https://zakupki.gov.ru{href.replace("common-info", "documents")}')
            resp = getPage(f'https://zakupki.gov.ru{href.replace("common-info", "documents")}', self.session,
                           self.headers)
            if resp:
                page = BeautifulSoup(resp.content, 'html.parser')
                attachments = page.select('div.col-6.b-left div.attachment__value')
                print(len(attachments))
                if len(attachments) == 0:
                    attachments = page.select('div.blockFilesTabDocs div.attachment')
                else:
                    attchs = attachments[0].select('span.count')
                    if len(attchs) > 0:
                        attachments = attchs
                for attachment in attachments:
                    docField = attachment.select('a')[-1]
                    link = docField.get('href').replace('https://zakupki.gov.ru', '')
                    contractDocLink = f"https://zakupki.gov.ru{link}"
                    contractDocName = docField.text.strip()
                    if not getValueFromTable(
                            'ContractFiles',
                            self.cursor,
                            self.connection,
                            None,
                            [
                                ['code', contractCode],
                                ['name', contractDocName],
                                ['link', contractDocLink]
                            ]):
                        pasteToTable(
                            'ContractFiles',
                            self.cursor,
                            self.connection,
                            [
                                contractCode,
                                contractDocName,
                                contractDocLink
                            ]
                        )
                    else:
                        print('Already doc exist. Skip...')

    def getDataForContract(self, record, inn):
        contractLinkAndCode = record.select_one('div.registry-entry__header-mid__number a')
        href = contractLinkAndCode.get('href')
        contractCode = contractLinkAndCode.text.strip('\n №\t')
        print(contractCode)

        contractStatus = record.select_one('div.registry-entry__header-mid__title').text.strip()
        print(contractStatus)
        contractName = record.select_one('div.registry-entry__body-value').text.strip()
        print(contractName)

        companyNameAndLink = record.select_one('div.registry-entry__body-href')
        siteName = companyNameAndLink.text.strip()
        contractSite = getValueFromTable(
            'site',
            self.cursor,
            self.connection,
            ['rowid'],
            [
                ['name', siteName]
            ]
        )[0]
        print(f'https://zakupki.gov.ru{href}')
        resp = getPage(f'https://zakupki.gov.ru{href}', self.session, self.headers)
        if resp:
            page = BeautifulSoup(resp.content, 'html.parser')
            price = page.select_one('div.price-block__value')
            if not price:
                price = page.select_one('span.cost')

            price = price.text.strip()
            price = re.sub(r'[^0-9\.,]', '', price)
            price = float(price.replace(',', '.'))

            titleType = page.select_one('div.registry-entry__header-top__title')
            if not titleType:
                titleType = page.select_one('div.cardMainInfo__title')
            # print(titleType)
            dataBlocks = page.select('div.data-block__title')
            if not dataBlocks:
                dataBlocks = page.select('span.cardMainInfo__title')
            # else:    
            datePosted = getCommonInfo(dataBlocks, 'Размещено').strip()
            print(datePosted)
            dateUpdated = getCommonInfo(dataBlocks, 'Обновлено').strip()
            print(dateUpdated)
            infoBlocks = page.select('section.blockInfo__section')
            if len(infoBlocks) > 0:
                typePurchase = getInfo(infoBlocks, 'Способ определения поставщика (подрядчика, исполнителя)')
                print(typePurchase)

                law = titleType.text.strip().replace(typePurchase, '').strip()
                purchaseId = getInfo(infoBlocks, 'Идентификационный код закупки (ИКЗ)')
                print(law)
            else:
                commonBlocks = page.select('div.common-text__title')
                typePurchase = getCommonInfo(commonBlocks, 'Способ осуществления закупки')
                law = titleType.text.strip().replace(typePurchase, '').strip()
                purchaseId = 'NULL'

                print(law)

            pasteToTableByQuery('contract', self.cursor, self.connection, [
                ['name', contractName],
                ['law', law],
                ['status', contractStatus],
                ['company', inn],
                ['type_purchase', typePurchase],
                ['site', contractSite],
                ['code', contractCode],
                ['price', price],
                ['purchase_id', purchaseId],
                ['date_posted', datePosted],
                ['date_updated', dateUpdated]
            ], [
                                    ('site', contractSite),
                                    ('code', contractCode)
                                ])

    def parse(self, inn):
        print(inn)
        pageNumber = 1
        maxPage = None
        while True:
            print(f'Page: {pageNumber}')
            if maxPage and pageNumber > maxPage:
                print('All pages loaded. Exit')
                break
            url = f'https://zakupki.gov.ru/epz/order/extendedsearch/results.html?searchString={inn}&morphology=on&publishDateFrom=01.01.2022&recordsPerPage=_50&pageNumber={pageNumber}'

            print(f'Разбор страницы: {url}')
            resp = getPage(url, self.session, self.headers)
            if resp:
                page = BeautifulSoup(resp.content, 'html.parser')
                pagination = page.find('ul', attrs={'class': 'pages'}).findAll('span')[-1].text
                if pagination:
                    maxPage = int(pagination)
                records = page.select('div.registry-entry__form')
                print(len(records))

                for num, record in enumerate(records):
                    # if num == 3:
                    #     break
                    contractLink = record.select_one('div.registry-entry__header-mid__number a')
                    contractCode = contractLink.text.strip('\n №\t')
                    print(contractCode)

                    contractStatus = record.select_one('div.registry-entry__header-mid__title').text.strip()
                    print(contractStatus)
                    contractName = record.select_one('div.registry-entry__body-value').text.strip()
                    print(contractName)

                    if getValueFromTable(
                            'contract',
                            self.cursor,
                            self.connection,
                            None,
                            [
                                ['status', 'Подача заявок'],
                                ['code', contractCode],
                            ]) or getValueFromTable(
                        'contract',
                        self.cursor,
                        self.connection,
                        None,
                        [
                            ['status', 'Работа комиссии'],
                            ['code', contractCode],
                        ]):
                        print('Already exist. Update...')
                        self.getDataForContractFiles(record)
                        self.getDataForContract(record, inn)

                    elif not getValueFromTable(
                            'contract',
                            self.cursor,
                            self.connection,
                            None,
                            [
                                ['code', contractCode],
                            ]):
                        print('Not exist. Paste to table...')
                        siteID = self.getDataForSite(record)
                        self.getDataForContractFiles(record)
                        self.getDataForContract(record, inn)
                pageNumber += 1
            else:
                print('Page not found. Exit')
                break

    def createTables(self):
        self.cursor.execute(f''' 
            CREATE TABLE IF NOT EXISTS ContractFiles (
                "code" "TEXT",
                "name" "TEXT",
                "link" "TEXT",
                FOREIGN KEY ("code") REFERENCES contract ("code")
            )
        ''')

        self.cursor.execute(f''' 
            CREATE TABLE IF NOT EXISTS site (
                "name" "TEXT",
                "sitelink" "TEXT",
                "purchaselink" "TEXT"
            )
        ''')

        self.cursor.execute(f''' 
            CREATE TABLE IF NOT EXISTS contract (
                "name" "TEXT",
                "law" "TEXT",
                "status" "TEXT",
                "company" "TEXT",
                "type_purchase" "TEXT",
                "site" "INTEGER",
                "code" "TEXT",
                "price" "REAL",
                "purchase_id" "INTEGER",
                "date_posted" "TEXT",
                "date_updated" "TEXT",
                FOREIGN KEY ("site") REFERENCES site ("id")
            )
        ''')

    def close(self):
        self.cursor.close()
        self.connection.close()
        self.session.close()


def parse():
    purchaseParserByINN = PurchaseParserByINN(dbNamePurchasesByINN='ZakupkiPoINN.db')
    inn = 7729040491
    purchaseParserByINN.parse(inn)
    purchaseParserByINN.close()


if __name__ == '__main__':
    schedule.every().day.at("20:15").do(parse)
    while True:
        schedule.run_pending()
        time.sleep(1)
