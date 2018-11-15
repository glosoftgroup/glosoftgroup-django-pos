import React, { Component } from 'react';

import '../css/loader.scss';

export class Loading extends Component {
  render() {
    return (
      <div className='loader'>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
      </div>
    );
  }
}

export default Loading;
