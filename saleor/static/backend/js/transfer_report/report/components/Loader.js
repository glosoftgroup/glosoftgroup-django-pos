import React, { Component } from 'react';

import '../css/loader.scss';

export class Loading extends Component {
  render() {
    return (
      <div className="pace-demo">
        <div className="theme_xbox">
            <div className="pace_progress" data-progress-text="60%" data-progress="60"></div>
            <div className="pace_activity"></div>
        </div>
      </div>
    );
  }
}

export default Loading;
