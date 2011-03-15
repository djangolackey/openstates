import re

from billy.scrape import NoDataForPeriod
from billy.scrape.bills import BillScraper, Bill

import lxml.html
import urllib, urlparse

import datetime

CHAMBERS = {
    'H': 'lower',
    'S': 'upper',
    'house': 'lower',
    'senate': 'upper',
}

test_file = "/Users/webdesk/Sprints/OpenGov/dfadooas/test.txt"

class ARBillsScraper(BillScraper):
    state = 'ar'

    def get_bill_status_rows(self, root, id):
        row = []
        status_wrapper = root.get_element_by_id(id)
        for table in status_wrapper:
            for table_row in table:
                row.append(table_row.cssselect('td'))
        return row


    def bill_history(self, bill, html):
        rows = self.get_bill_status_rows(html, '__gvctl00_ctl15_g_bfe6d8cd_6535_437b_86e9_601246028fa1_GridView1__div')
        for row in rows:
            if len(row) >= 4:
                column_count = 0
                file = open('/Users/webdesk/Sprints/OpenGov/dfadooas/bill_actions.txt', 'w')
                for column in row:
                    file.write(str(column_count) + ": " + column.text_content())
                    column_count += 1
                file.close()
                action_args = []
                action_kwargs = {}
                action_args.append(CHAMBERS[(row[0].text_content()).lower()])
                action_args.append(row[2].text_content())
                action_args.append(datetime.datetime.strptime(row[1].text_content(), '%m/%d/%Y %I:%M:%S %p' ))
                action_kwargs['type'] = None
                bill.add_action(*action_args, **action_kwargs)

    def add_sponsors(self, bill, html):
        rows = self.get_bill_status_rows(html, 'ctl00_ctl15_g_d4925428_6cd1_419b_9d52_6e43902068ae')
        type = 'primary'
        for row in rows:
            for item in row:
                if not item.text_content().lower() == 'cosponsors' and not bill['bill_id'] in item.text_content().lower():
                    if not item.text_content().lower() == 'primary sponsor(s)':
                        if item.text_content():
                            bill.add_sponsor(type, item.text_content())
                if item.text_content().lower() == 'cosponsors':
                    type = 'cosponsor'

    def all_scrape(self, chamber, session):
        url = ('ftp://www.arkleg.state.ar.us/dfadooas/LegislativeMeasures.txt')
        file = self.urlopen(url).decode('UTF-8', 'ignore')
        count = 0
        lines = file.split('\n')
        for item in lines:
            if item and count:
                item_chamber, type, bill_number, title, title_sub_1, title_sub_2, title_sub_3, title_sub_4, \
                title_sub_5, title_sub_6, record_id, initial_sponsor, act_number, initial_date, action_date, \
                unknown_legislator, bill_id, congressional_session = item.split('|')
                congressional_session = congressional_session.strip()
                if congressional_session == session and chamber == CHAMBERS[item_chamber]:
                    bill = Bill(session, chamber, bill_id, title, act_number=act_number)
                    if initial_sponsor:
                        bill.add_sponsor('primary', initial_sponsor)
                        bill.add_source(url)
                    self.save_bill(bill)
                    base_url = 'http://www.arkleg.state.ar.us/assembly/' + congressional_session[:4] + '/' + congressional_session + '/Pages/'
#                     try:
#                         html = self.urlopen(base_url + 'BillInformation.aspx?measureno=' + bill_id)
#                     except:
#                         pass

                    try:
                        html = self.urlopen(base_url + 'BillStatusHistory.aspx?measureno=' + bill_id)
                    except:
                        pass
                    else:
                        history = self.bill_history(bill, lxml.html.fromstring(html))

                    try:
                        html = self.urlopen(base_url + 'CoSponsors.aspx?measureno=' + bill_id)
                    except:
                        pass
                    else:
                        add_sponsors = self.add_sponsors(bill, lxml.html.fromstring(html))

                    count += 1
        return count

    def scrape(self, chamber, session):
        count = self.all_scrape(chamber, session)

# def url_fix(s, charset='utf-8'):
#     """http://stackoverflow.com/questions/120951/how-can-i-normalize-a-url-in-python"""
#     if isinstance(s, unicode):
#         s = s.encode(charset, 'ignore')
#     scheme, netloc, path, qs, anchor = urlparse.urlsplit(s)
#     path = urllib.quote(path, '/%')
#     qs = urllib.quote_plus(qs, ':&=')
#     return urlparse.urlunsplit((scheme, netloc, path, qs, anchor))
