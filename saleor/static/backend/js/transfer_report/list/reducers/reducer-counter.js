import { SET_COUNTER } from '../actions';

const initialState = {
  counter: ''
};

export default (state = initialState, action) => {
  switch (action.type) {
    case SET_COUNTER:
      return action.payload;
    default:
      return state;
  }
};
