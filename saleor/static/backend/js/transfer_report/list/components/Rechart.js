import React, { Component } from 'react';
import PropTypes from 'prop-types';

import {
    ComposedChart, Area, Line, Bar, ResponsiveContainer,
    XAxis, YAxis, CartesianGrid, Tooltip, Legend
} from 'recharts';

export class Rechart extends Component {
  /**
   * This component renders rechart Chart
   * Props:Title : String:
   *      data: array: format: data = [{
                                name: 'Asia',
                                data: [502, 635, 809, 947, 1402, 3634, 5268]
                              }, {
                                name: 'Africa',
                                data: [106, 107, 111, 133, 221, 767, 1766]
                              }, {
                                name: 'Europe',
                                data: [163, 203, 276, 408, 547, 729, 628]
                              }, {
                                name: 'America',
                                data: [18, 31, 54, 156, 339, 818, 1201]
                              }, {
                                name: 'Oceania',
                                data: [2, 2, 2, 6, 13, 30, 46]
                              }];
   */
  render() {
    return (
      <div>
        <h6 className="text-center">Transferred Quantity Summary Report</h6>
        <ResponsiveContainer height={400}>
          <ComposedChart width={600} height={400} data={this.props.data}
              margin={{top: 20, right: 80, bottom: 20, left: 20}}>
            <XAxis dataKey="name" label={{ value: 'Dates', position: 'insideBottomRight', offset: 0 }}/>
            <YAxis label={{ value: 'Quantity', angle: -90, position: 'insideLeft' }}/>
            <Tooltip/>
            <Legend/>
            <CartesianGrid stroke='#f5f5f5'/>
            <Area type='monotone' dataKey='transferred' fill='#8884d8' stroke='#8884d8'/>
            <Bar dataKey='sold' barSize={20} fill='#413ea0'/>
            <Line type='monotone' dataKey='deficit' stroke='#ff7300'/>
          </ComposedChart>
      </ResponsiveContainer>
      </div>
    );
  }
}

Rechart.propTypes = {
  data: PropTypes.array.isRequired
};

export default Rechart;
