var ColorSet = function() {
    this.color_options = [
        "#000000",
        "#0c090a",
        "#2c3539",
        "#2b1b17",
        "#34282c",
        "#25383c",
        "#3b3131",
        "#413839",
        "#3d3c3a",
        "#463e3f",
        "#4c4646",
        "#504a4b",
        "#565051",
        "#5c5858",
        "#625d5d",
        "#666362",
        "#6d6968",
        "#726e6d",
        "#736f6e",
        "#837e7c",
        "#848482",
        "#b6b6b4",
        "#d1d0ce",
        "#e5e4e2",
        "#bcc6cc",
        "#98afc7",
        "#6d7b8d",
        "#657383",
        "#616d7e",
        "#646d7e",
        "#566d7e",
        "#737ca1",
        "#4863a0",
        "#2b547e",
        "#2b3856",
        "#151b54",
        "#000080",
        "#342d7e",
        "#15317e",
        "#151b8d",
        "#0000a0",
        "#0020c2",
        "#0041c2",
        "#2554c7",
        "#1569c7",
        "#2b60de",
        "#1f45fc",
        "#6960ec",
        "#736aff",
        "#357ec7",
        "#368bc1",
        "#488ac7",
        "#3090c7",
        "#659ec7",
        "#87afc7",
        "#95b9c7",
        "#728fce",
        "#2b65ec",
        "#306eff",
        "#157dec",
        "#1589ff",
        "#6495ed",
        "#6698ff",
        "#38acec",
        "#56a5ec",
        "#5cb3ff",
        "#3bb9ff",
        "#79baec",
        "#82caff",
        "#a0cfec",
        "#b7ceec",
        "#b4cfec",
        "#c2dfff",
        "#c6deff",
        "#afdcec",
        "#addfff",
        "#bdedff",
        "#cfecec",
        "#e0ffff",
        "#ebf4fa",
        "#f0f8ff",
        "#f0ffff",
        "#ccffff",
        "#93ffe8",
        "#9afeff",
        "#7fffd4",
        "#00ffff",
        "#7dfdfe",
        "#57feff",
        "#8eebec",
        "#50ebec",
        "#4ee2ec",
        "#81d8d0",
        "#92c7c7",
        "#77bfc7",
        "#78c7c7",
        "#48cccd",
        "#43c6db",
        "#46c7c7",
        "#43bfc7",
        "#3ea99f",
        "#3b9c9c",
        "#438d80",
        "#348781",
        "#307d7e",
        "#5e7d7e",
        "#4c787e",
        "#008080",
        "#4e8975",
        "#78866b",
        "#848b79",
        "#617c58",
        "#728c00",
        "#667c26",
        "#254117",
        "#306754",
        "#347235",
        "#437c17",
        "#387c44",
        "#347c2c",
        "#347c17",
        "#348017",
        "#4e9258",
        "#6aa121",
        "#4aa02c",
        "#41a317",
        "#3ea055",
        "#6cbb3c",
        "#6cc417",
        "#4cc417",
        "#52d017",
        "#4cc552",
        "#54c571",
        "#99c68e",
        "#89c35c",
        "#85bb65",
        "#8bb381",
        "#9cb071",
        "#b2c248",
        "#a1c935",
        "#7fe817",
        "#59e817",
        "#57e964",
        "#64e986",
        "#5efb6e",
        "#00ff00",
        "#5ffb17",
        "#87f717",
        "#8afb17",
        "#6afb92",
        "#98ff98",
        "#b5eaaa",
        "#c3fdb8",
        "#ccfb5d",
        "#b1fb17",
        "#bce954",
        "#edda74",
        "#ede275",
        "#ffe87c",
        "#ffff00",
        "#fff380",
        "#ffffc2",
        "#ffffcc",
        "#fff8c6",
        "#fff8dc",
        "#f5f5dc",
        "#fbf6d9",
        "#faebd7",
        "#f7e7ce",
        "#ffebcd",
        "#f3e5ab",
        "#ece5b6",
        "#ffe5b4",
        "#ffdb58",
        "#ffd801",
        "#fdd017",
        "#eac117",
        "#f2bb66",
        "#fbb917",
        "#fbb117",
        "#ffa62f",
        "#e9ab17",
        "#e2a76f",
        "#deb887",
        "#ffcba4",
        "#c9be62",
        "#e8a317",
        "#ee9a4d",
        "#c8b560",
        "#d4a017",
        "#c2b280",
        "#c7a317",
        "#c68e17",
        "#b5a642",
        "#ada96e",
        "#c19a6b",
        "#cd7f32",
        "#c88141",
        "#c58917",
        "#af9b60",
        "#af7817",
        "#b87333",
        "#966f33",
        "#806517",
        "#827839",
        "#827b60",
        "#786d5f",
        "#493d26",
        "#483c32",
        "#6f4e37",
        "#7f5217",
        "#7f462c",
        "#c47451",
        "#c36241",
        "#c35817",
        "#c85a17",
        "#cc6600",
        "#e56717",
        "#e66c2c",
        "#f87217",
        "#f87431",
        "#e67451",
        "#ff8040",
        "#f88017",
        "#ff7f50",
        "#f88158",
        "#f9966b",
        "#e78a61",
        "#e18b6b",
        "#e77471",
        "#f75d59",
        "#e55451",
        "#e55b3c",
        "#ff0000",
        "#ff2400",
        "#f62217",
        "#f70d1a",
        "#f62817",
        "#e42217",
        "#e41b17",
        "#dc381f",
        "#c34a2c",
        "#c24641",
        "#c04000",
        "#c11b17",
        "#9f000f",
        "#990012",
        "#8c001a",
        "#954535",
        "#7e3517",
        "#8a4117",
        "#7e3817",
        "#800517",
        "#810541",
        "#7d0541",
        "#7e354d",
        "#7d0552",
        "#7f4e52",
        "#7f5a58",
        "#7f525d",
        "#b38481",
        "#c5908e",
        "#c48189",
        "#c48793",
        "#e8adaa",
        "#edc9af",
        "#fdd7e4",
        "#fcdfff",
        "#ffdfdd",
        "#fbbbb9",
        "#faafbe",
        "#faafba",
        "#f9a7b0",
        "#e7a1b0",
        "#e799a3",
        "#e38aae",
        "#f778a1",
        "#e56e94",
        "#f660ab",
        "#fc6c85",
        "#f6358a",
        "#e45e9d",
        "#e4287c",
        "#f535aa",
        "#ff00ff",
        "#e3319d",
        "#f433ff",
        "#d16587",
        "#c25a7c",
        "#ca226b",
        "#c12869",
        "#c12267",
        "#c25283",
        "#c12283",
        "#b93b8f",
        "#7e587e",
        "#571b7e",
        "#583759",
        "#4b0082",
        "#461b7e",
        "#4e387e",
        "#614051",
        "#5e5a80",
        "#6a287e",
        "#7d1b7e",
        "#a74ac7",
        "#b048b5",
        "#6c2dc7",
        "#842dce",
        "#8d38c9",
        "#7a5dc7",
        "#7f38ec",
        "#8e35ef",
        "#893bff",
        "#8467d7",
        "#a23bec",
        "#b041ff",
        "#c45aec",
        "#9172ec",
        "#9e7bff",
        "#d462ff",
        "#e238ec",
        "#c38ec7",
        "#c8a2c8",
        "#e6a9ec",
        "#e0b0ff",
        "#c6aec7",
        "#f9b7ff",
        "#d2b9d3",
        "#e9cfec",
        "#ebdde2",
        "#e3e4fa",
        "#fdeef4",
        "#fff5ee",
        "#fefcff",
        "#ffffff"
    ];
};

