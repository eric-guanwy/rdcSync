import threading
from threading import Thread
import urllib.parse,urllib.request,http.cookiejar
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from logger import *
from queue import Queue



class datacollector(Thread):
	def __init__(self, name, url, data_queue, page_queue):
		Thread.__init__(self, name=name)
		logging.info('Threading {} initialized...'.format(name))
		self.url = url
		#assert isinstance(driver, webdriver.phantomjs.webdriver.WebDriver)
		self.driver = webdriver.PhantomJS(executable_path="scripts/phantomjs.exe")
		#self.driver = webdriver.Chrome()
		self.data_queue = data_queue
		self.page_queue = page_queue


		self.driver.set_page_load_timeout(30)
		time.sleep(3)
		self.driver.get(self.url)
		time.sleep(2)


	def totalItems(self):
		html = self.driver.page_source
		content = etree.HTML(html)
		total_items = content.xpath('//*[@id="report"]/div[3]/div/div[2]/div/div[2]/div[2]/div[1]/span/text()')
		#logging.info(total_items)
		return int(total_items[0][1:-1])
		 
	def totalPages(self):
		html = self.driver.page_source
		content = etree.HTML(html)
		total_pages = content.xpath('//*[@id="report"]/div[3]/div/div[2]/div/div[2]/div[2]/div[2]/div[2]/span/text()')
		return int(total_pages[0][3:])

	def currentPage(self):
		html = self.driver.page_source
		content = etree.HTML(html)
		current_page_input = self.driver.find_element_by_xpath('//*[@id="report"]/div[3]/div/div[2]/div/div[2]/div[2]/div[2]/div[2]/div/input')
		current_page = current_page_input.get_attribute('value')
		return int(current_page)

	def locatePage(self, page_number):
		assert(page_number <= self.totalPages())
		current_page_input = self.driver.find_element_by_xpath('//*[@id="report"]/div[3]/div/div[2]/div/div[2]/div[2]/div[2]/div[2]/div/input')
		current_page_input.clear()
		current_page_input.send_keys(int(page_number))
		current_page_input.send_keys(Keys.TAB)		
		time.sleep(2)		
		return self.currentPage()

	def pageDataCollector(self, page_number):
		if int(page_number) != self.currentPage():
			_p = self.locatePage(page_number)
			assert page_number == _p

		content = etree.HTML(self.driver.page_source)

		category = content.xpath('//*[@class="table-scroller"]/table/tbody/tr/td[1]/text()')
		brandname = content.xpath('//*[@class="table-scroller"]/table/tbody/tr/td[2]/text()')
		materials = content.xpath('//*[@class="table-scroller"]/table/tbody/tr/td[3]/text()')
		metric = content.xpath('//*[@class="table-scroller"]/table/tbody/tr/td[4]/text()')
		batch_number = content.xpath('//*[@class="table-scroller"]/table/tbody/tr/td[5]/text()')
		name_batch_number = content.xpath('//*[@class="table-scroller"]/table/tbody/tr/td[6]/text()')
		inventory = content.xpath('//*[@class="table-scroller"]/table/tbody/tr/td[7]/text()')

		for c,b,m,mt,bn,nbn,i in zip(category,brandname,materials,metric,batch_number,name_batch_number,inventory):			
			self.data_queue.put([c,b,m,mt,bn,nbn,i])
			logging.info("data_queue size {}".format(self.data_queue.qsize()))
		 

	def run(self):
		while not self.page_queue.empty():
			page_number = self.page_queue.get()			
			self.pageDataCollector(page_number)

		logging.info("{} exit,current total threads {}".format(self.name,threading.active_count()))	
		self.driver.quit()

		




"""

driver.get(RDC_URL)
time.sleep(3)
html=driver.page_source
content = etree.HTML(html)


category = []
brandname = []
materials = []
metric = []
batch_number = []
name_batch_number = []
inventory = []


total_items = content.xpath('//*[@id="report"]/div[3]/div/div[2]/div/div[2]/div[2]/div[1]/span/text()')
print(total_items[0][1:-1])

current_page_input = driver.find_element_by_xpath('//*[@id="report"]/div[3]/div/div[2]/div/div[2]/div[2]/div[2]/div[2]/div/input')
current_page = current_page_input.get_attribute('value')
current_page = int(current_page)

total_pages = content.xpath('//*[@id="report"]/div[3]/div/div[2]/div/div[2]/div[2]/div[2]/div[2]/span/text()')
total_pages = int(total_pages[0][3:])

next_page_btn = driver.find_element_by_xpath('//*[@id="report"]/div[3]/div/div[2]/div/div[2]/div[2]/div[2]/div[1]/button[2]')
print("next_page.is_enabled:{}".format(next_page_btn.is_enabled()))

for page in range(1,total_pages+1):
	html=driver.page_source
	content = etree.HTML(html)
	category = category + content.xpath('//*[@class="table-scroller"]/table/tbody/tr/td[1]/text()')
	brandname = brandname + content.xpath('//*[@class="table-scroller"]/table/tbody/tr/td[2]/text()')
	materials = materials + content.xpath('//*[@class="table-scroller"]/table/tbody/tr/td[3]/text()')
	metric = metric + content.xpath('//*[@class="table-scroller"]/table/tbody/tr/td[4]/text()')
	batch_number = batch_number + content.xpath('//*[@class="table-scroller"]/table/tbody/tr/td[5]/text()')
	name_batch_number = name_batch_number + content.xpath('//*[@class="table-scroller"]/table/tbody/tr/td[6]/text()')
	inventory = inventory + content.xpath('//*[@class="table-scroller"]/table/tbody/tr/td[7]/text()')

	try:
		next_page_btn.click()
		next_page_btn = driver.find_element_by_xpath('//*[@id="report"]/div[3]/div/div[2]/div/div[2]/div[2]/div[2]/div[1]/button[2]')
	except Exception as e:
		next_page_btn = driver.find_element_by_xpath('//*[@id="report"]/div[3]/div/div[2]/div/div[2]/div[2]/div[2]/div[1]/button[2]')
		next_page_btn.click()

"""

if __name__ == '__main__':

	RDC_URL = r'https://www.jiandaoyun.com/r/5b25197e35e4396e9a0e95f6'
	q_data = Queue()
	q_page = Queue()

	#hard code
	for i in range(1,4):
		q_page.put(i)

	dcollectors = []
	
	for i in range(3):
		dcollectors.append(datacollector(name='dcollector {}'.format(i),url = RDC_URL, data_queue=q_data, page_queue=q_page))

	for dc in dcollectors:
		dc.setDaemon(True)
		dc.start()
		
	for dc in dcollectors:
		dc.join()

	while not q_data.empty():
		logging.info("{}|{}".format(q_data.qsize(),q_data.get()))


	
