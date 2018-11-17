import React, { Component } from 'react';
import * as Highcharts from 'highcharts';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
// Alternatively, this is how to load Highstock. Highmaps is similar.
// import Highcharts from 'highcharts/highstock';
// Load the exporting module.
// import * as Exporting from 'highcharts/modules/exporting';
// Initialize exporting module.
// Exporting(Highcharts);

export class HCharts extends Component {
  constructor(props) {
    super(props);
    this.state = {};
  }
  componentDidMount() {
    // Generate the chart
    Highcharts.chart('chart-container', this.props.data);
  }
  render() {
    return (
      <div id="chart-container" className="chart-container">
      </div>
    );
  }
}
HCharts.propTypes = {
  charts: PropTypes.object.isRequired,
  data: PropTypes.object.isRequired
};

const mapStateToProps = (state) => {
  return {
    charts: state.charts,
    data: state.charts
  };
};

export default connect(mapStateToProps, undefined)(HCharts);