ColorSet.prototype.setStart = function(start) {
    console.log("set start with: " + start);
    switch (start) {
    case "white":
        this.start = "#ffffff";
        break;
    case "red":
        this.start = "#ff0000";
        break;
    case "blue":
        this.start = "#000080";
        break;
    case "green":
        this.start = "#728c00";
        break;
    case "black":
        this.start = "#000000";
        break;
    default:
        // check if valid value
        var index = this.color_options.indexOf[start];
        if (index != -1) {
            this.start = start;
        } else {
            this.start = "#000000";
        }
        break;
    }
};

ColorSet.prototype.setRange = function(range) {
    this.range = range;
};

ColorSet.prototype.setStep = function(step) {
    this.step = step;
};

ColorSet.prototype.getSet = function(start, range, step) {
    this.setStart(start);
    this.setRange(range);
    this.setStep(step);

    colors = [];
    var index = this.color_options.indexOf(this.start);
    colors.push(this.color_options[index]);
    for (var i = 0; i < this.range; i += 1) {
        index = index + this.step;
        if (index > this.color_options.length) {
            index = index - this.color_options.length;
        }
        colors.push(this.color_options[index]);
    }
    return colors;
};

ColorSet.prototype.convertRgbToHex = function(r, g, b) {
    return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
};


// Example
var ColorExamples = function() {
    var color = new ColorSet();
    console.log(color.color_options.length);
    colors = color.getSet(color.color_options[0],
                          color.color_options.length, 1);
    for (var i = 0; i < colors.length; i++) {
        var colorNode = document.createElement("div");
        var colorText = document.createTextNode(colors[i]);
        colorNode.style.width = "200px";
        colorNode.style.height = "20px";
        colorNode.style.backgroundColor = colors[i];
        colorNode.appendChild(colorText);
        document.body.appendChild(colorNode);
    };
};
