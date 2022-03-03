// ----- multimedia.slideshow3 ----------------------------------------------------
$.widget("sv.doorbird_history", $.sv.widget, {

	initSelector: '[data-widget="doorbird.history"]',

	options: {
		history: [],
		motion: [],
		slideTime: 2000,
		maxFiles: 10,
		lang: 'de'
	},

	_create: function () {
		this._super();
		this.element.cycle();

	},

	_update: function (response) {
		var id = this.element.attr('id');
		var slideIndex = 0;
		var image_array = [];
		var image_array_length; 
		var slideTime = 2000;
		var maxFiles = 10;
		var items = String(this.options.item).explode();
		var slideInterval;
		console.log("snapshots ",response[0] , "motion ",response[1], "doorbell",response[2]);
		var lang = {'de': ['Keine Bilder vorhanden!', '', ''], 
					'en': ['No pictures!', '', '' ]

		}
		var snapshot_items = response[0];
		var motion_items = response[1];
		var doorbell_items = response[2];

		vorladen(snapshot_items);

		//startarray
		image_array = response[0];
		var image_text = "Snapshots";
		var auto_on = false;
		var maxFiles; 
		image_array = snapshot_items;

		console.log("load Snapshot images");

		$("div#" + id + " #btnsnaphots").addClass('ui-btn-active');
		$("div#" + id + " #btnmotion").removeClass('ui-btn-active');
		$("div#" + id + " #btnhistory").removeClass('ui-btn-active');
		$("div#" + id + " .caption-container").empty().append('Snapshots');
		

		showPics(image_array, maxFiles);

		

		function picCheck(){
			if (image_array.length == 0){
				$("div#" + id + " .image-container").html('<div class="doorbird-image" style="display:block;margin: 0 auto;  height: 8em;top: 50%;bottom: 50%;">Keine Bilder vorhanden! </div>');
				$("div#" + id + " .btnprev").css('display', 'none');
				$("div#" + id + " .btnnext").css('display', 'none');
			}else{
				$("div#" + id + " .btnprev").css('display', 'block');
				$("div#" + id + " .btnnext").css('display', 'block');
			}
		};

		//derarray durch, erzeugt Bilder und Miniaturbilder
		//ebenso das Bild mit dem  aktuellen index
		function showPics(image_array, maxFiles) {
			if (Array.isArray(image_array) && typeof image_array[0] !== 'undefined' && typeof image_array !== 'undefined') {
				image_array_length = image_array.length;
				var times = [];
				var fuellwort = "";

				for (var i = 0; i < maxFiles; i++) {
					//save a date for each image

					let timestamp = image_array[i].substring(image_array[i].lastIndexOf("/") + 1, image_array[i].lastIndexOf("."));
					let datetime = new Date(timestamp * 1000);
					let offs = new Date().getTimezoneOffset();
					let timeWithOffset = new Date(datetime - offs); 
					console.log(datetime, "local time", timeWithOffset.toUTCString())
					if (isNaN(datetime.getTime())){
						times[i] = '';
					}else{
						times[i] = (timeWithOffset.getUTCDate())+ '.'+ (timeWithOffset.getUTCMonth()+1)+'.'+timeWithOffset.getUTCFullYear() + '  '+timeWithOffset.getUTCHours()+ ':'+ timeWithOffset.getUTCMinutes()+ 'Uhr ';
						fuellwort = " vom ";

					}
					var i_display = i + 1;

					var rev_id = maxFiles;

					//add all images from array to the image-container
					$("div#" + id + " .image-container").append('<div class="doorbird-image" style=""><img data-id ="' + i+ '"style="width:100%;" src="' + image_array[i] + '"/> <div class="numbertext ">' + i_display + '/' + (maxFiles) + ' ' + fuellwort + times[i] + '</div> </div>');

					//add miniature images 
					if(isMobile()){
						$("div#" + id + " .rows").append('<div class="column" > <img alt="'+times[i]+'" class="miniatur cursor" src="' + image_array[i] + '"style="width:100%" data-id = "' + i + '" onclick="#"></div>');
					}else{
						$("div#" + id + " .rows").append('<div class="column" > <div class = "doorbird-column-text">' + times[i] + '</div><img alt="'+times[i]+'" class="miniatur cursor" src="' + image_array[i] + '"style="width:100%" data-id = "' + i + '" onclick="#"></div>');
					}
				};
				bindActions();
				showSlides(0);
			}else{
				picCheck()
			}
			
		};

		//Zeigt nur bild mit übergebener id an 
		function showSlides(n) {
			var i;
			var slides = document.getElementsByClassName("doorbird-image");
			var dots = document.getElementsByClassName("miniatur");
			var captionText = document.getElementById("doorbird-caption");
		
			console.log("Anzahl bilder", slides.length);
			//alle Bilder deaktivieren
			for (i = 0; i < slides.length; i++) {
				slides[i].style.display = "none";
				//console.log("Slides", slides[i]);
			};
			//alle voschaubilder deaktivieren
			for (i = 0; i < dots.length; i++) {
				dots[i].className = dots[i].className.replace(" active", "");
			};
			//console.log(slides, "zeige", n );
			//aktuelles BIld anzeigen, und vorschaubild aktivieren
			if (slides.length > 0 && n<slides.length) {
				slides[n].style.display = "block";
				dots[n].className += " active";
				//captionText.innerHTML = dots[slideIndex].alt;

			};

			//return slideIndex;
		};

		// Vorladen der Miniaturbilder
		function vorladen(Liste) {
			var Bilder = new Array(Liste.length);
			for (i = 0; i < Liste.length; i++) {
				Bilder[i] = new Image();
				Bilder[i].src = Liste[i];
			}
			return Bilder;
		}

		// Miniaturbilder hover
		$("div#" + id + " .rows").hover(function () {
			console.log("Image hover");
			console.log($("div#" + id + " .rows img").attr('alt'));
		
		});
		//Button events
		//Buttons on the images
		$("div#" + id + " .btnprev").click(function () {
			console.log("vorher" + slideIndex);
			if (slideIndex == 0){//überlauf, von hinten anfangen
				slideIndex = maxFiles-1;
			} else if (slideIndex > 0) {
				
				slideIndex -= 1;
			}
			console.log("prev " + slideIndex);
			showSlides(slideIndex);
		});

		$("div#" + id + " .btnnext").click(function () {
			console.log("slideindex", slideIndex);
			if (slideIndex < (maxFiles-1)) {
				slideIndex += 1;
			} else if (slideIndex == (maxFiles-1)) {
				//überlauf von vorne anfangen 
				slideIndex = 0;
			}
			console.log("next " + slideIndex);
			showSlides(slideIndex);
		});

		//Button under the images
		$("div#" + id + " #btnpause").click(function () {
			auto_on = false;
			$("div#" + id + " #btnplay").removeClass('ui-btn-active');
			$("div#" + id + " #btnpause").addClass('ui-btn-active');
			console.log("pause" + slideIndex);
			clearInterval(slideInterval);
		});


		$("div#" + id + " #btnplay").click(function () {
			auto_on = true;
			console.log("play" + slideIndex);
			if(image_array.length-1 > maxFiles){
				maxFiles = maxFiles;
			}else{
				maxFiles = image_array.length-1;
			}
			$("div#" + id + " #btnpause").removeClass('ui-btn-active');
			$("div#" + id + " #btnplay").addClass('ui-btn-active');
			slideInterval = setInterval(function () {
				if (slideIndex < image_array.length-1) {
					slideIndex += 1;
				} else if (slideIndex >= image_array.length-1) {
					//überlauf von vorne anfangen 
					slideIndex = 0;
				}
				showSlides(slideIndex);
			}, 2000);
		});

		$("div#" + id + " #btnsnapshots").click(function () {
			image_array = snapshot_items;
			//image_array = response[1];
			console.log("load Snapshot images");

			$("div#" + id + " .rows").empty();
			$("div#" + id + " .image-container").empty();
			$("div#" + id + " #btnsnaphots").addClass('ui-btn-active');
			$("div#" + id + " #btnmotion").removeClass('ui-btn-active');
			$("div#" + id + " #btnhistory").removeClass('ui-btn-active');
			$("div#" + id + " .caption-container").empty().append('Snapshots');
			picCheck();
			showPics(image_array, 10);
		});
		$("div#" + id + " #btnhistory").click(function () {
			image_array = doorbell_items;
			//image_array = response[1];
			console.log("load History images");

			$("div#" + id + " .rows").empty();
			$("div#" + id + " .image-container").empty();
			$("div#" + id + " #btnhistory").addClass('ui-btn-active');
			$("div#" + id + " #btnmotion").removeClass('ui-btn-active');
			$("div#" + id + " .caption-container").empty().append('History');
			picCheck();
			showPics(image_array, 10);
		});

		$("div#" + id + " #btnmotion").click(function (args) {
			motion = true;
			//image_array = response[2];
			console.log("Motion");
			image_array = motion_items;
			//image_array = response[1];
			$("div#" + id + " .rows").empty();
			$("div#" + id + " .image-container").empty();
			console.log("load Motion images");
			$("div#" + id + " #btnhistory").removeClass('ui-btn-active');
			$("div#" + id + " #btnmotion").addClass('ui-btn-active');
			$("div#" + id + " .caption-container").empty().append('Bewegungsmelder');
			picCheck();
			showPics(image_array, 10);
		});
		
		function isMobile(){
			return navigator.userAgent.match(/(iPhone|iPod|iPad|blackberry|android|Kindle|htc|lg|midp|mmp|mobile|nokia|opera mini|palm|pocket|psp|sgh|smartphone|symbian|treo mini|Playstation Portable|SonyEricsson|Samsung|MobileExplorer|PalmSource|Benq|Windows Phone|Windows Mobile|IEMobile|Windows CE|Nintendo Wii)/i);
		}

		function bindActions() {
			$(".cursor").on("click",function () {
				//console.log("Click vorschaubild ", cursor);
				let id = $( this ).attr("data-id");
				console.log("Click vorschaubild ", id);
				showSlides(id);
			});
		}
	},


	_repeat: function () {

	},

	_events: {
	}

});


