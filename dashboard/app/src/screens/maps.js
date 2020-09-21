import React from "react";
import ReactDOM from "react-dom";
import HPlatform, { HMap, HMapPolyLine } from "react-here-map";

const points = [
  { lat: 52.5309825, lng: 13.3845921 },
  { lat: 52.5311923, lng: 13.3853495 },
  { lat: 52.5313532, lng: 13.3861756 },
  { lat: 52.5315142, lng: 13.3872163 },
  { lat: 52.5316215, lng: 13.3885574 },
  { lat: 52.5320399, lng: 13.3925807 },
  { lat: 52.5321472, lng: 13.3935785 },
];

ReactDOM.render(
  <HPlatform
    app_id="YOUR_APP_ID"
    app_code="YOUR_APP_CODE"
    apikey={"YOUR_API_KEY_FOR_V3.1"}
    useCIT
    useHTTPS
    includeUI
    includePlaces
  >
    <HMap
      style={{
        height: "400px",
        width: "800px",
      }}
      mapOptions={{ center: { lat: 52.5321472, lng: 13.3935785 }, zoom: 10 }}
    >
      <HMapPolyLine points={points} />
    </HMap>
  </HPlatform>,
  document.getElementById("app")
);