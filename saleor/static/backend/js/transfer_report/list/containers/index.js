import React, { Component } from 'react';
import PropTypes from 'prop-types';
import FilterBlock from './FilterBlock';
import ItemList from './ItemList';
import GraphList from './GraphList';
import PaginationBlock from './PaginateBlock';

export default class App extends Component {
  static propTypes = {
    prop: PropTypes
  }

  render() {
    return (
      <div className="row">
        <div className="col-md-12">
          <FilterBlock />
          <div className="panel panel-body">
            <ItemList />
            <PaginationBlock />
          </div>
          <div className="panel panel-body">
            <GraphList />
          </div>
        </div>
      </div>
    );
  }
}
