import React, { Component } from 'react';
import PropTypes from 'prop-types';
import Select2 from 'react-select2-wrapper';

/**
 * Containers
 */
// import FilterSearch from './FilterSearch';
import FilterDate from './FilterDate';
import FilterMonth from './FilterMonth';
import FilterDateRange from './FilterDateRange';
import FilterMonthRange from './FilterMonthRange';
import FilterCounter from './FilterCounter';
/**
 * Utilities
 */
import PrintThis from '../../../common/components/PrintThis';
import CsvExport from '../../../common/components/CsvExport';

/**
 * Redux
 */
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

/**
 * Actions
 */
import { toggleGraph } from '../actions/action-toggle-graph';

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
      title: 'Shop Transfer Report',
      label: 'Shop Transfer',
      exportData: [],
      printCssPaths: [],
      defaultFilterChoice: 1,
      filterChoices: [
        {'text': 'Date', 'id': '1'},
        {'text': 'Month', 'id': '2'},
        {'text': 'Year', 'id': '3'}
      ],
      defaultFilter: 1,
      filters: [
        {'text': 'Filter', 'id': '1'},
        {'text': 'Range Filter', 'id': '3'}
      ],
      rangeStatus: false,
      compareStatus: false,
      checked: false
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
  toggleCheckBox = () => {
    var checked = (this.state.checked === '') ? 'checked' : '';
    this.setState({checked});
    let open = !this.props.openGraph.open;
    this.props.toggleGraph({open});
  }
  getData = () => {
    var items = [];
    var temp = this.props.items.results.slice();
    temp.map((obj, index) => {
      // delete unneccessary fields
      delete obj['view_url'];
      delete obj['created'];
      delete obj['trashed'];
      delete obj['trashed'];
      delete obj.name;
      delete obj.user;
      delete obj.description;
      delete obj.update_url;
      delete obj.text;
      delete obj.counter_transfer_items;
      delete obj.all_item_closed;
      delete obj.update_items_url;
      obj.counter = obj.counter.name;
      items.push(obj);
    });
    return items;
  }
  onSelectChange = (e) => {
    var name = e.target.name, value = e.target.value,
        newRangeStatus, newCompareStatus;

    newRangeStatus = value == 1 ? false : true;
    newCompareStatus = value == 1 ? false : true;

    this.setState({
      [name]: value,
      rangeStatus: newRangeStatus,
      compareStatus: newCompareStatus
    });
  }
  onSelectPeriod = (e) => {
    var name = e.target.name;
    var value = e.target.value;
    var newRangeStatus;
    var newCompareStatus;

    newRangeStatus = (this.state.defaultFilter === 1) ? false : true;

    this.setState({
      [name]: value,
      rangeStatus: newRangeStatus
    });
  }

  renderDateComponent(){
    var button;
    var periodChoice = this.state.defaultFilterChoice;
        
    button = this.state.rangeStatus ?
            (
              periodChoice == 2 || periodChoice == 3 ? 
              <FilterMonthRange mode={ periodChoice == 2 ? "month" : "year"} /> : 
              <FilterDateRange />
            ) :
            (periodChoice == 2 || periodChoice == 3 ? 
              <FilterMonth mode={ periodChoice == 2 ? "month" : "year"} /> : 
              <FilterDate />
            );

    return button;
  }

  render() {
    return (
        <div>
            <div className="panel no-print">
                <div className="panel-body">
                    <div className="col-md-2">
                      <FilterCounter />
                    </div>
                    <div className="col-md-1">
                    <label>Action</label>
                      <div className="form-group">
                        <Select2
                          data={this.state.filters}
                          onChange={this.onSelectChange}
                          value={ this.state.defaultFilter }
                          name="defaultFilter"
                          options={{
                            minimumResultsForSearch: -1,
                            placeholder: 'Select Action'
                          }}
                        />
                      </div>
                    </div>
                    <div className="col-md-1">
                        <label>Period</label>
                        <div className="form-group">
                          <Select2
                              data={this.state.filterChoices}
                              onChange={this.onSelectPeriod}
                              value={ this.state.defaultFilterChoice }
                              name="defaultFilterChoice"
                              options={{
                                minimumResultsForSearch: -1,
                                placeholder: 'Select Filter'
                              }}
                          />
                        </div>
                    </div>
                    <div className="col-md-4">
                        <label>Filter</label>
                        <div className="form-group">
                        {this.renderDateComponent()}
                        </div>
                    </div>
                    <div className="col-md-2">
                    <label className="visibility-hidden">&nbsp;</label>
                    <br/>
                    <div className="btn-group">
												<a href="#" className="btn btn-sm bg-teal dropdown-toggle" data-toggle="dropdown" aria-expanded="false">
                          Export
                          <span className="caret"></span>
                        </a>

												<ul className="dropdown-menu dropdown-menu-right">
                          <li>
                            <a href="#">
                             <PrintThis getData={this.getData} title={this.state.title} label={this.state.label} />
                            </a>
                          </li>
                          <li>
                            <a href="#">
                             <CsvExport getData={this.getData} title={this.state.title} label={this.state.label} />
                            </a>
                          </li>
												</ul>
											</div>
                    </div>
                    <div className="col-md-2">
                      <label>Show Graph</label>
                      <div className="form-control">
                        <div onClick={this.toggleCheckBox} className="checker">
                          <span className={this.state.checked}>
                            <input className="styleds" type="checkbox" />
                          </span>
                        </div>
                      </div>
                    </div>
                </div>
            </div>

      </div>
    );
  }
}
FilterBlock.propTypes = {
  items: PropTypes.array.isRequired,
  openGraph: PropTypes.object.isRequired,
  toggleGraph: PropTypes.func.isRequired
};
function mapDispatchToProps(dispatch) {
  return bindActionCreators({ toggleGraph }, dispatch);
}

function mapStateToProps(state) {
  return { items: state.items, openGraph: state.openGraph };
}
export default connect(mapStateToProps, mapDispatchToProps)(FilterBlock);
