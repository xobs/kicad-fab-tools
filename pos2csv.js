if (process.argv.length !== 4) {
    console.log("Check Command Arguments...");
    console.log("Usage: node pos2csv.js input.pos output.csv");
    process.exit(1);
}

var input = process.argv[2];
var output = process.argv[3];

//var outputString = '"Designator","NozzleNum","StackNum","Mid X","Mid Y","Rotation","Height","Speed","Vision","Pressure","Explanation"\r\n';
var outputString = 'Designator,Footprint,Mid X,Mid Y,Ref X,Ref Y,Pad X,Pad Y,Layer,Rotation,Comment\r\n';
outputString += ',,,,,,,,,,\r\n';

var outputFooter = "";


var lineReader = require('readline').createInterface({
    input: require('fs').createReadStream(input)
});

lineReader.on('line', function(line) {
    outputString += processLine(line);
});

lineReader.on('close', function() {
    var fs = require('fs');
    fs.writeFile(output, outputString, function(err) {
        if (err) {
            return console.log(err);
        }
    });
    //console.log(outputString);
});


function processLine(line) {
    if (line.lastIndexOf('#', 0) !== 0) {
        return formatCSV(line.split(/  +/)) + "\r\n";
    } else
        return '';
}

var columnRanges = {};
function formatCSV(details) {
    var xOffset = 0;
    var yOffset = 0;
    var columnIndex = {
        Ref: 0,
        Val: 1,
        Package: 2,
        PosX: 3,
        PosY: 4,
        Rot: 5,
        Side: 6
    };

    console.log("Details: " + JSON.stringify(details));
    details[columnIndex.PosX] = parseFloat(details[columnIndex.PosX]);
    details[columnIndex.PosY] = parseFloat(details[columnIndex.PosY]);
    details[columnIndex.Rot] = parseFloat(details[columnIndex.Rot]);

    details[columnIndex.PosX] += xOffset;
    details[columnIndex.PosY] += yOffset;

    details[columnIndex.PosX] = Math.round(details[columnIndex.PosX] * 1000) / 1000;
    details[columnIndex.PosY] = Math.round(details[columnIndex.PosY] * 1000) / 1000;

    var result = "";
    result += '"' + details[columnIndex.Ref] + '",'; // Designator
    result += '"' + details[columnIndex.Package] + '",'; // Footprint
    result += '"' + details[columnIndex.PosX] + 'mm",'; // Mid X
    result += '"' + details[columnIndex.PosY] + 'mm",'; // Mid Y
    result += '"' + details[columnIndex.PosX] + 'mm",'; // Ref X
    result += '"' + details[columnIndex.PosY] + 'mm",'; // Ref Y
    result += '"' + details[columnIndex.PosX] + 'mm",'; // Pad X
    result += '"' + details[columnIndex.PosY] + 'mm",'; // Pad Y
    result += '"' + details[columnIndex.Side] + '",'; // Layer
    result += '"' + details[columnIndex.Rot] + '",'; // Rotation
    result += '"' + details[columnIndex.Val] + '"'; // Comment

    return result;
}