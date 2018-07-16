/* global document, fetch, window */
import React, {Component} from 'react';
import {render} from 'react-dom';
import MapGL from 'react-map-gl';
import DeckGLOverlay from './deckgl-overlay.js';
import moment from 'moment'

// Creare un token su mapbox.com e inserirlo qui 
const MAPBOX_TOKEN = 'pk.eyJ1Ijoic21iZCIsImEiOiJjamo3NTF4ZW4yZWRkM3BvNDM1aHVwMHFyIn0.ZVHV8w2p_03h5sy1l8-Y1w'; // eslint-disable-line


// Funzione per estrarre i parametri GET dall'url
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

// Oggetto per mostrare il timestamp
export default class Counter extends Component {

  render() {
    const {time, date_start, date_end} = this.props;
    let timestamp = moment(date_start).add(parseInt(time), 'minutes').format("DD-MM-YYYY HH:mm:ss")

    if(moment(date_start).add(parseInt(time), 'minutes') > moment(date_end)){
      timestamp = moment(date_end).format("DD-MM-YYYY HH:mm:ss")
    }

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
      buildings: null,
      trips: null,
      time: 0,
      date_start: null,
      date_end: null
    };

    // Parametri del GET. Se non ci sono vengono forzati automaticamente

    let param_snap = findGetParameter('snap')

    let param_date = findGetParameter('date')
    let param_min_time = findGetParameter('min_time')
    let param_max_time = findGetParameter('max_time')
    let param_min_lat = findGetParameter('min_lat')
    let param_min_long = findGetParameter('min_long')
    let param_max_lat = findGetParameter('max_lat')
    let param_max_long = findGetParameter('max_long')

    // Se viene passato il parametro SNAP carico il JSON già compilato.
    if(param_snap != null) {
      fetch('./concerto.json')
        .then(data => this.setState({trips: data.json(), date_start: moment('2017-06-21 17:00')}))
        .then(data => console.log(this.state));

    } else if(param_date == null){
      param_date = '2017-06-15'
      param_min_time = '15:44'
      param_max_time = '15:54'
      param_min_lat = '44.9941845'
      param_min_long = '7.5991039'
      param_max_lat = '45.1202965'
      param_max_long = '7.7697372'


      // Chiamata API al backend
      console.log('http://194.116.76.192:5000?date=' + param_date + '&min_time=' + param_min_time + '&max_time=' + param_max_time + '&min_lat=' + param_min_lat + '&max_lat=' + param_max_lat + '&min_long=' + param_min_long + '&max_long=' + param_max_long + '')
      fetch('http://194.116.76.192:5000?date=' + param_date + '&min_time=' + param_min_time + '&max_time=' + param_max_time + '&min_lat=' + param_min_lat + '&max_lat=' + param_max_lat + '&min_long=' + param_min_long + '&max_long=' + param_max_long + '')
      .then(resp => resp.json())
      .then(data => this.setState({trips: data, date_start: moment(param_date + ' ' + param_min_time), date_end: moment(param_date + ' ' + param_max_time)}))
      .then(resp => this.setState({time: 0}));

    }

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
      // Ogni frame (30 o 60 al secondo) aumento il tempo di 1/5. time corrisponde ai minuti (vedi componente COUNTER)
      time: this.state.time + 1/5
    });
    this._animationFrame = window.requestAnimationFrame(this._animate.bind(this));
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
    const {viewport, trips, time, date_start, date_end} = this.state;

    return (
      <MapGL
        {...viewport}
        mapStyle="mapbox://styles/mapbox/dark-v9"
        onViewportChange={this._onViewportChange.bind(this)}
        mapboxApiAccessToken={MAPBOX_TOKEN}
      >
        <Counter
          time={time}
          date_start={date_start}
          date_end={date_end}
        ></Counter>

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
