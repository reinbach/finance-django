var month_display = d3.scale.quantize()
    .range(["Janurary", "February", "March", "April", "May",
            "June", "July", "August", "September", "October",
            "November", "December"])
    .domain([1,12]);


function HandleYearlyDebitData(data) {
    $("#monthly-debit-charts-loader").hide();

    var width = 1200,
        height = 800;

    var pie = d3.layout.pie()
        .sort(null)
        .value(function(d) {
            return d.balance;
        });

    var svg = d3.select("#monthly-debit-charts").append("svg")
        .attr("width", width)
        .attr("height", height)

    var key = function(d) {
        return window.btoa(d.data.label).replace(/=/g, "");
    };

    var months = d3.keys(data);
    var radius = Math.min(width, height) / 4 - 40;

    var arc = d3.svg.arc()
        .outerRadius(radius - 10)
        .innerRadius(0);

    var block_height = - (height / 4);

    height_needed = (height / 2) * Math.ceil(months.length / 2);
    svg.attr("height",
             d3.max([height_needed, height]));

    for (var i in months) {
        var color = d3.scale.ordinal()
            .range(colors.slice(10, 10 + data[months[i]].length))
            .domain([
                d3.min(data[months[i]], function(d) {
                    return d.label;
                }),
                d3.max(data[months[i]], function(d) {
                    return d.label;
                })
            ]);

        // setup chart block dimensions
        // at most 12 months
        var block_width = 0;
        if (i % 3 == 0) {
            block_width = width / 6;
            block_height = block_height + height / 2;
        } else {
            switch (i) {
            case "1":
            case "4":
            case "7":
            case "10":
                block_width = width / 2;
                break;
            default:
                block_width = (width / 6) * 5;
                break;
            }
        }

        // create pie chart block
        block = svg.append("g")
            .attr(
                "transform",
                "translate(" + block_width + "," + block_height + ")"
            )

        // add title
        block.append("text")
            .attr("transform",
                  "translate(0, -" + (height / 4 - 20) + ")")
            .attr("dy", "1em")
            .style("text-anchor", "middle")
            .text(month_display(months[i]));

        slices = block.selectAll(".arc")
            .data(pie(data[months[i]]))
            .enter()

        // create pie chart
        slices.append("g")
            .attr("class", "arc")
            .append("path")
            .attr("d", arc)
            .style("fill", function(d) {
                return color(d.value);
            })
            .on("mouseover", function(d) {
                $("." + key(d)).show();
            })
            .on("mouseout", function(d) {
                $("." + key(d)).hide();
            });


        // create label
        slices.append("text")
            .attr("class", function(d) {
                return key(d);
            })
            .attr("transform", function(d) {
                return "translate(" + arc.centroid(d) + ")";
            })
            .attr("dy", ".35em")
            .style("text-anchor", "middle")
            .text(function(d) {
                $("." + key(d)).hide();
                return d.data.label + " (" + d.data.balance + ")";
            });

    }
}

function HandleYearlyDebitVsCreditData(data) {
    $("#monthly-debit-vs-credit-charts-loader").hide();

    var margin = {top: 10, right: 10, bottom: 10, left: 50};
    var width = 1200 - margin.right - margin.left,
        height = 200 - margin.top - margin.bottom;

    var y = d3.scale.linear()
        .domain(d3.extent(data, function(d) { return parseInt(d[1]); }))
        .range([0, height])
        .nice();

    var x = d3.scale.ordinal()
        .domain(data.map(function(d) { return d[0]; }))
        .rangeRoundBands([0, width], .2);

    var months = d3.keys(data);

    var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left");

    var svg = d3.select("#monthly-debit-vs-credit-charts").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    svg.selectAll(".bar")
        .data(data)
        .enter()
        .append("rect")
        .attr("class", function(d) {
            return d[1] < 0 ? "bar positive" : "bar negative";
        })
        .attr("x", function(d) { return x(d[0]); })
        .attr("y", function(d) { return y(Math.min(0, d[1])); })
        .attr("width", x.rangeBand())
        .attr("height", function(d) { return Math.abs(y(d[1]) - y(0)); });

    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis);

    svg.append("g")
        .attr("class", "x axis")
        .append("line")
        .attr("y1", y(0))
        .attr("y2", y(0))
        .attr("x2", width);
}
