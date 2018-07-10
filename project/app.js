/* global document, fetch, window */
import React, {Component} from 'react';
import {render} from 'react-dom';
import MapGL from 'react-map-gl';
import DeckGLOverlay from './deckgl-overlay.js';

// Set your mapbox token here
const MAPBOX_TOKEN = 'pk.eyJ1Ijoic21iZCIsImEiOiJjamo3NTF4ZW4yZWRkM3BvNDM1aHVwMHFyIn0.ZVHV8w2p_03h5sy1l8-Y1w'; // eslint-disable-line

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

class Root extends Component {
  constructor(props) {
    super(props);
    this.state = {
      viewport: {
        ...DeckGLOverlay.defaultViewport,
        width: 500,
        height: 500
      },
      buildings: null,
      trips: null,
      time: 0
    };
    /*
    fetch(DATA_URL.BUILDINGS)
      .then(resp => resp.json())
      .then(data => this.setState({buildings: data}));
    */
    let param_date = findGetParameter('date')
    let param_min_time = findGetParameter('min_time')
    let param_max_time = findGetParameter('max_time')
    let param_min_lat = findGetParameter('min_lat')
    let param_min_long = findGetParameter('min_long')
    let param_max_lat = findGetParameter('max_lat')
    let param_max_long = findGetParameter('max_long')

    // date=2017-06-22&time=20:00&min_lat=44.9941845&max_lat=45.1202965&min_long=7.5991039&max_long=7.7697372
    if(param_date == null){
      param_date = '2017-06-15'
      param_min_time = '15:44'
      param_max_time = '15:54'
      param_min_lat = '44.9941845'
      param_min_long = '7.5991039'
      param_max_lat = '45.1202965'
      param_max_long = '7.7697372'

    }

    // date=2017-06-22&min_time=15:00&max_time=15:05&min_lat=44.9941845&max_lat=45.1202965&min_long=7.5991039&max_long=7.7697372
    //fetch('http://194.116.76.192:5000/')
    console.log('http://194.116.76.192:5000?date=' + param_date + '&min_time=' + param_min_time + '&max_time=' + param_max_time + '&min_lat=' + param_min_lat + '&max_lat=' + param_max_lat + '&min_long=' + param_min_long + '&max_long=' + param_max_long + '')
    fetch('http://194.116.76.192:5000?date=' + param_date + '&min_time=' + param_min_time + '&max_time=' + param_max_time + '&min_lat=' + param_min_lat + '&max_lat=' + param_max_lat + '&min_long=' + param_min_long + '&max_long=' + param_max_long + '')
      .then(resp => resp.json())
      .then(data => this.setState({trips: data}))
      .then(resp => this.setState({time: 0}));

  }


  componentDidMount() {
    window.addEventListener('resize', this._resize.bind(this));
    this._resize();
    this._animate();
  }

  componentWillUnmount() {
    if (this._animationFrame) {
      window.cancelAnimationFrame(this._animationFrame);
    }
  }

  _animate(){
    this.setState({
      time: this.state.time + 1/120
    });
    this._animationFrame = window.requestAnimationFrame(this._animate.bind(this));
  }

/*
  _animate() {
    const timestamp = Date.now();
    const loopLength = 6;
    const loopTime = 6000;
    //console.log("ANIMATION")
    this.setState({
      time: (timestamp % loopTime) / loopTime * loopLength
    });
    this._animationFrame = window.requestAnimationFrame(this._animate.bind(this));
  }
*/
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
    const {viewport, trips, time} = this.state;

    return (
      <MapGL
        {...viewport}
        mapStyle="mapbox://styles/mapbox/dark-v9"
        onViewportChange={this._onViewportChange.bind(this)}
        mapboxApiAccessToken={MAPBOX_TOKEN}
      >
        <DeckGLOverlay
          viewport={viewport}
          trips={trips}
          trailLength={2}
          time={time}
        />
      </MapGL>
    );
  }
}

render(<Root />, document.body.appendChild(document.createElement('div')));
