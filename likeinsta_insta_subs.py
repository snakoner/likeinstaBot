# LikeInsta Bot subscriber
# 		this program use selenium module for autosubscribin at likeinsta.ru
#		@author: 	2021, Andrey Stroganov
#		@contact:	https://github.com/snakoner/ 
#		This program is free to use
#

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType

import selenium
import time
import sys
import random
import datetime
import os
import constant

def rand_time(min, max):
	'''
	@brief: function to get random float from {[min, max] + noise}, where noise < 1
	
		@min: 	minimal value
		@max: 	maximum value
	'''
	noise = random.randint(0,100)/100.0
	return random.randint(min, max) + noise


def read_user_data(browser, filename):
	'''
	@brief: function to get user's auth data

		@filename: 	source file with user's auth data
	'''
	data = []
	try:
		with open(filename, 'r') as f:
			data = f.read().splitlines()
	except IOError:
		error_report("Can't get file: {}".format(filename))
		kill_proc(browser)

	return data[0], data[1]


def get_user_balance(browser):
	'''
	@brief: function to get user's balance at bosslike.ru. 
			To get balance current window must be bosslike.ru.

		@browser: 	actual browser object
	'''
	return browser.find_element_by_id("user_points_balance").text

def error_report(message):
	print("[ERROR] {}".format(message))
	pass

def kill_proc(browser):
	browser.close()
	os.system('kill -9 {}'.format(os.getpid()))
	pass

def refresh_page(browser, link):
	browser.get(link)
	time.sleep(3)
	pass

def auth_likeinsta(browser, username, password):
	'''
	@brief: function to auth on likeinsta.ru

		@browser: 	actual browser object
		@username:	username to set
		@password:	password to set (plain text, no md5)
	'''
	browser.get(constant.LIKEINSTA_URL_AUTH)
	time.sleep(.8)

	log = browser.find_elements_by_id('User_loginLogin')
	try:
		log[0].send_keys(username)
		time.sleep(.2)
	except IndexError:
		error_report("{}Can't get login textarea".format("[LIKEINSTA]"))
		kill_proc(browser)
		return 

	passw = browser.find_elements_by_id('User_passwordLogin')
	try:
		passw[0].send_keys(password)
		time.sleep(.2)
	except IndexError:
		error_report("{}Can't get password textarea".format("[BOSSLIKE]"))
		kill_proc(browser)
		return 
	
	btn = browser.find_elements_by_name('submitLogin')
	try:
		btn[0].click()
		time.sleep(.2)
	except IndexError:
		error_report("{}Can't get submit button".format("[BOSSLIKE]"))
		kill_proc(browser)
		return 
	pass


def auth_instagram(browser, username, password):
	'''
	@brief: function to auth on instagram.com

		@browser: 	actual browser object
		@username:	username to set
		@password:	password to set (plain text, no md5)
	'''
	browser.get(constant.INSTAGRAM_URL_AUTH)
	time.sleep(.8)
	
	log = browser.find_elements_by_xpath('//input[@name="username"]')
	try:
		log[0].send_keys(username)
		time.sleep(.8)
	except IndexError:
		error_report("{}Can't get login textarea".format("[INSTAGRAM]"))
		kill_proc(browser)
		return 

	passw = browser.find_elements_by_xpath('//input[@name="password"]')
	try:
		passw[0].send_keys(password)
		time.sleep(3)
	except IndexError:
		error_report("{}Can't get password textarea".format("[INSTAGRAM]"))
		kill_proc(browser)
		return 

	enter = browser.find_elements_by_xpath('//button')
	try:
		enter[1].click()
		time.sleep(4)
	except IndexError:
		error_report("{}Can't get submit button".format("[INSTAGRAM]"))
		kill_proc(browser)
		return 
	
	print('{} successfull auth'.format('[INSTAGRAM]'))
	pass

if __name__ == '__main__':
	#driver start
	opts = Options()
	opts.headless = True if '-s' in sys.argv else False
	opts.add_argument("user-agent={}".format(constant.DRIVER_USER_AGENT))
	browser = webdriver.Chrome(constant.DRIVER_EXEC_PATH, options=opts)

	#auth bosslike + instagram
	likeinsta_uname, likeinsta_passw = read_user_data(browser, constant.LIKEINSTA_UDATA_PATH)
	auth_likeinsta(browser, likeinsta_uname, likeinsta_passw)

	insta_uname, insta_passw = read_user_data(browser, constant.INSTAGRAM_UDATA_PATH)
	auth_instagram(browser, insta_uname, insta_passw)
	
	#go to likeinsta
	browser.get(constant.LIKEINSTA_URL_SUBS)
	main_window = browser.current_window_handle

	#statistics
	failed = 0
	refresher = 0
	prev_balance = ''
	balance = ''
	
	print('\n')

	while True:
		btns = browser.find_elements_by_class_name("do.do-task.btn.btn-sm.btn-primary.btn-block")
		if len(btns) == 0:
			refresh_page(browser, constant.LIKEINSTA_URL_SUBS)
		try:
			btns[0].click()
		except IndexError:
			continue

		time.sleep(1)
		chwd = browser.window_handles
		if len(chwd) != constant.DRIVER_MAX_WINDOW_OPENED:
			failed += 1
			if failed > constant.LIKEINSTA_REFRESH_TRESHOLD:
				browser.get(constant.LIKEINSTA_URL_SUBS)
				time.sleep(1)
				failed = 0
			continue
		else:
			time.sleep(rand_time(5,6))
			for w in chwd:
				if w!=main_window:
					browser.switch_to.window(w)
			subscribe_btn = browser.find_elements_by_xpath('//button[text()[contains(.,"Подписаться")]]')
			if len(subscribe_btn):
				subscribe_btn[0].click()
				time.sleep(rand_time(0,1))
				browser.close()
				time.sleep(rand_time(0,1))
	
			else:
				browser.close()
				time.sleep(1)
			browser.switch_to.window(main_window)
			btns = browser.find_elements_by_class_name("do.btn.btn-sm.btn-primary.btn-block.btn-success.check-task")
			curr_btn = None
			try:
				curr_btn = btns.pop(0)
			except IndexError:
				pass
			try:
				curr_btn.click()
			except selenium.common.exceptions.ElementClickInterceptedException:
				pass

			time.sleep(1)
		#each cycle print data
		print("{} ---- {}".format(str(datetime.datetime.now().time()).split('.')[0], get_user_balance(browser)))

