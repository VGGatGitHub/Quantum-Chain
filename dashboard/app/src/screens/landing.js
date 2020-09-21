import React, {Component} from "react";
import {Link} from 'react-router-dom';
import {XYPlot, VerticalGridLines, HorizontalGridLines,MarkSeries, LineSeries} from 'react-vis';
import { LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip } from 'recharts';

import Logo from '../assets/logo.png';
const data = [{name: '12:00', Temperature: 25, Humidity: 50, Pressure: 50, Movement:5}, {name: '12:10', Temperature: 24, Humidity: 50, Pressure: 40, Movement:5}, {name: '12:20', Temperature: 25, Humidity: 50, Pressure: 30, Movement:3}, {name: '12:30', Temperature: 20, Humidity: 45, Pressure: 30, Movement:7}, {name: '12:40', Temperature: 24, Humidity: 40, Pressure: 60, Movement:2}];


class Dash extends Component {
  constructor(props) {
    super(props);
  } 
    render() {
        return (
         <div style={{margin:-10}}>
            <div style={{position:'absolute', height:'98vh', backgroundColor:'#000', width:'20vw', float:'left'}}>
            <img src={Logo} height="70vh"  style={{ margin:'15%'}}></img>
            <Link to="/"> <div style={{color:'white', fontFamily:'Roboto', fontSize:20, marginTop:'15%',marginBottom:'15%'}}>Status</div></Link>
            <Link to="/maps"> <div style={{color:'white', fontFamily:'Roboto', fontSize:20}}>Track</div></Link>
            </div>
            <div style={{float: "left", marginLeft:'22vw'}}>
              <div style={{margin:"5vh 2.5%",fontFamily:"Roboto", fontSize:"3.75vh",lineHeight:"100%", color:"#4A73B1"}}>
              
                Status
               
                    <LineChart width={1400} height={800} data={data} margin={{ top: 15, right: 40, bottom: 25, left: 10 }} >
                    <Line type="monotone" dataKey="Temperature" stroke="#8884d8" />
                    <Line type="monotone" dataKey="Humidity" stroke="#668dd8" />
                    <Line type="monotone" dataKey="Pressure" stroke="#228dd8" />
                    <Line type="monotone" dataKey="Movement" stroke="#108dd8" />
                    <CartesianGrid stroke="#ccc" strokeDasharray="5 5" />
                    <XAxis dataKey={"name"} />
                    <YAxis />
                    <Tooltip />
                </LineChart>
                    
                <div style={{ marginRight:"5%"}}>
            
                </div>
                </div>
             
            </div>
         </div>   
        );
    }
}

export default Dash;