import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import moment from 'moment';
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
      search: '',
      modifiers: {
        highlighted: new Date(2010, 9, 9)
      }
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
    var payload = { date: value };
    this.props.setDate(payload);
  }
  render() {
    return (
        <div className="form-grou search-form-group mr-15">
            <div className="has-feedback has-feedback-left">
                <DayPickerInput
                  dayPickerProps={{
                    todayButton: 'Today'
                  }}
                  placeholder={moment().format('YYYY-MM-DD')}
                  onDayChange={day => this.handleChange(day)}
                />
                <div className="form-control-feedback">
                    <i className="icon-calendar22 text-size-large text-muted"></i>
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
    fetchItems: fetchItems,
    setDate: setDate
  }, dispatch);
}

function mapStateToProps(state) {
  return { search: state.search };
}
export default connect(mapStateToProps, mapDispatchToProps)(FilterDate);
