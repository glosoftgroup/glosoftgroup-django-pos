import React, { Component } from 'react';
import PropTypes from 'prop-types';
import Container from '../containers';
import '../css/style.scss';
import '../css/tooltip.scss';
import '../../../common/css/print.scss';

export default class App extends Component {
  static propTypes = {
    prop: PropTypes
  }

  render() {
    return (
      <div className="row">
        <div className="col-md-12">
          <Container />
        </div>
      </div>
    );
  }
}
