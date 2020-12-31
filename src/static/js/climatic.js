/*
 * 
 * TODO: Adjust the display format of dates on the line graph. 
 * 
 * TODO: Style the page to look nice instead of shitty. 
 * 
 * TODO: Make Flask host the CSV file created by the 
 * data logger so users can choose to download the master file and parse its
 * data. 
 * 
 * TODO: Trigger when an 'analyze' button is clicked instead of when a file is 
 * selected.
 * 
 * TODO: Format the code to conform to a common JS style guide
 * 
 * TODO: Remove all the console.log lines used for debugging
 *
 */


/** Check the column definitions of the CSV file
 *  @param {string} rawData the contents of the file as a string
 *  @returns {boolean} true if the columns are correct, else false
 */
function checkColumns(rawData){
    var firstline = rawData.split("\n")[0].replace(/\s+/g, "");
    //console.log(firstline);
    if(firstline != "Timestamp,Celsius,Fahrenheit,Humidity"){
        return false
    }
    return true
}


/** Verify the file selected is a CSV file with data in the format we expect
 *  @param {string} rawData string the raw file contents returned by FileReader API
 *  @returns {boolean} true if the file is okay, otherwise false
 * 
 */
function verifyFile(rawData){
    var i;
    var matches;
    var splitdata = rawData.split("\n");

    // make sure the column definitions are correct
    if(!checkColumns(rawData)){
        console.log("Badcolumns");
        return false
    }

    /* make sure each record contains 4 columns */
    for(i = 0; i < splitdata.length; i++){
        matches = splitdata[i].match(/,/g);
        if(matches != null && matches.length != 3){
            console.log("Bad line");
            console.log(splitdata[i]);
            return false
        }
    }
    
    return true
}


/** Clear the error alert box
 * 
 */
function clearError(){
    $("#error-box").hide();
    $("#error-msg").text("");
}


/** Display the error message in a Bootstrap alert box
 *  @param {string} message string the error message to display
 * 
 */
function displayError(message){
    // clear any previous data and hide cards on error
    $("#file-content").text("");
    $("#raw-card").hide();
    $("#graph-card").hide();
    $("#stat-card").hide();
    clearStatistics();

    // fill in message and display error div
    $("#error-msg").text(message);
    $("#error-box").show();
 }


/** Read in a local file and call the displayContents function
 *  @param {event object} e the event trigger when a file is selected
 * 
 */
function readSingleFile(e) {
    //console.log(e);
    var file = e.target.files[0];
    if (!file) {
        return;
    }
    var reader = new FileReader();
    reader.onload = function(e) {
        var contents = e.target.result;
        handleContents(contents);
    };
    reader.readAsText(file);
}


/** Handles the file contents, verify, parse, and display 
 *   the contents of the uploaded file
 *  @param {string} contents file contents as a string returned by tehe FileReader API
 * 
 */
function handleContents(contents) {
    // make sure we have a valid CSV data file
    if(!verifyFile(contents)){
        displayError("Incorrect data detected. Please try a different file.");
        return;
    } else {
        clearError();
    }

    // populate raw data scroll box
    $("#file-content").text(contents);

    // parse CSV data into an array
    var data = CSVToArray(contents, ",");
    
    // debugging
    //console.log(data);
    //console.log("------------------");
    var parsed = parseData(data);
    //console.log(parsed);
    displayStatistics(calculateStatistics(parsed));
    
    /* show cards and plot line graph. 
     * Graph MUST be plotted AFTER card is shown */
    $("#graph-card").show();
    $("#raw-card").show();
    $("#stat-card").show();
    var line = makeGraph($("#line-graph"), parsed);
}


/** Calculates statistics from the parsed CSV data, if there are multiple data
 *  points that tie, then the most recent data point is preferred
 *  @param {object} data an array of objects returned from the parseData function
 *  @returns {object} an object containing the max/min/avg temperature seen and 
 *   max/min/avg humidity seen.
 * 
 */
