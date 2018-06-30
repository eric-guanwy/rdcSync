import threading
from threading import Thread
import urllib.parse,urllib.request,http.cookiejar
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from logger import *
from queue import Queue
from datacollector import *

class datasubmit(Thread):
	def __init__(self, name, url, data_queue):
		Thread.__init__(self, name=name)
		logging.info('Threading {} initialized...'.format(name))
		self.name = name
		self.url = url
		self.driver = webdriver.PhantomJS(executable_path="scripts/phantomjs.exe")
		#self.driver = webdriver.Chrome()
		self.data_queue = data_queue

		self.driver.set_page_load_timeout(30)
		time.sleep(3)

	def open_url(self):
		self.driver.get(self.url)
		time.sleep(3)


	def data_writer(self,data_array):
		self.open_url()
		
		cat_input = self.driver.find_element_by_xpath('//*[@class="subform-content"]/div[@class="subform-row"][@row-idx="{}"]/div[@class="subform-cell"]/div[@widgetname="_widget_1506786760764"]/div/input'.format(0))
		brdname_input = self.driver.find_element_by_xpath('//*[@class="subform-content"]/div[@class="subform-row"][@row-idx="{}"]/div[@class="subform-cell"]/div[@widgetname="_widget_1506786760766"]/div/input'.format(0))
		mat_input = self.driver.find_element_by_xpath('//*[@class="subform-content"]/div[@class="subform-row"][@row-idx="{}"]/div[@class="subform-cell"]/div[@widgetname="_widget_1513909282950"]/div/input'.format(0))
		batch_number_input = self.driver.find_element_by_xpath('//*[@class="subform-content"]/div[@class="subform-row"][@row-idx="{}"]/div[@class="subform-cell"]/div[@widgetname="_widget_1522567414307"]/div/input'.format(0))
		repo_count_input = self.driver.find_element_by_xpath('//*[@class="subform-content"]/div[@class="subform-row"][@row-idx="{}"]/div[@class="subform-cell"]/div[@widgetname="_widget_1520927125908"]/div/input'.format(0))

		add_btn = self.driver.find_element_by_xpath('//*[@id="content"]/div[1]/div/div/div[2]/ul/li[8]/div[2]/div/div[5]/div')
		submit_btn = self.driver.find_element_by_xpath('//*[@id="content"]/div[1]/div/div/div[3]/div/div')
		
		[c,b,m,mt,bn,nbn,i] = data_array
		#	try:
		cat_input.clear()
		cat_input.send_keys(c)
		cat_input.send_keys(Keys.TAB)
		#time.sleep(2)
		brdname_input.clear()
		brdname_input.send_keys(b)
		brdname_input.send_keys(Keys.TAB)
		#time.sleep(2)
		mat_input.clear()
		mat_input.send_keys(m)
		mat_input.send_keys(Keys.TAB)
		#time.sleep(2)

		while not batch_number_input.is_displayed():
			try:
				#add_btn.click()
				logging.debug('batch_number_input.is_displayed: {}'.format(batch_number_input.is_displayed()))
				mat_input.send_keys(Keys.TAB)
			except Exception as e:
				logging.error(e)				
				time.sleep(1)
		 	 
		batch_number_input.clear()
		batch_number_input.send_keys(bn)		
		batch_number_input.send_keys(Keys.TAB)
		#batch_number.send_keys(Keys.ENTER)
		logging.debug('repo_count {}'.format(repo_count_input.get_attribute('value')))
		#time.sleep(3)
		while '' == repo_count_input.get_attribute('value'):
			time.sleep(1)

		logging.debug('repo_count {}'.format(repo_count_input.get_attribute('value')))
		#add_btn.click()
		#submit_btn.send_keys(Keys.ENTER)
		submit_btn.click()
		time.sleep(1)
		#print(html)

		"""			except Exception as e:
						logging.error(e)
					else:
						pass
					finally:
						pass"""

	def run(self):		
		while not self.data_queue.empty():
			self.data_writer(self.data_queue.get())
			logging.info("data_queue qsize: {}".format(self.data_queue.qsize()))
			logging.debug("current total threads {}".format(threading.active_count()))

		logging.info("{} exit,current total threads {}".format(self.name,threading.active_count()))
		self.driver.quit()


if __name__ == '__main__':

	RDC_URL = r'https://www.jiandaoyun.com/r/5b25197e35e4396e9a0e95f6'
	REPO_URL = r'https://www.jiandaoyun.com/f/5b0b1ff9d172903a1c0b5553'
	q_data = Queue()
	q_page = Queue()

	for i in range(1,4):
		q_page.put(i)

	dcollectors = []
	dwriters = []

	for i in range(3):
		dcollectors.append(datacollector(name='dcollector {}'.format(i),url = RDC_URL, data_queue=q_data, page_queue=q_page))


	for dc in dcollectors:
		dc.setDaemon(True)
		dc.start()

	for dc in dcollectors:
		dc.join()

	for i in range(10):
		dwriters.append(datasubmit(name='dwriter {}'.format(i),url=REPO_URL, data_queue=q_data))

	for dwriter in dwriters:
		dwriter.setDaemon(True)
		dwriter.start()
		

	for dwriter in dwriters:
		dwriter.join()

	