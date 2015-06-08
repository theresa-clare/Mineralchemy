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
					$(data.idTag).append($("<h1></h1>").text(data.resultTitle));

					for (i = 0; i < response.numResults; i++) {
						var listing = response.listingsFound[i];
						var title = $("<p></p>").text(listing.title);
						var price = $("<p></p>").text(listing.price);
						var link = $("<a></a>").attr("href", listing.url).text("URL");

						if (listing.description != null) {
							description = $("<p></p>").text(listing.description);
						};
						$(data.idTag).append(title, price, description, link);

						for (j = 0; j < listing.image_urls.length; j++) {
							image = $("<img>").attr("src", listing.image_urls[j]);
							$(data.idTag).append(image);
						};

						var button = $("<button></button>").text("Favorite").addClass("favorite").attr("value", JSON.stringify(listing));
						$(data.idTag).append(button);
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
				resultTitle : "Etsy Results:", 
				noResultsString : "No matching results found on Etsy"
				},
	ebayData : {
				routeUrl : "/search_ebay",
				idTag : "#eBay",
				resultTitle : "eBay Results:", 
				noResultsString : "No matching results found on eBay"
				},
	minfindData : {
				routeUrl : "/scrape_minfind",
				idTag : "#Minfind",
				resultTitle : "Minfind Results:", 
				noResultsString : "No matching results found on Minfind"
				}
};

$(document).ready(function() {
	getResults(searchData.etsyData);
	getResults(searchData.ebayData);
	getResults(searchData.minfindData);
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
				dataType: 'text',
				success: function(response) {
					alert(response);
				}
			}
		);
	};
};

$('.website_div').on('click', '.favorite', addToFavorite);