function calculateStatistics(data){
    var hightemp = -1;
    var lowtemp = 1000000;

    var highhumid = -1;
    var lowhumid = 1000;

    var avgtemp = 0;
    var tempcount = 0
    
    var avghumidity = 0;
    var humidcount = 0;
    
    var hightempdate, lowtempdate, highhumiddate, lowhumiddate;

    var stats = []
    var i;
    for(i = 0; i < data.length; i++){
        if(data[i].hasOwnProperty("fahrenheit")){
            tempcount++;
            avgtemp += data[i]["fahrenheit"];

            if(data[i]["fahrenheit"] >= hightemp){
                hightemp = data[i]["fahrenheit"];
                hightempdate = data[i]["timestamp"];
            }
            
            if(data[i]["fahrenheit"] <= lowtemp){
                lowtemp = data[i]["fahrenheit"];
                lowtempdate = data[i]["timestamp"];
            }
        }

        if(data[i].hasOwnProperty("humidity")){
            humidcount++;
            avghumidity += data[i]["humidity"];

            if(data[i]["humidity"] >= highhumid){
                highhumid = data[i]["humidity"];
                highhumiddate = data[i]["timestamp"];
            }
            if(data[i]["humidity"] <= lowhumid){
                lowhumid = data[i]["humidity"];
                lowhumiddate = data[i]["timestamp"];
            }
        }
    }

    avgtemp /= tempcount;
    avghumidity /= humidcount;
    stats.push({"maxtemp": hightemp, "maxtempdate": hightempdate, 
                "mintemp": lowtemp, "mintempdate": lowtempdate, 
                "avgtemp": avgtemp, "maxhumid": highhumid, 
                "maxhumiddate": highhumiddate, "minhumid": lowhumid, 
                "minhumiddate": lowhumiddate, "avghumid": avghumidity});
    return stats;
}


/** Display the statistics in the stat-card
 * @param {object} stats the statistics calculated by calculateStatistics
 * 
 */
function displayStatistics(stats){

    $("#max-temp").text("Max: " + stats[0]["maxtemp"].toString() + " F" + " - " + getDateString(stats[0]["maxtempdate"]));
    $("#min-temp").text("Min: " + stats[0]["mintemp"].toString() + " F" + " - " + getDateString(stats[0]["mintempdate"]));
    $("#avg-temp").text("Average: " + stats[0]["avgtemp"].toFixed(2) + " F");

    $("#max-humidity").text("Max: " + stats[0]["maxhumid"].toString() + "%" + " - " + getDateString(stats[0]["maxhumiddate"]));
    $("#min-humidity").text("Min: " + stats[0]["minhumid"].toString() + "%" + " - " + getDateString(stats[0]["minhumiddate"]));
    $("#avg-humidity").text("Average: " + stats[0]["avghumid"].toFixed(2) + "%");
}


/** Clear statistics on an error
 * 
 */
function clearStatistics(){
    $("#max-temp").text("");
    $("#min-temp").text("");
    $("#avg-temp").text("");

    $("#max-humidity").text("");
    $("#min-humidity").text("");
    $("#avg-humidity").text("");
}


/** Parse the raw CSV data array into parsed dates and convert strings to floats
 * @param data raw CSV data produced by CSVToArray
 * @returns {object} a new object containing timestamp, fahrenheit, and humidity data
 * 
 */
function parseData(data){
    var newdata = [];
    var i;

    // start at 1 to skip column definitions
    for(i = 1; i < data.length; i++){
        if(data[i].length > 1){
            var date = Date.parse(data[i][0]);
            //var cels = parseFloat(temp1[i][1]);
            var fah = parseFloat(data[i][2]);
            var hum = parseFloat(data[i][3].slice(0, -1));
            newdata.push({"timestamp": date, "fahrenheit": fah, "humidity": hum});
        }
    }

    return newdata;
}


/** Get only the last 150 entries if there is a lot of data points
 * @param {object} data parsed CSV data produced by the parseData function
 * @returns {object} a new object containing only the last 15 entries
 * 
 */
function trimData(data){
    var i;
    var newdata = [];

    if(data.length <= 150){
        return data;
    }

    for(i = data.length-150; i < data.length; i++){
        newdata.push(data[i]);
    }
    return newdata;
}


