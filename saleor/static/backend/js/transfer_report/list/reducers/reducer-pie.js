import { SET_PIE } from '../actions';

const initialState = [];

export default (state = initialState, action) => {
  switch (action.type) {
    case SET_PIE:
      return action.payload;
    default:
      return state;
  }
};
