
let topic = "{{topics_details}}";
debugger
const topics_details = JSON.parse(topic.replace(/&#x27;/gi, '"'));

data = [{
type: 'scatterpolar',
r: Object.values(topics_details),
theta: Object.keys(topics_details),
fill: 'toself'
}];

layout = {
polar: {
    radialaxis: {
    visible: true,
    range: [0, 5]
    }
},
showlegend: false
};

Plotly.plot(document.getElementById('radar'), data, layout);

