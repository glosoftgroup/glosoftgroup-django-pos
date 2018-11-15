import React, { Component } from 'react';
// import Rechart from '../components/HCharts';
import Rechart from '../components/Rechart';
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
import Api from '../api/Api';

export class GraphList extends Component {
  constructor(props) {
    super(props);
    this.state = {
      data: [],
      options: {
        chart: {
          type: 'line'
        },
        title: {
          text: 'Monthly Average Temperature'
        },
        subtitle: {
          text: 'Source: WorldClimate.com'
        },
        xAxis: {
          categories: [] // ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        },
        yAxis: {
          title: {
            text: 'Temperature (°C)'
          }
        },
        plotOptions: {
          line: {
            dataLabels: {
              enabled: true
            },
            enableMouseTracking: false
          }
        },
        series: []
      }
    };
  }
  componentWillMount() {
    Api.retrieve('/counter/transfer/report/api/graph/recharts/')
    // Api.retrieve('/counter/transfer/report/api/graph/')
    .then(response => { return response.data; })
    .then(data => {
      // console.error(data);
      this.props.setChartOptions(data);
      var options = this.state.options;
      options = {
        ...options,
        series: data.series,
        categories: data.categories
      };
      this.setState({data, options});
    })
    .catch(error => console.error(error));
  }
  render() {
    return (
      <div>
        <Rechart data={this.state.data}/>
      </div>
    );
  }
}
const mapDispatchToProps = (dispatch) => {
  return bindActionCreators({
    setChartOptions
  }, dispatch);
};

GraphList.propTypes = {
  setChartOptions: PropTypes.func.isRequired
};
export default connect(undefined, mapDispatchToProps)(GraphList);
