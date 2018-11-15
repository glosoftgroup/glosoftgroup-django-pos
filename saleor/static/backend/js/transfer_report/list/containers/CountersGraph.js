import React from 'react';
import PropTypes from 'prop-types';
import Highcharts from 'highcharts';

/**
 * Redux
 */
// import { } from 'redux';
import { connect } from 'react-redux';

class CountersGraph extends React.Component {
  /**
   * This component renders highcharts pie charts
   * https://www.highcharts.com/demo/pie-basic
   * Props: pie: objects: struct: { data: [], title:'String', name: 'quantity'}
   */
  constructor(props) {
    super(props);
    this.state = {
      series: [],
      categories: [],
      title: ''
    };
  }
  componentDidMount() {
    this.drow(this.props);
  }

  componentWillReceiveProps(nextProps, nextState) {
    let series = nextProps.counterGraph.series;
    let categories = nextProps.counterGraph.categories;
    let title = nextProps.counterGraph.title;
    this.setState({series, categories, title}, () => {
      this.chart.destroy();
      this.drow(nextProps);
    });
  }

  shouldComponentUpdate() {
    return false;
  }

  componentWillUnmount() {
    this.chart.destroy();
  }

  drow(props) {
    this.chart = Highcharts.chart(this.container, {
      chart: {
        type: 'line'
      },
      title: {
        text: this.state.title
      },
      subtitle: {
        text: 'Shop report'
      },
      xAxis: {
        categories: this.state.categories
      },
      yAxis: {
        title: {
          text: 'Quantity'
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
      series: this.state.series
    });
  }

  render() {
    return <div className="chart" ref={ ref => (this.container = ref) } />;
  }
}
CountersGraph.propTypes = {
  counterGraph: PropTypes.array.isRequired
};
const mapStateToProps = (state) => ({
  counterGraph: state.counterGraph
});

export default connect(mapStateToProps)(CountersGraph);
