import { SET_CHART_OPTIONS } from '../actions/action-charts';

const initialState = [];

export default (state = initialState, action) => {
  switch (action.type) {
    case SET_CHART_OPTIONS:
      return action.payload;
    default:
      return state;
  }
};
