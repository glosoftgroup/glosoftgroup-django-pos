import React, { Component } from 'react';
import PropTypes from 'prop-types';

/**
 * CONTAINERS
 */
import FilterBlock from '../containers/FilterBlock';
import ItemList from '../containers/ItemList';
import PaginationBlock from '../containers/PaginateBlock';

/**
 * STYLES
 */
import '../css/style.scss';
import '../css/tooltip.scss';

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
        </div>
      </div>
    );
  }
}
