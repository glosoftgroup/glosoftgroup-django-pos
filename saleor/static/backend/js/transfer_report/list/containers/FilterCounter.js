import React, { Component } from 'react';
import PropsTypes from 'prop-types';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import Select2 from 'react-select2-wrapper';
// import moment from 'moment';
/**
 * actions
 */
import { fetchItems, setCounter } from '../actions';
/**
 * Utils
 */
import api from '../api/Api';

export class FilterCounter extends Component {
  constructor(props) {
    super(props);
    this.state = {
      counters: [],
      counter: ''
    };
    this.getCounters();
  }
  getCounters = () => {
    api.retrieve('/counter/api/list')
    .then((response) => { return response.data.results; })
    .then((response) => {
      var counters = [];
      response.map((value, index) => {
        delete value.description;
        delete value.delete_url;
        delete value.update_url;
        counters.push(value);
      });
      this.setState({counters});
    })
    .catch((error) => { console.log(error); });
  }
  onSelectChange = (e) => {
    var name = e.target.name;
    var counter = e.target.value;

    this.setState({
      [name]: counter
    }, () => { this.fetchItems(); });
    this.props.setCounter({counter});
  }
  fetchItems = () => {
    var payload = {counter: this.state.counter};
    if (this.props.date) {
      if (this.props.date.from !== undefined && this.props.date.to !== undefined) {
        payload = { ...payload, date_from: [this.props.date.from], date_to: [this.props.date.from] };
      }
      if (this.props.date.date) {
        payload = { ...payload, date: [this.props.date.date] };
      }
    }
    if (this.props.mode) {
      payload = { ...payload, mode: this.props.mode.mode };
    }

    if (this.props.search) {
      var search = this.props.search.q;
      payload = { ...payload, q: search };
    }

    this.props.fetchItems(payload);
  }
  render() {
    return (
      <div>
        <label>Select Shop</label>
            <div className="form-group">
                <Select2
                    data={this.state.counters}
                    onChange={this.onSelectChange}
                    value={ this.state.counter }
                    name="counter"
                    options={{
                      minimumResultsForSearch: -1,
                      placeholder: 'Select Shop'
                    }}
                />
            </div>
      </div>
    );
  }
}
FilterCounter.propTypes = {
  mode: PropsTypes.object.isRequired,
  search: PropsTypes.object.isRequired,
  date: PropsTypes.object.isRequired,
  setCounter: PropsTypes.func.isRequired,
  fetchItems: PropsTypes.func.isRequired
};
function mapDispatchToProps(dispatch) {
  return bindActionCreators({
    fetchItems,
    setCounter
  }, dispatch);
}

function mapStateToProps(state) {
  return { search: state.search, date: state.date, mode: state.mode };
}
export default connect(mapStateToProps, mapDispatchToProps)(FilterCounter);

