import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { setSearch } from '../actions/action-search';
import { fetchItems } from '../actions/action-items';

class FilterSearch extends Component {
  /*
   * This component render search input. Items filter based on searched query
   * Props: Listed in FilterSearch.propTypes below
   *        All props are fetch from redux
   *  Usage: <FilterSearch />
   * */
  constructor(props) {
    super(props);
    this.state = {
      search: ''
    };
  }
  handleChange = (e) => {
    var value = e.target.value;
    this.setState({
      [e.target.name]: value
    });
    var payload = { q: value };
    this.props.setSearch(payload);
    if (this.props.date) {
      var date = this.props.date.date;
      payload = { ...payload, date: date };
    }
    this.props.fetchItems(payload);
  }
  render() {
    return (
        <div className="form-grou search-form-group mr-15">
            <div className="has-feedback has-feedback-right">
                <input value={this.state.search} name="search"
                  onChange={this.handleChange} className="form-control"
                  placeholder="Product name or sku" type="search" />
                <div className="form-control-feedback">
                    <i className="icon-search4 text-size-large text-muted"></i>
                </div>
            </div>
        </div>
    );
  }
}

FilterSearch.propTypes = {
  setSearch: PropTypes.func.isRequired,
  fetchItems: PropTypes.func.isRequired,
  date: PropTypes.array.isRequired
};

function mapDispatchToProps(dispatch) {
  return bindActionCreators({
    fetchItems: fetchItems,
    setSearch: setSearch
  }, dispatch);
}

function mapStateToProps(state) {
  return { search: state.search, date: state.date };
}
export default connect(mapStateToProps, mapDispatchToProps)(FilterSearch);
