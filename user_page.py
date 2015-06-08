def get_favorites(results):
	etsy_listings = []
	ebay_listings = []
	minfind_listings = []

	for result in results:
		listing = {
				"title": result[4],
				"price": result[5],
				"description": result[6],
				"url": result[7],
				"primary_image": result[8]
				}
		if result[2] == "etsy":
			etsy_listings.append(listing)
		elif result[0] == "ebay":
			ebay_listings.append(listing)
		else:
			minfind_listings.append(listing)
	return etsy_listings, ebay_listings, minfind_listings