---- weather.waqi -------------------------------------------------

$.widget("sv.weather_waqi", $.sv.widget, {

	initSelector: '[data-widget="weather.waqi"]',

	options: {
	},
	
	_create: function() {
		this._super();
		this.element.cycle();
	},

	_update: function(response) {
		var names = {
			pm25: "PM<sub>2.5</sub>",
			pm10: "PM<sub>10</sub> [µg/m³]",
			o3: "Ozon [µg/m³]",
			no2: "Stickstoffdioxid [µg/m³]",
			no: "Stickstoffoxid [µg/m³]",
			so2: "Schwefeldioxid [µg/m³]",
			co2: "Kohlenstoffdioxid",
			t: "Temperatur [°C]",
			w: "Wind [m/s]",
			wg: "Windgeschwindigkeit [m/s]",
			r: "Rain (precipitation) [mm]",
			h: "Luftfeuchtigkeit [%]",
			d: "Taupunkt",
			p: "Luftdruck [hPa]",
			city: "Datenaufnahme",
			aqi: "Luftqualität [aqi]"
		}
		var aqi_spectrum = [
			{a:0,  b:"#cccccc",f:"#ffffff"},
			{a:50, b:"#009966",f:"#ffffff"},
			{a:100,b:"#ffde33",f:"#000000"},
			{a:150,b:"#ff9933",f:"#000000"},
			{a:200,b:"#cc0033",f:"#ffffff"},
			{a:300,b:"#660099",f:"#ffffff"},
			{a:500,b:"#7e0023",f:"#ffffff"}
			];
		var all_spectrum = [
			{a:0,b:"#059a65", f:'#FFFFFF'},
			{a:25,b:"#00787e", f:'#FFFFFF'},
			{a:50,b:"#85bd4b", f:'#000000'},
			{a:75,b:"#ffdd33", f:'#000000'},
			{a:100,b:"#ffba33", f:'#000000'},
			{a:125,b:"#fe9633", f:'#000000'},
			{a:150,b:"#e44933", f:'#FFFFFF'},
			{a:175,b:"#ca0035", f:'#FFFFFF'},
			{a:200,b:"#970068", f:'#FFFFFF'},
			{a:300,b:"#78003f", f:'#FFFFFF'},
			{a:400,b:"#4e0016", f:'#FFFFFF'},
			];
		var items = String(this.options.item).explode();
		console.log(items, "response0", response[0]);
		//$('.waqi-table').append("<h2>Luftqualität</h2>");
		var tr = "<table style=width:100%;><tr>"
		var font_color;
		var bg_color;
		//werte aus datenarray durchgehen
		for (var specie in response[0]) {
			console.log(specie, response[0][specie]);
			var value = response[0][specie];
			var i = 0;
			//bei  api  andere scalala laden
			console.log(specie);
			if (specie == 'aqi' ){
				spectrum = aqi_spectrum;				
			}else{
				spectrum = all_spectrum;
			}
			
			//wert mit skala vergleichen und anschließend felder einfärben
			for (i=0;i<spectrum.length-2;i++) {
				if (specie == 'city'){
					font_color = '#FFFFFF';
					bg_color = '';
					break;
					
				}
				font_color = spectrum[i]['f'];
				bg_color = spectrum[i]['b'];
				console.log("spectrum val", spectrum[i]);
				if (value=="-"||value<=spectrum[i].a){
					break;
				}
			};	
			
			
			var name = names[specie];
			tr+="<td style=min-width:30px;font-size:120%; text-align: left;>"+name+"</td><td style=color:"+font_color+";background-color:"+bg_color+";min-width:30px;font-size:120%;>"+response[0][specie]+"</td></tr>";
			
		}
		tr+="</table>";
		$('.waqi-table').html(tr);

		
		
	},
	
	
	_repeat: function() {

	},

	_events: {
	}

});
