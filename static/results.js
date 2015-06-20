function getResults(data){
	$.ajax(
		{
			type: 'GET',
			url: data.routeUrl, 
			data: {
				"keywords": keywords,
				"min_price": min_price,
				"max_price": max_price,
			},
			dataType: 'JSON',
			success: function(response){

				var count = parseInt($('#count').text().trim(), 10);
				var new_count = count + response.numResults;
				$('#count').text(new_count);

				if (response.numResults > 0) {
					var resultTitle = $("<h2></h2>").text(data.resultTitle);
					$(resultTitle).attr("class", "subtitle thumbnail-darker result-title");
					$(data.idTag + "Results").append(resultTitle);

					for (i = 0; i < response.numResults; i++) {
						// Create main div for each listing
						var listingDiv = $("<div></div>").attr("class", "listing-div thumbnail-darker");
						var listing = response.listingsFound[i];

						// Create two separate divs for text and image in listing
						var listingTextDiv = $("<div></div>").attr("class", "column listing-column");
						var listingImgDiv = $("<div></div>").attr("class", "column listing-column");

						// Create row to nest text and image divs
						var listingRow = $("<div></div>").attr("class", "container row listing-row");

						// Create linked title, price, favorite button, and text notification
						var link = $("<a></a>").attr("href", listing.url);
						var title = $("<h6></h6>").text(listing.title).attr("class", "result-title-price");
						$(link).append(title);

						var price = $("<h6></h6>").text("$" + listing.price).attr("class", "result-title-price");
						var button = $("<button></button>").text("Favorite").addClass("favorite btn btn-default").attr("value", JSON.stringify(listing));
						var success_text = $("<p></p>").attr("id", "ID" + listing.listing_id).attr("class", "listing-p-favorite");

						if (listing.description != null) {
							description = $("<p></p>").text(listing.description).addClass("listing-p");
						};

						// Add in all created elements to listing div
						// $(listingDiv).append(link, price, button, success_text, description);
						$(listingTextDiv).append(link, price, button, success_text, description);

						// Get first image and add it to img div
						image = $("<img>").attr("src", listing.image_urls[0]).attr("class", "listing-img");
						image_div = $("<div></div>").append(image);
						$(listingImgDiv).append(image_div);

						// Add text and img div to listing row
						$(listingRow).append(listingTextDiv);
						$(listingRow).append(listingImgDiv);

						// Add listing row to main listing div
						$(listingDiv).append(listingRow)

						// Add the main listing div to the overall origin section
						$(data.idTag).append(listingDiv);

						// Add divider to main listing div
						$(data.idTag).append("<hr>");
					};
				} else {
					$(data.idTag).append($("<h1></h1>").text(data.noResultsString));
				};
			}
		}
	);
}

var searchData = {
	etsyData : {
				routeUrl : "/search_etsy",
				idTag : "#Etsy",
				resultTitle : "Etsy Results", 
				noResultsString : "No matching results found on Etsy"
				},
	ebayData : {
				routeUrl : "/search_ebay",
				idTag : "#eBay",
				resultTitle : "eBay Results", 
				noResultsString : "No matching results found on eBay"
				},
	minfindData : {
				routeUrl : "/scrape_minfind",
				idTag : "#Minfind",
				resultTitle : "Minfind Results", 
				noResultsString : "No matching results found on Minfind"
				}
};


$(document).ready(function() {
	getResults(searchData.etsyData);
	getResults(searchData.ebayData);
	getResults(searchData.minfindData);

	$(document).ajaxStart(function() {
		$('#loading').css("display", "block");
	});

	$(document).ajaxComplete(function() {
		$('#loading').css("display", "none");
		$('#search-results').css("display", "block");
	});
});

function addToFavorite(evt){
	if (user_id == 0){
		alert("Please log in first!");
	} else {
		var listing = JSON.parse($(evt.currentTarget).attr("value"));
		listing.user_id = user_id;
		listing.primary_image = listing.image_urls[0];

		$.ajax(
			{
				type: 'GET',
				url: '/add_to_favorites',
				data: listing,
				dataType: 'JSON',
				success: function(response) {
					$('#ID' + response.listing_id).text(response.success_text);
				}
			}
		);
	};
};

$('#all-results').on('click', '.favorite', addToFavorite);
