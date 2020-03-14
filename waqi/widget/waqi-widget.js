// ----- weather.waqi -------------------------------------------------

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
			pm25: "PM<sub>2.5</sub> [µg/m³]",
			pm10: "PM<sub>10</sub> [µg/m³]",
			o3: "Ozon [µg/m³]",
			no2: "Stickstoffdioxid [µg/m³]",
			no: "Stickstoffoxid [µg/m³]",
			so2: "Schwefeldioxid [µg/m³]",
			co2: "Kohlenstoffdioxid [µg/m³]",
			t: "Temperatur [°C]",
			w: "Windgeschwindigkeit [m/s]",
			wg: "Globalstrahlung [mW/cm²]",
			r: "Rain (precipitation) [mm]",
			h: "Luftfeuchtigkeit [%]",
			d: "Taupunkt",
			p: "Luftdruck [hPa]",
			city: "Datenquelle",
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
		//var tr = "<table style=width:100%;><tr>"
		var style = 'app';
		var tr = '<div style="width:100%;">';
		var font_color;
		var bg_color;
		//werte aus datenarray durchgehen
		for (var specie in response[0]) {
			console.log(specie, response[0][specie]);
			if (specie.includes('alarm')){
				break;
			} 
			var value = response[0][specie];
			var i = 0;
			if (specie == 'aqi' ){
				spectrum = aqi_spectrum;				
			}else{
				spectrum = all_spectrum;
			}
			
			//wert mit skala vergleichen und anschließend felder einfärben
			for (i=0;i<spectrum.length-2;i++) {
				if (specie == 'pm25' || specie == 'pm10' || specie == 'o3' || specie == 'no2' || specie == 'so2' || specie == 'co'|| specie == 'aqi' ){
					font_color = spectrum[i]['f'];
					bg_color = spectrum[i]['b'];
					
					if (value=="-"||value<=spectrum[i].a){
						break;
					};
				}else if (specie =='t'){
					if(spectrum[i] >= 25){
						bg_color = '#ca0035';
					}else if (spectrum[i] < 4){
						bg_color = '#1877f2';
					}
				}else if (specie =='w'){
					if(spectrum[i] >= 10.8){
						bg_color = '#fe9633';
					}else if (spectrum[i] >=20,8){
						bg_color = '#00787e';
					}else{
						bg_color = '#ca0035';
					}
				}else{
					font_color = '#FFFFFF';
					bg_color = '';
					break;
				};
				
			};	
			
			
			var name = names[specie];
			//visualisation app style
			if(style == 'app'){
				if (specie != 'city'){
					tr+="<span style='box-sizing:border-box; border:2px solid #444444; border-radius:6%; float:left; padding:1%; margin:1%; min-width:31%; height: 50%;text-align: center; color:"+font_color+";background-color:"+bg_color+"'>";
					tr+="<span style='font-size:150%;'>"+response[0][specie]+"</span></br>";
					tr+="<span style='font-size:70%;'>"+name+"</span> ";
					tr+="</span></span>";
				}else{
					
					tr+="<span style='box-sizing:border-box; border:2px solid #444444;float:left;padding:1%; margin:1%;border-radius:6%; min-width:31%; height: 100%;text-align: center; color:"+font_color+";background-color:"+bg_color+"'>";
					tr+="<span style='font-size:80%;'>"+response[0][specie]+"</span></br>";
					tr+="</span></span>";
				}
			//visualisation table
			}else{
				if (specie == 'city'){
					tr+="<span style='float:left; width:80%;height: 30px;font-size:120%;text-align: left;'>"+name+" - "+response[0][specie]+"</span>";
					
				}else{
					//tr+="<td style=min-width:30px;font-size:120%; text-align: left;>"+name+"</td><td style=color:"+font_color+";background-color:"+bg_color+";min-width:30px;font-size:100%;>"+response[0][specie]+"</td></tr>";
					tr+="<span style='float:left; width:80%;height: 30px;font-size:120%; text-align: left;color:"+font_color+";background-color:"+bg_color+";'>"+name+"</span><span style='height: 30px;float:right; text-align: right; color:"+font_color+";background-color:"+bg_color+";width:20%;font-size:120%;'>"+response[0][specie]+"</span></br>";
				}
			}
		}
		//tr+="</table>";
		tr+="</div>";
		$('.waqi-table').html(tr);

		
		
	},
	
	
	_repeat: function() {

	},

	_events: {
	}

});
