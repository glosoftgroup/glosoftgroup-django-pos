import React from 'react';
import Highcharts from 'highcharts';

class PercentageArea extends React.Component {
  componentDidMount() {
    this.drow(this.props);
  }

  componentWillReceiveProps(nextProps, nextState) {
    this.chart.destroy();
    this.drow(nextProps);
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
        type: 'area'
      },
      title: {
        text: props.title
      },
      xAxis: {
        categories: props.categories,
        tickmarkPlacement: 'on',
        title: {
          enabled: false
        }
      },
      yAxis: {
        title: {
          text: 'Percent'
        }
      },
      tooltip: {
        pointFormat: '<span style="color:{series.color}">{series.name}</span>: <b>{point.percentage:.1f}%</b> ({point.y:,.0f} millions)<br/>',
        split: true
      },
      plotOptions: {
        area: {
          stacking: 'percent',
          lineColor: '#ffffff',
          lineWidth: 1,
          marker: {
            lineWidth: 1,
            lineColor: '#ffffff'
          }
        }
      },
      series: props.data
    });
  }

  render() {
    return <div className="chart" ref={ref => (this.container = ref)} />;
  }
}

export default PercentageArea;
