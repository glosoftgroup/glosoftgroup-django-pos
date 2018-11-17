import React, { Component } from 'react';
import FilterSearch from './FilterSearch';
import FilterDate from './FilterDate';
import PrintThis from '../../../common/components/PrintThis';
import CsvExport from '../../../common/components/CsvExport';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';

class FilterBlock extends Component {
  /*
   * This component render search/datepicker components & transfer button.
   * Props: Listed in FilterBlock.propTypes below
   *        All props are fetch from redux
   *  Usage: <FilterBlock />
   * */
  constructor(props) {
    super(props);
    this.state = {
      title: 'Counter transfer list',
      label: 'Transfer Report',
      exportData: [],
      printCssPaths: []
    };
  }
  componentWillMount() {
    var baseURL = document.location.protocol + '//' + document.location.host;
    var printCssPaths = [];
    printCssPaths.push(baseURL + '/static/backend/css/bootstrap.css');
    printCssPaths.push(baseURL + '/static/backend/css/core.css');
    printCssPaths.push(baseURL + '/static/backend/css/print.css');
    this.setState({printCssPaths});
  }
  getData = () => {
    var items = [];
    var temp = this.props.items.results.slice();
    temp.map((obj, index) => {
      // delete unneccessary fields
      delete obj['name'];
      delete obj['user'];
      delete obj['created'];
      delete obj['description'];
      delete obj['update_items_url'];
      delete obj['update_url'];
      delete obj['delete_url'];
      delete obj['view_url'];
      delete obj['closing_items_view_url'];
      delete obj['closing_items_url'];
      delete obj['counter_transfer_items'];
      delete obj['text'];
      obj['counter'] = obj.counter.name;
      obj['closed'] = obj.all_item_closed;
      delete obj['all_item_closed'];
      items.push(obj);
    });
    return items;
  }
  render() {
    return (
      <div className="no-print breadcrumb-line breadcrumb-line-component content-group-lg">
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
            <li>
              <PrintThis printCssPaths={this.state.printCssPaths} title={this.state.title}/>
            </li>
            <li>
              <CsvExport getData={this.getData} title={this.state.title} label={this.state.label} />
            </li>
        </ul>
      </div>
    );
  }
}
FilterBlock.propTypes = {
  items: PropTypes.array.isRequired
};
function mapDispatchToProps(dispatch) {
  return bindActionCreators({}, dispatch);
}

function mapStateToProps(state) {
  return { items: state.items };
}
export default connect(mapStateToProps, mapDispatchToProps)(FilterBlock);
