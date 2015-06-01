function getResults(data){
	$.ajax(
		{
			type: 'GET',
			url: data.routeUrl, 
			data: {
				"keywords": "{{ keywords }}",
				"min_price": {{ min_price }},
				"max_price": {{ max_price }}
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

						var valueString = listing.listing_origin + "," + listing.listing_id;
						var button = $("<button></button>").text("Favorite").addClass("favorite").attr("value", valueString);
						$(data.idTag).append(button);
					};
				} else {
					$(data.idTag).append($("<h1></h1>").text(data.noResultsString));
				};
			}
		}
	);
}

var etsyData = {
	routeUrl : "/search_etsy",
	idTag : "#Etsy",
	resultTitle : "Etsy Results:", 
	noResultsString : "No matching results found on Etsy"
};
var ebayData = {
	routeUrl : "/search_ebay",
	idTag : "#eBay",
	resultTitle : "eBay Results:", 
	noResultsString : "No matching results found on eBay"
};
var minfindData = {
	routeUrl : "/scrape_minfind",
	idTag : "#Minfind",
	resultTitle : "Minfind Results:", 
	noResultsString : "No matching results found on Minfind"
};

getResults(etsyData);
getResults(ebayData);
getResults(minfindData);

function addToFavorite(evt){
	if ({{ user_id }} == 0){
		alert("Please log in first!");
	} else {
		origin_id_string = $(evt.currentTarget).attr("value");
		origin_id_array = origin_id_string.split(",");
		var listing_origin = origin_id_array[0];
		var listing_id = parseInt(origin_id_array[1], 10);

		$.ajax(
			{
				type: 'GET',
				url: '/add_to_favorites',
				data: {
					"user_id": {{ user_id }},
					"listing_origin": listing_origin,
					"listing_id": listing_id
				},
				dataType: "text",
				success: function(response){
					alert(response);
				}
			}
		);

	};
};

$('.website_div').on('click', '.favorite', addToFavorite);