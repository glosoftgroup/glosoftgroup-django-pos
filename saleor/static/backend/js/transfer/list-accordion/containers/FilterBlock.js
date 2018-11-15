import React, { Component } from 'react';
import FilterSearch from './FilterSearch';
import FilterDate from './FilterDate';

class FilterBlock extends Component {
  /*
   * This component render search/datepicker components & transfer button.
   * Props: Listed in FilterBlock.propTypes below
   *        All props are fetch from redux
   *  Usage: <FilterBlock />
   * */
  render() {
    return (
      <div className="breadcrumb-line breadcrumb-line-component content-group-lg">
        <ul className="breadcrumb">
            <li>
              <a className="text-white btn btn-primary btn-sm btn-raised legitRipple" href="/counter/transfer/add/">
              <i className="icon-add position-left"></i>
              Transfer
              </a>
            </li>
        </ul>
        <ul className="breadcrumb-elements">
            <li><a href="javascript:;" className="text-bold"> Search:</a></li>
            <li>
              <FilterSearch />
            </li>
            <li><a href="javascript:;" className="text-bold"> Date:</a></li>
            <li>
              <FilterDate />
            </li>
        </ul>
      </div>
    );
  }
}

export default FilterBlock;
