/* global window,document */
import React, {Component} from 'react';
import {render} from 'react-dom';
import MapGL from 'react-map-gl';
import DeckGLOverlay from './deckgl-overlay.js';
import moment from 'moment'
import {csv as requestCsv} from 'd3-request';

// Set your mapbox token here
const MAPBOX_TOKEN = 'pk.eyJ1Ijoic21iZCIsImEiOiJjamo3NTF4ZW4yZWRkM3BvNDM1aHVwMHFyIn0.ZVHV8w2p_03h5sy1l8-Y1w'; // eslint-disable-line

// Source data CSV
const DATA_URL =
  //'https://raw.githubusercontent.com/uber-common/deck.gl-data/master/examples/3d-heatmap/heatmap-data.csv'; // eslint-disable-line
  './June_24_grid_50_50_h20.csv'

function findGetParameter(parameterName) {
    var result = null,
        tmp = [];
    location.search
        .substr(1)
        .split("&")
        .forEach(function (item) {
          tmp = item.split("=");
          if (tmp[0] === parameterName) result = decodeURIComponent(tmp[1]);
        });
    return result;
}


export default class Counter extends Component {

  render() {
    const {date_start} = this.props;
    let timestamp = moment(date_start).format("DD-MM-YYYY HH:mm:ss")

    var h1Style = {
      color: 'white'
    };

    return (
      <h1 style={h1Style}>{timestamp}</h1>
    );
  }
}

class Root extends Component {
  constructor(props) {
    super(props);
    this.state = {
      viewport: {
        ...DeckGLOverlay.defaultViewport,
        width: 500,
        height: 500
      },
      data: null,
      date_start: null
    };
/*
    requestCsv(DATA_URL, (error, response) => {
      if (!error) {
        const data = response.map(d => [Number(d.lng), Number(d.lat)]);
        this.setState({data});
        console.log(data)
      }
    });
*/

    let param_snap = findGetParameter('snap')

    let param_date = findGetParameter('date')
    let param_time = findGetParameter('time')
    let param_min_lat = findGetParameter('min_lat')
    let param_min_long = findGetParameter('min_long')
    let param_max_lat = findGetParameter('max_lat')
    let param_max_long = findGetParameter('max_long')

    // date=2017-06-22&time=20:00&min_lat=44.9941845&max_lat=45.1202965&min_long=7.5991039&max_long=7.7697372

    if(param_snap != null) {
      let day = 14
      if (param_snap == '1'){
        day = 14
      } else if (param_snap == '2'){
        day = 21
      } else if (param_snap == '3'){
        day = 22
      }
      console.log('http://194.116.76.192:5000/heatmap?snap=' + param_snap + '')
      console.log(day)

      fetch('http://194.116.76.192:5000/heatmap?snap=' + param_snap + '')
        .then(data => this.setState({data: data.json(), date_start: moment('2017-06-' + day + ' 20:00')}));
    }

    else if(param_date == null){
      param_date = '2017-06-22'
      param_time = '20:00'
      param_min_lat = '44.9941845'
      param_min_long = '7.5991039'
      param_max_lat = '45.1202965'
      param_max_long = '7.7697372'

      fetch('http://194.116.76.192:5000/heatmap?date=' + param_date + '&time=' + param_time + '&min_lat=' + param_min_lat + '&max_lat=' + param_max_lat + '&min_long=' + param_min_long + '&max_long=' + param_max_long + '')
        .then(resp => resp.json())
        .then(data => this.setState({data: data, date_start: moment(param_date + ' ' + param_time)}));

    } else {
      //194.116.76.192
      fetch('http://194.116.76.192:5000/heatmap?date=' + param_date + '&time=' + param_time + '&min_lat=' + param_min_lat + '&max_lat=' + param_max_lat + '&min_long=' + param_min_long + '&max_long=' + param_max_long + '')
        .then(resp => resp.json())
        .then(data => this.setState({data: data, date_start: moment(param_date + ' ' + param_time)}));
    }


  }

  componentDidMount() {
    window.addEventListener('resize', this._resize.bind(this));
    this._resize();
  }

  _resize() {
    this._onViewportChange({
      width: window.innerWidth,
      height: window.innerHeight
    });
  }

  _onViewportChange(viewport) {
    this.setState({
      viewport: {...this.state.viewport, ...viewport}
    });
  }

  render() {
    const {viewport, data, date_start} = this.state;
    console.log(data)

    return (
      <MapGL
        {...viewport}
        mapStyle="mapbox://styles/mapbox/dark-v9"
        onViewportChange={this._onViewportChange.bind(this)}
        mapboxApiAccessToken={MAPBOX_TOKEN}
      >
        <Counter
          date_start={date_start}
        ></Counter>
        <DeckGLOverlay viewport={viewport} data={data || []} />
      </MapGL>
    );
  }
}

render(<Root />, document.body.appendChild(document.createElement('div')));
