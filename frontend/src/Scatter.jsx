import React from 'react';
import Plot from "react-plotly.js";
export default function Scatter(plot ) {
//   const trace = {
//     x: [4.2, 5.55, 6.91],
//     y: [3.14, 2.84, 4.34],
//     mode: "markers+lines",
//     type: "scatter",
//   };
//  const data = [trace];
const data_json = JSON.parse(plot.data);

  return (
    <div>
      <Plot
        data={data_json.data}
        layout={data_json.layout}
      />
    </div>
  );
}