//Function to change image shwon in the report
 function changeImage(imgSrc) {
    document.getElementById("chartImage").src = imgSrc;
    document.getElementById("chartImage").alt = imgSrc;
}

//Function to change the JSON shown in the report
function changeJSON(jsonSrc) {
    //Hide all the elements with class="jsonBlock"
    let x = document.getElementsByClassName("jsonBlock");
    let i;
    for (i = 0; i < x.length; i++) {
        x[i].style.display = "none";
    }
    //Show the element with id="jsonSrc"
    document.getElementById(jsonSrc).style.display = "block";
}

//Function to change the JSON inside the code block
function changeJSONHidden(btn) {
    let x = document.getElementById("jsonCode");

    //Get the value of the this button
    let btnValue = btn.value;

    //Copy the text inside the element
    x.innerHTML = btnValue;
    hljs.highlightAll();
}

//Function to Create Chart for sleep data
function generateChartSleep(sleepLevels) {
    //Change double quotes to &quot; so that the JSON.parse works
    sleepLevels = JSON.parse(JSON.stringify(sleepLevels));
    sleepLevels = JSON.parse(sleepLevels);
    //IF sleepLevels is not an array, then make it an array
    if (!Array.isArray(sleepLevels)) {
        sleepLevels = [sleepLevels];
    }
            const levels = ['DEEP', 'LIGHT', 'REM', 'AWAKE']
            const colors = ['#4B56D2', '#82C3EC', '#CF4DCE', '#F273E6']
    console.log(sleepLevels);
           // loop through the data and format the startGMT and endGMT values
            for (var i = 0; i < sleepLevels.length; i++) {
                sleepLevels[i].startGMT = moment(sleepLevels[i].startGMT).format('HH:mm');
                sleepLevels[i].endGMT = moment(sleepLevels[i].endGMT).format('HH:mm');
            }

            // then use the formatted values to create the chart
            var ctx = document.getElementById('myChart').getContext('2d');
            // destroy the previous chart if it exists
            let chartStatus = Chart.getChart("myChart"); // <canvas> id
            if (chartStatus != undefined) {
              chartStatus.destroy();
            }
            var chart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: sleepLevels.map(function(d) { return d.startGMT + ' - ' + d.endGMT; }),
                    datasets: [{
                        label: 'Activity Level',
                        //show in the y axis the levles array defined above using the activityLevel value
                        //as the index to get the correct level
                        data: sleepLevels.map(function(d) { return d.activityLevel + 1; }),
                        //Change the color of the bar based on the activity level,
                        //using the colors array defined above
                        backgroundColor: sleepLevels.map(function(d) { return colors[d.activityLevel]; }),
                        borderColor: sleepLevels.map(function(d) { return colors[d.activityLevel]; }),
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                //use the levels array defined above to show the correct level
                                //in the y axis
                                callback: function(value, index, values) {
                                    return levels[value - 1];
                                }
                            }
                        },
                    }
                }
            });
        }

//Function to Create Chart for SpO2 data
function spo2Chart(spo2List) {
            spo2List = JSON.parse(JSON.stringify(spo2List));
            spo2List = JSON.parse(spo2List);
            // loop through the data and format the epochTimestamp values
            for (var i = 0; i < spo2List.length; i++) {
                spo2List[i].epochTimestamp = moment(spo2List[i].epochTimestamp).format('HH:mm');
            }

            // then use the formatted values to create the chart
            var ctx = document.getElementById('myChart').getContext('2d');
            // destroy the previous chart if it exists
            let chartStatus = Chart.getChart("myChart"); // <canvas> id
            if (chartStatus != undefined) {
              chartStatus.destroy();
            }
            var chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: spo2List.map(function(d) { return d.epochTimestamp; }),
                    datasets: [{
                        label: 'SpO2 Reading',
                        data: spo2List.map(function(d) { return d.spo2Reading; }),
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Spo2 %',
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Time',
                    }
                }
                    }
                }
            });
}

//Function to create line chart
function createLineChart(yData, xData, time=false, type, xLabel, yLabel) {
    //remove the [] from the start and end of the string
    yData = yData.substring(1, yData.length - 1);
    xData = xData.substring(1, xData.length - 1);
  //Convert yData and xData to arrays
    yData = yData.split(",");
    xData = xData.split(",");
    if (time) {
        //Convert xData timestamps to HH:mm format
        for (var i = 0; i < xData.length; i++) {
            //convert to integer
            xData[i] = parseInt(xData[i]);
            let date = new Date(xData[i]);
            if (date.getHours() < 10) {
                if (date.getMinutes() < 10) {
                    date = "0" + date.getHours() + ":" + "0" + date.getMinutes();
                } else {
                    date = "0" + date.getHours() + ":" + date.getMinutes();
                }
            } else {
                if (date.getMinutes() < 10) {
                    date = date.getHours() + ":" + "0" + date.getMinutes();
                } else {
                    date = date.getHours() + ":" + date.getMinutes();
                }
            }
            xData[i] = date;
        }
    }
  var ctx = document.getElementById('myChart').getContext('2d');
  let chartStatus = Chart.getChart("myChart"); // <canvas> id
   if (chartStatus != undefined) {
         chartStatus.destroy();
    }

   var data = yData.map((y, i) => ({
    x: xData[i],
    y: y
  }));


  var myChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: xData,
      datasets: [
        {
          label: type,
          data: data,
          backgroundColor: 'rgba(255, 99, 132, 0.2)',
          borderColor: 'rgba(255, 99, 132, 1)',
          borderWidth: 1
        }
      ]
    },
    options: {
      scales: {
        y: {
            beginAtZero: true,
            title: {
                display: true,
                text: yLabel,
            }
        },
        x: {
            title: {
                display: true,
                text: xLabel,
            }
        }
      },
        elements: {
            point: {
                radius: 0
            }
        }
    }
  });
}

