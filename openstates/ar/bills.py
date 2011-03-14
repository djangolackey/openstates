import re

from billy.scrape import NoDataForPeriod
from billy.scrape.bills import BillScraper, Bill

import lxml.html
import urllib, urlparse

CHAMBERS = {
    'H': 'lower',
    'S': 'upper',
}

class ARBillsScraper(BillScraper):
    state = 'ar'

    def all_scrape(self, chamber, session):
        url = ('ftp://www.arkleg.state.ar.us/dfadooas/LegislativeMeasures.txt')
        file = self.urlopen(url).decode('UTF-8', 'ignore')
        count = 0
        lines = file.split('\n')
        for item in lines:
            if item:
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
                    count += 1
        return count
#                 try:
#                     html = urllib2.urlopen('http://www.arkleg.state.ar.us/assembly/' + congressional_session[:4] + '/' + congressional_session + '/Pages/BillInformation.aspx?measureno=' + bill_id)
#                 except:
#                     pass

    def scrape(self, chamber, session):
        count = self.all_scrape(chamber, session)

def url_fix(s, charset='utf-8'):
    """http://stackoverflow.com/questions/120951/how-can-i-normalize-a-url-in-python"""
    if isinstance(s, unicode):
        s = s.encode(charset, 'ignore')
    scheme, netloc, path, qs, anchor = urlparse.urlsplit(s)
    path = urllib.quote(path, '/%')
    qs = urllib.quote_plus(qs, ':&=')
    return urlparse.urlunsplit((scheme, netloc, path, qs, anchor))
