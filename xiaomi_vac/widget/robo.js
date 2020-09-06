/// ----- robo.saugroboter ----------------------------------------------------
$.widget("sv.status_robvac", $.sv.widget, {

	initSelector: '[data-widget="status.robvac"]',

	options: {
	},
	
	_create: function() {
		this._super();
		this.element.cycle();
	},

	_update: function(response) {
		var items = String(this.options.item).explode();
		//console.log('test_saugroboter_update');
		//console.log(items);
		//console.log(response);
		$(".vac_status").empty();
		if (response[2] == 'Charging'){
			$(".vac_status").prepend(" -+ Charging +-");
		}else if (response[2] == 'Cleaning'){
			$(".vac_status").prepend(" -+ Cleaning +-");
			$(".vac_status").prepend(" Fläche: "+ items[0] +" m² | </br> Zeit: "+ items[1] +"h");
		}else if (response[2] == 'Error'){
			$(".vac_status").prepend(" -+ ERROR +-");
			$(".vac_status").prepend(" Code: "+ items[3]);
		};
		$(".vac_status").append("</br> <hr>");
	},
	
	_repeat: function() {

	},

	_events: {
	}

});
