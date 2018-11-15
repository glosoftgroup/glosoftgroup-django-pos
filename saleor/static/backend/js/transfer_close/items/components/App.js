import React, { Component } from 'react';
import PropTypes from 'prop-types';
import FilterBlock from '../containers/FilterBlock';
import ItemList from '../containers/ItemList';
import PaginationBlock from '../containers/PaginateBlock';
import '../css/style.scss';
import '../css/tooltip.scss';
import '../../../common/css/print.scss';

export default class App extends Component {
  static propTypes = {
    prop: PropTypes
  }

  render() {
    return (
      <div className="row">
        <div className="col-md-12">
          <FilterBlock />
          {/* back button */}
          <div className="clearfix"></div>
          <div className="col-md-12 row mb-10" >
            <a href="javascript:;" onClick={() => { window.location.href = document.referrer; }} className="btn btn-primary pull-left back-btn legitRipple">
              <i className="icon-arrow-left13 position-left"></i>
              Back To Transfer List
            </a>
          </div>
          <div className="clearfix"></div>
          <div className="panel panel-body">
            <ItemList />
            <PaginationBlock />
          </div>
        </div>
      </div>
    );
  }
}
