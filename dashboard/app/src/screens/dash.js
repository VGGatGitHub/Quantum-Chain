import React, {Component} from "react";
import {Link} from 'react-router-dom';


import Logo from '../assets/logo.png';
import HPlatform, { HMap, HMapPolyLine, HMapCircle, HMapRoute, HMapMarker, Polygon, Marker, polygonOptions, markerOptions, routeParams } from "react-here-map";

const points = [
    { lat:37.7749, lng: -122.4194 },
    { lat: 37.3382, lng: -121.8863 },
    { lat: 36.9741, lng: -122.0308 },
    { lat: 35.282, lng: -120.6596 },
    { lat: 37.9577, lng: -121.2908 },
    { lat: 38.4404, lng: -122.7141 },
  ];
  
  const circleOptions = {
    style: {
      strokeColor: "rgba(55, 85, 170, 0.6)", // Color of the perimeter
      lineWidth: 2,
      fillColor: "rgba(0, 128, 0, 0.7)", // Color of the circle
    },
  };
  const circleOptions2 = {
    style: {
      strokeColor: "rgba(55, 85, 170, 0.6)", // Color of the perimeter
      lineWidth: 2,
      fillColor: "rgba(255, 128, 0, 0.7)", // Color of the circle
    },
  };

  const isoRoutingParams = {
    mode: "fastest;car;",
    start: "geo!37.734555,-122.436547",
    range: "1000",
    rangetype: "time",
  };
  const routeLineOptions = {
    style: { strokeColor: "green", lineWidth: 10 },
    arrows: { fillColor: "white", frequency: 2, width: 0.8, length: 0.7 },
  };
  const icon =
    '<svg width="24" height="24" ' +
    'xmlns="http://www.w3.org/2000/svg">' +
    '<rect stroke="white" fill="#1b468d" x="1" y="1" width="22" ' +
    'height="22" /><text x="12" y="18" font-size="12pt" ' +
    'font-family="Arial" font-weight="bold" text-anchor="middle" ' +
    'fill="white">H</text></svg>';
  
  const RouteMarkerIso = ({
    map,
    platform,
    ui,
    route,
    routeShape,
    center,
    component,
  }) => {
    return (
      <React.Fragment>
        <Polygon
          points={routeShape}
          options={polygonOptions}
          setViewBounds
          map={map}
          platform={platform}
        />
        <Marker
          coords={center}
          map={map}
          platform={platform}
          icon={icon}
          options={markerOptions}
          setViewBounds={false}
        />
      </React.Fragment>
    );
  };
export function Maps() {
    return (
        <div style={{margin:-10}}>
            <div style={{position:'absolute', height:'98vh', backgroundColor:'#000', width:'20vw', float:'left'}}>
            <img src={Logo} height="70vh"  style={{ margin:'15%'}}></img>
            <Link to="/"> <div style={{color:'white', fontFamily:'Roboto', fontSize:20, marginTop:'15%',marginBottom:'15%'}}>Status</div></Link>
            <Link to="/maps"> <div style={{color:'white', fontFamily:'Roboto', fontSize:20}}>Track</div></Link>
            </div>
            <div style={{float: "left", marginLeft:'22vw'}}>
              <div style={{margin:"5vh 2.5%",fontFamily:"Roboto", fontSize:"3.75vh",lineHeight:"100%", color:"#4A73B1"}}>
              
                Track
                
            <HPlatform
    app_id="qfqqNcCx8qOx1ihb4I7X"
    apikey={"5x25sr7a7eRRgBdVqHdVSwcbRtdtjT__ry0IxOpX6IQ"}
    useCIT
    useHTTPS
    includeUI
    includePlaces
  >
    <HMap
      style={{
        height: "800px",
        width: "1400px",
      }}
      mapOptions={{ center: { lat:37.7749, lng: -122.4194 }, zoom: 2 }}
    >
      <HMapPolyLine points={points} />
      <HMapCircle coords={points[0]} radius={10000} options={circleOptions}  />
      <HMapCircle coords={points[1]} radius={10000} options={circleOptions2} />
      <HMapCircle coords={points[2]} radius={10000} options={circleOptions2} />
      <HMapCircle coords={points[3]} radius={10000} options={circleOptions2} />
      <HMapCircle coords={points[4]} radius={10000} options={circleOptions2} />
      <HMapCircle coords={points[5]} radius={10000} options={circleOptions2} />
      <HMapRoute
      routeParams={isoRoutingParams}
      icon={icon}
      isoLine
      defaultDisplay
      lineOptions={routeLineOptions}
    />
    </HMap>
    
  </HPlatform>
  </div>
      </div>
      </div>
    );
  }



