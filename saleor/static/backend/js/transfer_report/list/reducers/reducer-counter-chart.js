import { SET_COUNTER_CHART } from '../actions';

const initialState = [];

export default (state = initialState, action) => {
  switch (action.type) {
    case SET_COUNTER_CHART:
      return action.payload;
    default:
      return state;
  }
};
