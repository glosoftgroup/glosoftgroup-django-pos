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
        plotBackgroundColor: null,
        plotBorderWidth: null,
        plotShadow: false,
        type: 'pie'
      },
      title: {
        text: 'Browser market shares in January, 2018'
      },
      tooltip: {
        pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
      },
      plotOptions: {
        pie: {
          allowPointSelect: true,
          cursor: 'pointer',
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
        name: 'Share',
        data: this.props.data
      }]
    });
  }

  render() {
    return <div className="chart" ref={ ref => this.container = ref } />;
  }
}

export default PercentageArea;
