import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import DayPickerInput from 'react-day-picker/DayPickerInput';
import 'react-day-picker/lib/style.css';
import { setDate } from '../actions/action-date';
import { setMode } from '../actions/action-mode';
import { fetchItems } from '../actions/action-items';
import moment from 'moment';
import Datetime from 'react-datetime';

class FilterMonth extends Component {
  /*
   * This component render datepicker input. Items filter based on selected date
   * Props: Listed in FilterDate.propTypes below
   *        All props are fetch from redux
   *  Usage: <FilterMonth />
   * */
  constructor(props) {
    super(props);
    this.state = {
      search: '',
      date:undefined
    };
  }

  fetchItems = () => {
    var payload = {};

    if (this.state.date !== undefined) {
      var value = moment(this.state.date).format("YYYY-MM-DD");
      payload = { date: value, mode: this.props.mode };
      this.props.setDate(payload);
    }

    if(this.props.mode){
      payload = { ...payload, mode:this.props.mode };
      this.props.setMode(payload);
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

  focousOut = (value) =>{
    if(!moment(value).isValid()) {
     this.setState({selectedValue: ''}); 
    }
  }

  handleChange = (date) => {
    this.setState({ date }, () => {
        this.fetchItems();
    });
  }

  render() {
    const { date } = this.state;
    const { mode } = this.props;
    let format = (mode == "month") ? "YYYY-MM" : "YYYY"
    return (
        <div className="col-md-7 form-grou search-form-group mr-15">
            <Datetime
                inputProps={{ placeholder: format }}
                dateFormat={format}
                timeFormat={false}
                value={date}
                onChange={this.handleChange}
                onBlur={this.focousOut}
                locale='en-US'
                closeOnSelect
            />
        </div>
    );
  }
}

FilterMonth.propTypes = {
  setMode: PropTypes.func.isRequired,
  setDate: PropTypes.func.isRequired,
  search: PropTypes.array.isRequired,
  counter: PropTypes.object.isRequired,
  fetchItems: PropTypes.func.isRequired
};

function mapDispatchToProps(dispatch) {
  return bindActionCreators({
    fetchItems: fetchItems,
    setDate: setDate,
    setMode: setMode
  }, dispatch);
}

function mapStateToProps(state) {
  return { search: state.search, counter: state.counter };
}
export default connect(mapStateToProps, mapDispatchToProps)(FilterMonth);