//Function to create bar chart
function createBarChart(yData, xData) {
    //remove the [] from the start and end of the string
    yData = yData.substring(1, yData.length - 1);
    xData = xData.substring(1, xData.length - 1);
  //Convert yData and xData to arrays
    yData = yData.split(",");
    xData = xData.split(",");
    //Convert xData timestamps to HH:mm format
        for (var i = 0; i < xData.length; i++) {
            //convert to integer
            xData[i] = parseInt(xData[i]);
            let date = new Date(xData[i]);
            if (date.getHours() < 10) {
                if (date.getMinutes() < 10) {
                    date = "0" + date.getHours() + ":" + "0" + date.getMinutes();
                } else {
                    date = "0" + date.getHours() + ":" + date.getMinutes();
                }
            } else {
                if (date.getMinutes() < 10) {
                    date = date.getHours() + ":" + "0" + date.getMinutes();
                } else {
                    date = date.getHours() + ":" + date.getMinutes();
                }
            }
            xData[i] = date;
        }
  var ctx = document.getElementById('myChart').getContext('2d');
  let chartStatus = Chart.getChart("myChart"); // <canvas> id
   if (chartStatus != undefined) {
         chartStatus.destroy();
    }

   var data = yData.map((y, i) => ({
    x: xData[i],
    y: y
  }));


  var myChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: xData,
      datasets: [
        {
          label: 'My Line Chart',
          data: data,
          backgroundColor: 'rgba(255, 99, 132, 0.2)',
          borderColor: 'rgba(255, 99, 132, 1)',
          borderWidth: 1
        }
      ]
    },
    options: {
      scales: {
        y : {
            beginAtZero: true,
            title: {
                display: true,
                text: 'Weight (kg)'
            }
        },
        x: {
            title: {
                display: true,
                text: 'Date'
            }
        }
      }
    }
  });
}


//Function to create pie chart
function createPieChart(values) {
    var ctx = document.getElementById('myChart').getContext('2d');
  let chartStatus = Chart.getChart("myChart"); // <canvas> id
   if (chartStatus != undefined) {
         chartStatus.destroy();
    }
   //remove the first and last character from the string
    values = values.substring(1, values.length - 1);
   //convert values to array
    values = values.split(",");
    var myChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['DEEP', 'LIGHT', 'REM', 'AWAKE'],
            datasets: [{
                label: 'Types of Sleep',
                data: values,
                backgroundColor: [
                    '#4B56D2',
                    '#82C3EC',
                    '#CF4DCE',
                    '#F273E6'
                ],
                borderColor: [
                    '#4B56D2',
                    '#82C3EC',
                    '#CF4DCE',
                    '#F273E6'
                ],
                borderWidth: 1,
                hoverOffset: 4
            }]
        }
    });
 }

 //Another method to create a chart
 function createChart(id, type, data, labels, title, xLabel, yLabel) {
    var ctx = document.getElementById(id).getContext('2d');
    var myChart = new Chart(ctx, {
        type: type,
        data: {
            labels: labels,
            datasets: [{
                label: title,
                data: data,
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1
            }]
},
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: yLabel,
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: xLabel,
                    }
                }

            }
        }
    });
 }

 //Function to open the GPS map
function openMap(id) {
    //Close all iframes
    let x = document.getElementsByClassName("map");
    let i;
    for (i = 0; i < x.length; i++) {
        x[i].hidden = true;
    }
    //Show the element with id="jsonSrc"
    document.getElementById(id).hidden = false;
}

//Create a heatmap
 const cal = new CalHeatmap();
function heatMap(json) {
    cal.paint({
        itemSelector: "#heatmap",
        date: { start: new Date('2022-01-01') },
        domain: { type: 'month',  label: { position: 'top' } },
        subDomain: { type: 'day', label: 'D', width: 20, height: 20 },
        data: { source: json, type: 'json', x: 'date', y: 'total', },
        scale: { type: 'diverging', scheme: 'PRGn', domain: [0, 5] },
    }, [[Tooltip, { text: function (date, value) {
        if (value == null) return 'No Activities on ' + cal.dateHelper.format(date, 'LL');
        return value + ' Activities on ' + cal.dateHelper.format(date, 'LL')
    } }]]);

}

function previous() {
    event.preventDefault();
    cal.previous();
}

function next() {
    event.preventDefault();
    cal.next();
}

//Function to change the year of the heatmap
function changeYear(date) {
    //update the heatmap
        cal.paint({
            date: { start: new Date(date.value + '-01-01') },
        })
}

function openTimeline(id) {
    //hide all elements with class="timeline__items"
    let x = document.getElementsByClassName("timeline");
    let i;
    for (i = 0; i < x.length; i++) {
        x[i].hidden = true;
    }
    document.getElementById(id).hidden = false;
}