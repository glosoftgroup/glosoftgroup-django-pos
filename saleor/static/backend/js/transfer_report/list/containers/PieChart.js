import React from 'react';
import PropTypes from 'prop-types';
import Highcharts from 'highcharts';

/**
 * Redux
 */
// import { } from 'redux';
import { connect } from 'react-redux';

class PieChart extends React.Component {
  /**
   * This component renders highcharts pie charts
   * https://www.highcharts.com/demo/pie-basic
   * Props: pie: objects: struct: { data: [], title:'String', name: 'quantity'}
   */
  constructor(props) {
    super(props);
    this.state = {
      data: [],
      name: '',
      title: ''
    };
  }
  componentDidMount() {
    this.drow(this.props);
  }

  componentWillReceiveProps(nextProps, nextState) {
    let data = nextProps.pie.data;
    let name = nextProps.pie.name;
    let title = nextProps.pie.title;
    this.setState({data, name, title}, () => {
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
        plotBackgroundColor: null,
        plotBorderWidth: null,
        plotShadow: false,
        type: 'pie',
        options3d: {
          enabled: true,
          alpha: 45,
          beta: 0
        },
        polar: false
      },
      title: {
        text: this.state.title
      },
      tooltip: {
        pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
      },
      plotOptions: {
        pie: {
          allowPointSelect: true,
          depth: 35,
          cursor: 'pointer',
          innerSize: '60%',
          showInLegend: true,
          dataLabels: {
            enabled: true,
            format: '<b>{point.name}</b>: {point.percentage:.1f} %',
            style: {
              color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
            },
            connectorColor: 'silver'
          }
        }
      },
      series: [{
        name: this.state.name,
        data: this.state.data
      }]
    });
  }

  render() {
    return <div className="chart" ref={ ref => (this.container = ref) } />;
  }
}
PieChart.propTypes = {
  pie: PropTypes.array.isRequired
};
const mapStateToProps = (state) => ({
  pie: state.pie
});

export default connect(mapStateToProps)(PieChart);
