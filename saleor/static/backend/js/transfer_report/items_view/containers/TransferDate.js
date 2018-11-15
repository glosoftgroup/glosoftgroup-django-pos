import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import moment from 'moment';
import DayPickerInput from 'react-day-picker/DayPickerInput';
import 'react-day-picker/lib/style.css';
import { setDate } from '../actions/action-transfer-date';

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
      search: '',
      date: moment().add(1, 'days').format('YYYY-MM-DD')
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
  }
  render() {
    return (
        <div className="form-grou search-form-group mr-15">
            <div className="has-feedback has-feedback-left">
                <DayPickerInput placeholder={this.state.date} dayPickerProps={{ disabledDays: {before: new Date()} }} onDayChange={day => this.handleChange(day)}/>
                <div className="form-control-feedback">
                    <i className="icon-calendar22 text-size-large text-muted">&nbsp;&nbsp;</i>
                </div>
            </div>
        </div>
    );
  }
}

FilterDate.propTypes = {
  setDate: PropTypes.func.isRequired,
  search: PropTypes.array.isRequired,
  fetchItems: PropTypes.func.isRequired
};

function mapDispatchToProps(dispatch) {
  return bindActionCreators({
    setDate: setDate
  }, dispatch);
}

function mapStateToProps(state) {
  return { search: state.search };
}
export default connect(mapStateToProps, mapDispatchToProps)(FilterDate);
