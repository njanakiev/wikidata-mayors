d3.json('arcs.json').then(function(data){
	var arcs = [];
	var scatter = [];

	data.forEach(function(d){
		if(d.distance > 1000){
			arcs.push(d);
		}else{
			scatter.push({
				'positon': d.target,
				'color': d.color
			});
		}
	});

    new deck.DeckGL({
	    container: 'container',
	    mapboxAccessToken: '',
	    mapStyle: 'https://tileserver.janakiev.com/styles/positron/style.json',
	    longitude: 8.682127,
	    latitude: 50.110924,
	    zoom: 3,
		maxZoom: 15,
	    pitch: 30,
	    bearing: 10,
	    map: mapboxgl,
	    layers: [
	        new deck.ScatterplotLayer({
		        id: 'scatter-plot',
		        data: scatter,
		        radiusMinPixels: 1,
		        getPosition: d => d.positon,
		        getColor: d => d.color,
		        getRadius: d => 3000,
		        opacity: 0.7
	        }),
	        new deck.ArcLayer({
				id: 'arc',
				data: arcs,
				getSourcePosition: d => d.source,
				getTargetPosition: d => d.target,
				getSourceColor: d => [150, 150, 150],
				getTargetColor: d => d.color,
				strokeWidth: 3
			})
      	]
    });
});
