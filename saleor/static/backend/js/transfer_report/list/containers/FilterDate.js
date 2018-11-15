import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import DayPickerInput from 'react-day-picker/DayPickerInput';
import 'react-day-picker/lib/style.css';
import { setDate } from '../actions/action-date';
import { fetchItems } from '../actions/action-items';

class FilterDate extends Component {
  /*
   * This component render datepicker input. Items filter based on selected date
   * Props: Listed in FilterDate.propTypes below
   *        All props are fetch from redux
   *  Usage: <FilterDate />
   * */
  constructor(props) {
    super(props);
    this.state = {
      search: ''
    };
  }
  dayMonthFormatter = (num) => {
    return (num < 10) ? '0' + num : num;
  }
  dateFormatter = (date) => {
    date = new Date(date);
    var day = date.getDate();
    var monthIndex = date.getMonth() + 1;
    var year = date.getFullYear();

    return year + '-' + this.dayMonthFormatter(monthIndex) + '-' + this.dayMonthFormatter(day);
  }
  handleChange = (e) => {
    var value = this.dateFormatter(e);
    var payload = {};
    if (e) {
      payload = { date: value };
      this.props.setDate(payload);
    }
    if (this.props.search) {
      var search = this.props.search.q;
      payload = { ...payload, q: search };
    }

    if (this.props.counter) {
      var counter = this.props.counter.counter;
      payload = { ...payload, counter };
    }

    this.props.fetchItems(payload);
  }
  render() {
    return (
        <div className="form-grou search-form-group mr-15">
            <div className="has-feedback has-feedback-left">
                <DayPickerInput onDayChange={day => this.handleChange(day)}/>
            </div>
        </div>
    );
  }
}

FilterDate.propTypes = {
  setDate: PropTypes.func.isRequired,
  search: PropTypes.array.isRequired,
  counter: PropTypes.object.isRequired,
  fetchItems: PropTypes.func.isRequired
};

function mapDispatchToProps(dispatch) {
  return bindActionCreators({
    fetchItems: fetchItems,
    setDate: setDate
  }, dispatch);
}

function mapStateToProps(state) {
  return { search: state.search, counter: state.counter };
}
export default connect(mapStateToProps, mapDispatchToProps)(FilterDate);
