/*
 * All reducers get two parameters passed in, state and action that occurred
 *       > state isn't entire apps state, only the part of state that this reducer is responsible for
 * */

// "state = null" is set so that we don't throw an error when app first boots up
import moment from 'moment';
import { SET_DATE } from '../actions/action-transfer-date.js';

var initialState = {date: moment().add(1, 'days').format('YYYY-MM-DD')};

export default function (state = initialState, action) {
  switch (action.type) {
    case SET_DATE:
      return action.payload;
  }
  return state;
};
