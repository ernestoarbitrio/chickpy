## ⚠️ VERY PREMATURE AND EXPERIMENTAL PROJECT!!! ⚠️

ChickPy is a chart/plot generator with the goal of using a custom scripting language to render charts with several output options and backends. 
For example without knowing matplotlib or bokeh api you can render charts just writing `CREATE CHART "my_chart" VALUES [1,2,3] [4,5,6] TYPE SCATTER;`.

**What's available now:**
- 1 backend (Matplotlib)
- 3 type of charts (SCATTER, LINE, BAR)
- Basic values syntax definition e.g. [1,2,3] [3.4, 5.01, 6.7]
- Plotting data from CSV e.g. `CREATE CHART "foo" FROM CSV "path/to/csv/mydata.csv";`. CSV file must have only 2 columns with `x` and `y` as labels 🤷🏼‍♂️.

**Future work:**
- Bokeh backend
- Extend chart types
- Working with numpy arrays as data inputs
- Increment the flexibility of CSV usage specifing the column names to be used ad Data Source

**Demo:**

https://chickpy.pages.dev/
