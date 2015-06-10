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
						var listingDiv = $("<div></div>").attr("class", "listing-div thumbnail-darker");
						var listing = response.listingsFound[i];

						var link = $("<a></a>").attr("href", listing.url);
						var title = $("<h6></h6>").text(listing.title).attr("class", "result-title-price");
						$(link).append(title);

						var price = $("<h6></h6>").text("$" + listing.price).attr("class", "result-title-price");
						var button = $("<a></a>").text("Favorite").addClass("favorite btn btn-default").attr("value", JSON.stringify(listing));

						if (listing.description != null) {
							description = $("<p></p>").text(listing.description).addClass("listing-p");
						};
						$(listingDiv).append(link, price, button, description);

						// for (j = 0; j < listing.image_urls.length; j++) {
						// 	image = $("<img>").attr("src", listing.image_urls[j]);
						// 	$(data.idTag).append(image);
						// };
						image = $("<img>").attr("src", listing.image_urls[0]);
						image_div = $("<div></div>").append(image);
						$(listingDiv).append(image_div);

						$(data.idTag).append(listingDiv);
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

$(window).load(function(){
	$('#loading').hide();
});