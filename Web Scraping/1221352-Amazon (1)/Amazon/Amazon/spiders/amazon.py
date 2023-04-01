# -*- coding: utf-8 -*-
import scrapy
from scrapy import FormRequest
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from Amazon import settings
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
import csv


class AmazonSpider(scrapy.Spider):
	name = "amazon"
	allowed_domains = 'http://www.amazon.in/'
	start_urls = [
			# "https://www.amazon.in/gp/offer-listing/B0154B5PAY/ref=dp_olp_new?ie=UTF8&condition=new"
			# "https://www.amazon.in/Forever-Impressive-Straight-Ceramic-Straightener/dp/B01N6IJ3DA/ref=sr_1_22?s=hpc&ie=UTF8&qid=1505716962&sr=1-22&keywords=Hair+brush",
			# "https://www.amazon.in/Littly-Contemporary-Foldable-Mattress-Mosquito/dp/B00XF70POG/ref=sr_1_4?s=baby&ie=UTF8&qid=1505716072&sr=1-4&keywords=baby"
			"https://www.amazon.in/s/ref=nb_sb_noss?url=search-alias%3Dbaby&field-keywords=baby&rh=n%3A1571274031%2Ck%3Ababy",
			# "https://www.amazon.in/gp/search/ref=sr_nr_n_4?fst=as%3Aoff&rh=n%3A1571274031%2Cn%3A1953144031%2Ck%3Ababy&keywords=baby&ie=UTF8&qid=1505553883&rnid=1571275031",
			# "https://www.amazon.in/s/ref=nb_sb_noss_1?url=search-alias%3Daps&field-keywords=recorder&rh=i%3Aaps%2Ck%3Arecorder",
			# "https://www.amazon.in/s?marketplaceID=A21TJRUUN4KGV&me=A29KCN6W7ABXOE&merchant=A29KCN6W7ABXOE&redirect=true"
			]
			
	download_delay = 1.0
	
	CSV_TITLE = [
				'Link', 'Best Seller Rank', 'Total_Sellers or Offers', 'Buy Box Price', 'FBA', 'Sellers',
				'Brand', 'ASIN', 'Title', 'No of reviews', 'Weight and Dimensions', 'Seller Prices', 'Page No'
			]

	def __init__(self):
		dispatcher.connect(self.spider_closed, signals.spider_closed)
		self.csv_file = open('RESULT.csv', 'wb')
		self.csv_wr = csv.writer(self.csv_file, quoting=csv.QUOTE_ALL)
		self.csv_wr.writerow(self.CSV_TITLE)

	def spider_closed(self, spider):
		self.csv_file.close()
		
		
	def parse(self, response):
		for i in range(3,5):
			yield scrapy.FormRequest.from_response(
							response,
							formdata={
								'Cookie':'x-wl-uid',
								'page':str(i)
								},
								callback=self.parse_links, dont_filter=True
				)
			
	def parse_links(self, response):
		Page_No = response.xpath('//*[@id="pagn"]/span[@class="pagnCur"]/text()').extract_first()
		for url in response.xpath('//li[starts-with(@id,"result_")]/div/div[2]/div/div/a/@href').extract():
			rq = scrapy.Request(response.urljoin(url), callback=self.parse_item, dont_filter=True)
			rq.meta['Page_No'] = Page_No
			yield rq
	
	
	
	def parse_item(self, response):
		Page_No = response.meta['Page_No']
		for sel in response.xpath('//div[@id="dp-container"]'):
			Title = sel.xpath('//*[@id="productTitle"]/text()').extract()
			Title = str(Title).replace("[u",'').replace(",",'').replace("'",'').replace("]",' ').replace('\\n','').replace('"','').replace('                                                                 ', '').replace('                                                                                                                    ','').lstrip()
			Brand = sel.xpath('//*[@id="brand"]/text()').extract()
			Brand = str(Brand).replace("[u",'').replace("[",'').replace(",",'').replace("'",'').replace("]",' ').replace('\\n','').replace('"','').replace('                                                                 ', '').replace('                                                                                                                    ','').lstrip()
			Best_Seller_Rank = sel.xpath('//*[@id="SalesRank"]/td[2]/text()[1] | //*[@id="SalesRank"]/text()').extract()
			Best_Seller_Rank = str(Best_Seller_Rank).encode('utf-8').replace('\\xa0\\xa0','').replace("[u",'').replace(",",'').replace("u'",'').replace("]",' ').replace('"','').replace("(",'').replace('\\n','').replace(")",'').replace("'",'').lstrip()
			# Total_Sellers_or_Offers = sel.xpath('//*[@id="olp_feature_div"]/div/span/a/text()').re(r'(\d+)\s')
			# Total_Sellers_or_Offers = str(Total_Sellers_or_Offers).replace("[",'').replace(",",'').replace("'",'').replace("u",'').replace("]",' ').replace(' ','')
			Buy_Box_Price = sel.xpath('//span[@id="priceblock_ourprice"]//text() | //span[@id="priceblock_saleprice"]//text() | //span[@id="priceblock_dealprice"]//text() | //*[@id="unqualifiedBuyBox"]/div/div[1]/span/text()').extract()
			Buy_Box_Price = str(Buy_Box_Price).decode('utf-8').replace("[",'').replace(",",'').replace("'",'').replace("u",'').replace("]",' ').replace(' ','').replace('\\xa0\\xa0','')
			Weight = sel.xpath('//*[@id="prodDetails"]/div/div[1]/div/div[2]/div/div/table//tr[@class="size-weight"] | //*[@id="productDetailsTable"]//tr/td/div/ul/li[1] | //*[@id="detail_bullets_id"]/table//tr/td/div/ul/li[1]').re(r'<tr class="size-weight"><td class="label">Item Weight</td><td class="value">(.*)</td></tr>|<li><b>\n    Item Weight: \n    </b>\n    (.*)\n    </li>')
			Dimensions = sel.xpath('//*[@id="prodDetails"]/div/div[1]/div[1]/div[2]/div/div/table//tr[@class="size-weight"]').re(r'<tr class="size-weight"><td class="label">Product Dimensions</td><td class="value">(.*)</td></tr>')
			Weight_and_Dimensions = str(Weight).replace("[",'').replace(",",'').replace("'",'').replace("u",'').replace("]",' ') + ' / ' + str(Dimensions).replace("[",'').replace("'",'').replace("u",'').replace("]",' ').replace(",",'')
			if "Fulfilled by Amazon" in response.body:
				FBA = "YES"
			else:
				FBA = "NO"
			No_of_reviews = sel.xpath('//*[@id="acrCustomerReviewText"]/text()').re(r'(\d+)\s*customer')
			No_of_reviews = str(No_of_reviews).replace("[",'').replace(",",'').replace("'",'').replace("u",'').replace("]",' ').replace(' ','')
			ASIN = sel.xpath('//*[@id="prodDetails"]/div/div[2]/div[1]/div[2]/div/div/table//tr[1] | //*[@id="productDetailsTable"]//tr/td/div/ul/li | //*[@id="detail_bullets_id"]/table//tr/td/div/ul/li').re(r'<tr><td class="label">ASIN\:*</td><td class="value">(.*)</td></tr>|<li><b>ASIN\:*\s*</b>(.*)</li>')
			ASIN = str(ASIN).replace("[",'').replace(",",'').replace("'",'').replace("u",'').replace("]",' ').replace(' ','')
			Link = "http://www.amazon.in/dp/"
			Link = Link + str(ASIN).replace("[",'').replace(",",'').replace("'",'').replace("u",'').replace("]",' ').replace(' ','')
			offer_link = "https://www.amazon.in/gp/offer-listing/"
			asin_no = ASIN
			path = "/ref=dp_olp_new?ie=UTF8&condition=new"
			offer_page_link = offer_link + asin_no + path
			rq = scrapy.Request(response.urljoin(offer_page_link), callback=self.parse_offers, dont_filter=True)
			rq.meta['Page_No'] = Page_No
			rq.meta['Title'] = Title
			rq.meta['Brand'] = Brand
			rq.meta['Best_Seller_Rank'] = Best_Seller_Rank
			# rq.meta['Total_Sellers_or_Offers'] = Total_Sellers_or_Offers
			rq.meta['Buy_Box_Price'] = Buy_Box_Price
			rq.meta['Weight_and_Dimensions'] = Weight_and_Dimensions
			rq.meta['FBA'] = FBA
			rq.meta['No_of_reviews'] = No_of_reviews
			rq.meta['ASIN'] = ASIN
			rq.meta['Link'] = Link
			yield rq
		
	def parse_offers(self, response):
		Total_Sellers_or_Offers = len(response.xpath('//span[@class="a-size-large a-color-price olpOfferPrice a-text-bold"]').extract())
		seller_prices = []
		seller_price = ''
		sellers = " # ".join(response.xpath('//*[@id="olpTabContent"]/div/div[2]/div[@class="a-row a-spacing-mini olpOffer"]/div[3]/h3/span/a/text()').extract())
		for prices, ship in zip(response.xpath('//span[@class="a-size-large a-color-price olpOfferPrice a-text-bold"]/span[@style="text-decoration: inherit; white-space: nowrap;"]/text()').extract(), response.xpath('//span/span[@class="olpShippingPrice"]/span[@style="text-decoration: inherit; white-space: nowrap;"]/text() | //p[@class="olpShippingInfo"]/span[@class="a-color-secondary"][contains(text(), "Delivery charges")]/text() | //p[@class="olpShippingInfo"]/span[@class="a-color-secondary"]/b/text()').extract()):
			prices = str(prices).strip("'").replace(",",'')
			prices = prices[prices.find(' ') + 1:prices.find('.')]
			ship = str(ship).replace('FREE Delivery','0.0').replace('+ Delivery charges may apply','0.0').strip("'").strip(",").replace(",",'')
			ship = ship[ship.find(' ') + 1:ship.find('.')]
			price_ship = int(prices) + int(ship)
			seller_prices.append(price_ship)
			seller_price = seller_prices
			seller_price = str(seller_price).replace('[','').replace(']','').replace(', ',' # ')
		
		
		# next_page = response.xpath('//*[@id="olpTabContent"]/div/div[3]/ul/li[4]/a/@href').extract_first()
		# if next_page:
			# yield scrapy.Request(response.urljoin(next_page), dont_filter=True)
		data = [
			response.meta['Link'],
			response.meta['Best_Seller_Rank'],
			Total_Sellers_or_Offers,
			response.meta['Buy_Box_Price'],
			response.meta['FBA'],
			sellers,
			response.meta['Brand'],
			response.meta['ASIN'],
			response.meta['Title'],
			response.meta['No_of_reviews'],
			response.meta['Weight_and_Dimensions'],
			seller_price,
			response.meta['Page_No'],
			]
		self.csv_wr.writerow(data)