/** Make the line graph
 * @param {string} element the element the graph will be anchored to
 * @param {object} parseData parsed CSV data produced by parseData()
 * 
 */
function makeGraph(element, parseData){
    // Remove the previous graph if it exists
    $("#line-graph").empty();
    var graphData;
    
    // If more than 15 data points, only show most recent 15
    if(parseData.length > 150){
        graphData = trimData(parseData);
    } else {
        graphData = parseData;
    }

    var line = new Morris.Line({
        // ID of the element in which to draw the chart.
        element: element,
        // Chart data records -- each entry in this array 
        // corresponds to a point on the chart.
        data: graphData,
        // The name of the data record attribute that contains 
        // x-values.
        xkey: 'timestamp',
        // A list of names of data record attributes that 
        // contain y-values.
        ykeys: ['fahrenheit', 'humidity'],
        // Labels for the ykeys -- will be displayed when 
        // you hover over the chart.
        labels: ['Temperature', 'Humidity']
    });
    return line;
}


// From: 
// https://www.bennadel.com/blog/1504-ask-ben-parsing-csv-strings-with-javascript-exec-regular-expression-command.htm

/** This will parse a delimited string into an array of
 *  arrays. The default delimiter is the comma, but this
 *  can be overriden in the second argument.
 *  @param {string} strData raw file contents
 *  @param {string} strDelimiter the delimiter to use to separate columns
 *  @returns {array} a 2D array representing the CSV data
 *
 */ 
function CSVToArray(strData, strDelimiter){
    // Check to see if the delimiter is defined. If not,
    // then default to comma.
    strDelimiter = (strDelimiter || ",");

    // Create a regular expression to parse the CSV values.
    var objPattern = new RegExp((
            // Delimiters.
            "(\\" + strDelimiter + "|\\r?\\n|\\r|^)" +

            // Quoted fields.
            "(?:\"([^\"]*(?:\"\"[^\"]*)*)\"|" +

            // Standard fields.
            "([^\"\\" + strDelimiter + "\\r\\n]*))"
        ), "gi");

        // Create an array to hold our data. Give the array
        // a default empty first row.
        var arrData = [[]];

        // Create an array to hold our individual pattern
        // matching groups.
        var arrMatches = null;

    // Keep looping over the regular expression matches
    // until we can no longer find a match.
    while(arrMatches = objPattern.exec(strData)){

        // Get the delimiter that was found.
        var strMatchedDelimiter = arrMatches[1];

        // Check to see if the given delimiter has a length
        // (is not the start of string) and if it matches
        // field delimiter. If id does not, then we know
        // that this delimiter is a row delimiter.
        if(strMatchedDelimiter.length && (strMatchedDelimiter != strDelimiter)){
            // Since we have reached a new row of data,
            // add an empty row to our data array.
            arrData.push([]);
        }

        // Now that we have our delimiter out of the way,
        // let's check to see which kind of value we
        // captured (quoted or unquoted).
        if(arrMatches[2]){

            // We found a quoted value. When we capture
            // this value, unescape any double quotes.
            var strMatchedValue = arrMatches[2].replace(
                new RegExp("\"\"", "g"), "\"");

        }else{

            // We found a non-quoted value.
            var strMatchedValue = arrMatches[3];

        }

        // Now that we have our value string, let's add
        // it to the data array.
        arrData[arrData.length - 1].push(strMatchedValue);
    }

    // Return the parsed data.
    return(arrData);
}


/** A simple function to convert raw date in Epoch time to a string
 *  @param {int} rawdate number of seconds since Epoch
 *  @returns {string} the formatted date as a string
 * 
 */
function getDateString(rawdate){
    var parsed = new Date(rawdate);
    return parsed.toLocaleString();
}

/* Listener that is triggered when a file is selected */

//document.getElementById('file-input').addEventListener('change', readSingleFile, false);
$("#file-input").on("change", readSingleFile);
/*
$("#file-input").on("change", function(e){
    console.log(e);
    console.log("SUCCESS")
});
*/
