import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import moment from 'moment';
import { DateUtils } from "react-day-picker";
import DayPickerInput from 'react-day-picker/DayPickerInput';
import { formatDate, parseDate } from 'react-day-picker/moment';
// import 'react-day-picker/lib/style.css';
import { setDate, setDateRange } from '../actions/action-date';
import { fetchItems } from '../actions/action-items';

class FilterDateRange extends Component {
  /*
   * This component render datepicker input. Items filter based on selected date
   * Props: Listed in FilterDateRange.propTypes below
   *        All props are fetch from redux
   *  Usage: <FilterDateRange />
   * */
  constructor(props) {
    super(props);
    this.state = {
      search: '',
      from:undefined,
      to:undefined,
      month:undefined
    };
  }

  componentWillUnmount() {
    clearTimeout(this.timeout);
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

  fetchItems = () => {
    var from = this.dateFormatter(this.state.from);
    var to = this.dateFormatter(this.state.to);
    var payload = {};

    if (this.state.from !== undefined && this.state.to !== undefined) {
        payload = { date_from: from, date_to:to };
        this.props.setDateRange(payload);
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
  
  focusTo() {
    // Focus to `to` field. A timeout is required here because the overlays
    // already set timeouts to work well with input fields
    this.timeout = setTimeout(() => this.to.getInput().focus(), 0);
  }

  handleFromChange = (from) => {
    // Change the from date and focus the 
    this.setState({ from }, () => {
      this.fetchItems();
    });
  }

  handleToChange = (to) => {
    this.setState({ to }, () => {
      this.fetchItems();
    });
  }

  render() {
    const { from, to, month } = this.state;
    const modifiers = { start: from, end: to };

    return (
        <div className="form-grou search-form-group mr-15">
            <div className="input-group InputFromTo">
                    <DayPickerInput
                        value={from}
                        placeholder="From"
                        format="LL"
                        formatDate={formatDate}
                        parseDate={parseDate}
                        dayPickerProps={{
                            selectedDays: [from, { from, to }],
                            disabledDays: { after: to },
                            toMonth: to,
                            modifiers,
                            numberOfMonths: 2,
                            onDayClick: () => this.to.getInput().focus(),
                        }}
                        onDayChange={day => this.handleFromChange(day)}
                    />

                    <span className="input-group-addon"> to</span>

                    <DayPickerInput
                        ref={el => (this.to = el)}
                        value={to}
                        placeholder="To"
                        format="LL"
                        formatDate={formatDate}
                        parseDate={parseDate}
                        dayPickerProps={{
                            selectedDays: [from, { from, to }],
                            disabledDays: { before: from },
                            modifiers,
                            month: from,
                            fromMonth: from,
                            numberOfMonths: 2,
                        }}
                        onDayChange={day => this.handleToChange(day)}
                    />

            </div>

        </div>
    );
  }
}

FilterDateRange.propTypes = {
  setDate: PropTypes.func.isRequired,
  setDateRange: PropTypes.func.isRequired,
  search: PropTypes.array.isRequired,
  counter: PropTypes.object.isRequired,
  fetchItems: PropTypes.func.isRequired
};

function mapDispatchToProps(dispatch) {
  return bindActionCreators({
    fetchItems: fetchItems,
    setDate: setDate,
    setDateRange: setDateRange
  }, dispatch);
}

function mapStateToProps(state) {
  return { search: state.search, counter: state.counter };
}
export default connect(mapStateToProps, mapDispatchToProps)(FilterDateRange);
