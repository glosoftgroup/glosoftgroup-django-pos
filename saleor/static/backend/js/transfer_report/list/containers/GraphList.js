import React, { Component } from 'react';
// import Rechart from '../components/HCharts';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';

/**
 * Actions
 */
import { setChartOptions } from '../actions/action-charts';

/**
 * Utils
 */
// import Api from '../api/Api';

/**
 * Components
 */
// import LineChart from './LineChart';
import PieChart from './PieChart';
import Rechart from '../components/Rechart';
import CounterCharts from '../components/CounterCharts';
// import CounterGraph from './CountersGraph';

export class GraphList extends Component {
  constructor(props) {
    super(props);
    this.state = {
      data: []
    };
  }
  render() {
    return (
      <div className="row">
        <div className="col-md-6">
          <Rechart data={this.props.charts}/>
        </div>
        <div className="col-md-6">
          <PieChart />
        </div>
        <div className="col-md-6">
          <CounterCharts data={this.props.counterGraph}/>
        </div>
      </div>
    );
  }
}
GraphList.propTypes = {
  setChartOptions: PropTypes.func.isRequired,
  charts: PropTypes.array.isRequired.length,
  counterGraph: PropTypes.array.isRequired
};
const mapDispatchToProps = (dispatch) => {
  return bindActionCreators({
    setChartOptions
  }, dispatch);
};
const mapStateToProps = (state) => ({
  charts: state.charts,
  counterGraph: state.counterGraph
});

export default connect(mapStateToProps, mapDispatchToProps)(GraphList);
