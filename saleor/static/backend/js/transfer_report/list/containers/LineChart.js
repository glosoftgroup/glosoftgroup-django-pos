import React, { Component } from 'react';
import LineHighChart from '../components/LineCharts';
/**
 * Utilities
 */
import Api from '../api/Api';

export class LineChart extends Component {
  constructor(props) {
    super(props);
    this.state = {
      options: { series: [], categories: [] }
    };
  }
  componentWillMount () {
    // Api.retrieve('/counter/transfer/report/api/graph/recharts/')
    Api.retrieve('/counter/transfer/report/api/graph/')
    .then(response => { return response.data; })
    .then(data => {
      // console.error(data);
    //   this.props.setChartOptions(data);
      var options = {series: data.series, categories: data.categories};
      this.setState({options});
    })
    .catch(error => console.error(error));
  }
  render() {
    const title = 'Historic and Estimated Worldwide Population Distribution by Region';
    return (
      <div>
        <LineHighChart
          title={title}
          data={this.state.options.series}
          categories={this.state.options.categories}
        />
      </div>
    );
  }
}

export default LineChart;
